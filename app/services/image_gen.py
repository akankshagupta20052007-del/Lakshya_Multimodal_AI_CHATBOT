# app/services/image_gen.py
"""
Text-to-Image Generation Service for Nexus Multimodal AI Studio.
Adheres strictly to the prompt without ever falling back to static stock photos.
Features:
- Gemini-powered prompt intelligence: fixes typos (e.g. 'imag eo fmodi ji' -> 'Narendra Modi'),
  translates Hindi/Hinglish/slang, and enriches prompts into high-detail visual descriptions.
- Cooldown intelligence: detects 45s free-tier rate limits and provides exact countdown timer.
- Banner suppression: detects and blocks yellow rate-limit error images.
- Local disk storage: saves genuine JPEG artwork to ./data/generated/images/.
"""
import io
import os
import re
import uuid
import time
import random
import urllib.parse
import logging
import requests
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
from ..config import settings

logger = logging.getLogger("nexus.image_gen")


class ImageGenService:
    def __init__(self):
        self.output_dir = settings.resolved_images_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.last_generation_time = 0
        self.cooldown_period = 45  # Free tier limits to 1 image every 45s per IP

    @staticmethod
    def is_image_request(prompt: str) -> bool:
        """
        Determines if the prompt is an image generation request.
        Handles common abbreviations, typos, and multilingual keywords.
        """
        p = prompt.lower().strip()
        triggers = [
            "generate an image", "generate image", "create an image", "create image",
            "draw an image", "draw a picture", "draw image", "make an image",
            "generate a picture", "create a picture", "make a picture",
            "render an image", "paint a picture", "generate photo", "create photo",
            "design an image", "illustration of", "generate pic", "create pic",
            "generate img", "photo of", "picture of", "image of",
            "photo banao", "image banao", "picture banao", "tasveer"
        ]
        strong_verbs = ["generate", "create", "draw", "make", "paint", "render", "show", "banao", "dikhao"]
        has_verb = any(v in p for v in strong_verbs)
        has_noun = any(
            n in p for n in [
                "image", "imag", "img", "picture", "pic", "photo", "fotu",
                "drawing", "painting", "illustration", "art", "portrait",
                "sketch", "tasveer", "chitra"
            ]
        )
        return (has_verb and has_noun) or any(t in p for t in triggers)

    @staticmethod
    def sanitize_prompt_regex(prompt: str) -> str:
        """Regex-based fallback to strip command phrases."""
        prefixes = [
            "generate an image of", "generate image of", "generate an image", "generate image",
            "generate imag of", "generate imag eo f", "generate imag of", "generate imag",
            "create an image of", "create image of", "create an image", "create image",
            "draw a picture of", "draw an image of", "draw a picture", "draw image",
            "make an image of", "make a picture of", "paint a picture of",
            "render an image of", "please generate an image of", "generate photo of",
            "generate pic of", "photo of", "picture of", "image of"
        ]
        p_clean = prompt.strip()
        p_lower = p_clean.lower()
        for prefix in prefixes:
            if p_lower.startswith(prefix):
                p_clean = p_clean[len(prefix):].strip(" :,-")
                break
        return p_clean if p_clean else prompt

    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """Alias for backward compatibility."""
        return ImageGenService.sanitize_prompt_regex(prompt)

    def enhance_image_prompt(self, raw_prompt: str) -> str:
        """
        Uses Google Gemini to fix typos (e.g. 'imag eo fmodi ji' -> 'Narendra Modi'),
        interpret Hindi/Hinglish/slang, and transform the user request into an
        optimized, photorealistic visual prompt for text-to-image synthesis.
        """
        api_key = settings.effective_api_key
        if not api_key:
            return self.sanitize_prompt_regex(raw_prompt)

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            instruction = (
                "You are an expert AI prompt engineer for text-to-image synthesis. "
                "Task: Convert the user's request into a high quality, photorealistic, descriptive visual prompt in English (under 30 words). "
                "CRITICAL: Fix any typos (e.g. 'imag eo fmodi ji' -> 'Narendra Modi, Indian Prime Minister'), slang, or non-English phrases. "
                "Focus on subject, appearance, lighting, and detail. "
                "Output ONLY the final visual prompt description without quotes, prefixes, or commentary."
            )
            resp = client.models.generate_content(
                model=settings.effective_model,
                contents=f"{instruction}\n\nUser Request: {raw_prompt}"
            )
            if resp and resp.text:
                enhanced = resp.text.strip().strip('"\'')
                # Avoid overly short or error text
                if len(enhanced) > 5 and not enhanced.startswith("Error"):
                    logger.info(f"Gemini enhanced prompt: '{raw_prompt}' -> '{enhanced}'")
                    return enhanced
        except Exception as e:
            logger.warning(f"Gemini prompt enhancement fallback: {e}")

        return self.sanitize_prompt_regex(raw_prompt)

    @staticmethod
    def is_rate_limit_banner(img_bytes: bytes) -> bool:
        """
        Detects if an image returned is the yellow 'Free limit reached' banner.
        Checks both raw byte indicators and dominant yellow background color.
        """
        lower = img_bytes.lower()
        if (
            b"free limit" in lower
            or b"every 45 seconds" in lower
            or b"classic api" in lower
            or b"payment required" in lower
        ):
            return True

        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            w, h = img.size
            step = max(1, min(w, h) // 40)
            pixels = [
                img.getpixel((x, y))
                for x in range(0, w, step)
                for y in range(0, h, step)
            ]
            if pixels:
                # Yellow rate limit banner background color: (253, 215, 108)
                yellow_pixels = sum(
                    1 for (r, g, b) in pixels if r > 215 and g > 175 and b < 135
                )
                ratio = yellow_pixels / len(pixels)
                if ratio > 0.55:
                    logger.warning(f"Detected rate limit banner by color ratio: {ratio:.2f}")
                    return True
        except Exception as e:
            logger.debug(f"Image analysis error: {e}")

        return False

    def generate_image(self, prompt: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Synthesizes an image strictly adhering to the user's prompt.
        Uses Gemini prompt enhancement to fix typos and enrich descriptions.
        Handles 45s cooldown with helpful countdown timing.
        Saves verified artwork locally to ./data/generated/images/{unique_id}.jpg.

        Returns:
            Tuple of (local_file_path, relative_web_url, status_message)
        """
        # 1. Check local cooldown tracker (if no custom API key provided)
        pollen_key = settings.POLLINATIONS_API_KEY
        if not pollen_key and self.last_generation_time > 0:
            elapsed = time.time() - self.last_generation_time
            if elapsed < self.cooldown_period:
                wait_remaining = int(self.cooldown_period - elapsed) + 1
                msg = (
                    f"⏳ **Free Tier Image Cooldown Active**\n\n"
                    f"Free image generation allows 1 image every 45 seconds per IP.\n\n"
                    f"Please wait **{wait_remaining} seconds** before creating your next image."
                )
                logger.info(f"Local cooldown active: {wait_remaining}s remaining.")
                return None, None, msg

        # 2. Enhance & correct prompt via Gemini
        enhanced_desc = self.enhance_image_prompt(prompt)
        encoded_prompt = urllib.parse.quote(enhanced_desc)
        seed = random.randint(1000, 999999)

        # 3. Build candidate endpoints
        key_param = f"&key={pollen_key}" if pollen_key else ""
        candidate_urls = [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&nologo=true&seed={seed}{key_param}",
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&nologo=true&private=true&seed={seed + 1}{key_param}",
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&seed={seed + 2}{key_param}",
        ]

        logger.info(f"Initiating image synthesis for: '{enhanced_desc[:60]}...'")

        for url in candidate_urls:
            try:
                response = requests.get(url, timeout=35)

                # Check for rate limit or server busy status (402, 429, 503)
                if response.status_code in [402, 429, 503] or "FREE_LIMIT" in response.text or "SERVICE_UNAVAILABLE" in response.text:
                    # Try to extract exact retry duration from response body
                    retry_seconds = 40
                    match = re.search(r'retry after (\d+)s', response.text, re.IGNORECASE)
                    if match:
                        retry_seconds = match.group(1)
                    logger.warning(f"Endpoint rate limit: status={response.status_code}, retry_after={retry_seconds}s")
                    msg = (
                        f"⏳ **Image Generation Busy (Free Tier Cooldown)**\n\n"
                        f"Free generation allows 1 image every 45 seconds per IP.\n\n"
                        f"Please retry in **{retry_seconds} seconds**."
                    )
                    return None, None, msg

                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    content_len = len(response.content)

                    # Check if response is JSON error masquerading under 200
                    if "json" in content_type and b"FREE_LIMIT" in response.content:
                        continue

                    # Check for rate limit banner graphic
                    if self.is_rate_limit_banner(response.content):
                        logger.warning("Rate limit yellow banner image intercepted and suppressed.")
                        continue

                    # Verify it is a valid image with reasonable size (> 5KB)
                    if "image" in content_type or content_len > 5000:
                        try:
                            test_img = Image.open(io.BytesIO(response.content))
                            test_img.verify()
                        except Exception as e:
                            logger.warning(f"Corrupt or unreadable image received: {e}")
                            continue

                        # Save verified image locally
                        filename = f"img_{uuid.uuid4().hex[:12]}.jpg"
                        file_path = self.output_dir / filename
                        with open(file_path, "wb") as f:
                            f.write(response.content)

                        # Update last generation timestamp
                        self.last_generation_time = time.time()

                        relative_url = f"/static/images/{filename}"
                        success_msg = f"🎨 **Generated artwork for:** *\"{enhanced_desc}\"*"
                        logger.info(f"Image successfully generated and saved to {file_path}")
                        return str(file_path), relative_url, success_msg

            except requests.exceptions.Timeout:
                logger.warning(f"Image synthesis timed out for: {url}")
                continue
            except Exception as e:
                logger.warning(f"Image candidate error: {e}")
                continue

        # If all candidates fail
        msg = "⚠️ Image generation is temporarily busy, please retry in a moment."
        logger.info("Image generation unavailable, returned notice to user.")
        return None, None, msg


# Singleton instance
image_gen_service = ImageGenService()
