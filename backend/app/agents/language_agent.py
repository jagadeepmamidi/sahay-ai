"""
Language Agent
==============

Handles multilingual support including language detection, translation,
and transliteration for Indian languages.

Uses deep-translator for free translation (Google Translate backend).

Author: Jagadeep Mamidi
"""

import logging
from functools import lru_cache
from typing import Dict, Optional

from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, detect

from app.core.config import SUPPORTED_LANGUAGES, get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Make language detection deterministic
DetectorFactory.seed = 0


# Language code mapping for different services
LANGUAGE_CODES = {
    "en": "en",
    "hi": "hi",
    "te": "te",
    "ta": "ta",
    "bn": "bn",
    "mr": "mr",
    "gu": "gu",
    "kn": "kn",
    "ml": "ml",
    "pa": "pa",
    "or": "or",
}


class LanguageAgent:
    """
    Handles all multilingual operations:
    - Language detection
    - Translation to/from English
    - Transliteration support
    """

    def __init__(self):
        self.default_language = settings.default_language
        self.translation_enabled = settings.enable_translation

        # Cache translators for performance
        self._translators: Dict[str, GoogleTranslator] = {}

    def _get_translator(self, source: str, target: str) -> GoogleTranslator:
        """Get or create a translator instance."""
        key = f"{source}_{target}"
        if key not in self._translators:
            self._translators[key] = GoogleTranslator(source=source, target=target)
        return self._translators[key]

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.

        Returns:
            Language code (e.g., 'hi', 'en', 'te')
        """
        if not text or len(text.strip()) < 3:
            return self.default_language

        try:
            detected = detect(text)

            # Map detected language to supported language
            if detected in SUPPORTED_LANGUAGES:
                return detected

            # Handle some edge cases
            if detected in ["hi", "mr", "ne"]:  # Hindi script languages
                return "hi"
            elif detected in ["te"]:
                return "te"
            elif detected in ["ta"]:
                return "ta"
            elif detected in ["bn"]:
                return "bn"
            elif detected in ["gu"]:
                return "gu"
            elif detected in ["kn"]:
                return "kn"
            elif detected in ["ml"]:
                return "ml"
            elif detected in ["pa"]:
                return "pa"
            elif detected in ["or"]:
                return "or"

            # Default to English for unknown
            return "en"

        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return self.default_language

    def translate_to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text from any language to English.

        Args:
            text: Text to translate
            source_lang: Source language code (auto-detect if None)

        Returns:
            Translated English text
        """
        if not self.translation_enabled:
            return text

        if not text or len(text.strip()) < 2:
            return text

        try:
            # Detect language if not provided
            if not source_lang:
                source_lang = self.detect_language(text)

            # No translation needed if already English
            if source_lang == "en":
                return text

            # Map to Google Translate codes
            source_code = LANGUAGE_CODES.get(source_lang, source_lang)

            # Translate
            translator = self._get_translator(source_code, "en")
            translated = translator.translate(text)

            logger.debug(
                f"Translated from {source_lang}: '{text[:50]}...' -> '{translated[:50]}...'"
            )
            return translated

        except Exception as e:
            logger.warning(f"Translation to English failed: {e}")
            return text

    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate text from English to target language.

        Args:
            text: English text to translate
            target_lang: Target language code

        Returns:
            Translated text in target language
        """
        if not self.translation_enabled:
            return text

        if not text or len(text.strip()) < 2:
            return text

        # No translation needed if target is English
        if target_lang == "en":
            return text

        try:
            # Map to Google Translate codes
            target_code = LANGUAGE_CODES.get(target_lang, target_lang)

            # Translate
            translator = self._get_translator("en", target_code)
            translated = translator.translate(text)

            logger.debug(
                f"Translated to {target_lang}: '{text[:50]}...' -> '{translated[:50]}...'"
            )
            return translated

        except Exception as e:
            logger.warning(f"Translation from English failed: {e}")
            return text

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between any two supported languages.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text
        """
        if source_lang == target_lang:
            return text

        # Route through English if neither is English
        if source_lang != "en" and target_lang != "en":
            english_text = self.translate_to_english(text, source_lang)
            return self.translate_from_english(english_text, target_lang)
        elif source_lang == "en":
            return self.translate_from_english(text, target_lang)
        else:
            return self.translate_to_english(text, source_lang)

    @lru_cache(maxsize=100)
    def get_language_name(self, lang_code: str) -> str:
        """Get display name for a language code."""
        return SUPPORTED_LANGUAGES.get(lang_code, lang_code)

    def is_romanized_indian(self, text: str) -> bool:
        """
        Check if text appears to be romanized Indian language (Hinglish, etc.).

        Common patterns: mixing English with transliterated Hindi words.
        """
        # Simple heuristic: check for common Hindi words in Roman script
        hindi_patterns = [
            "kya",
            "hai",
            "kaise",
            "mujhe",
            "mera",
            "kab",
            "kaun",
            "kahan",
            "aapka",
            "humko",
            "hum",
            "tum",
            "aap",
            "yeh",
            "woh",
            "kuch",
            "nahi",
            "haan",
            "theek",
            "accha",
            "bahut",
            "bohot",
            "karo",
            "karna",
            "milega",
            "milta",
            "chahiye",
            "karein",
            "boliye",
            "bataiye",
            "kripya",
            "dhanyawad",
            "shukriya",
            "namaste",
        ]

        text_lower = text.lower()
        matches = sum(1 for pattern in hindi_patterns if pattern in text_lower)

        # If more than 2 Hindi patterns found, likely Hinglish
        return matches >= 2

    def normalize_query(self, text: str) -> str:
        """
        Normalize a query for processing.
        - Detect if Hinglish/romanized
        - Convert to English for processing if needed
        """
        # Check if romanized Indian language
        if self.is_romanized_indian(text):
            # For now, keep as-is since Groq Llama 3.3 can understand Hinglish
            # Could add transliteration here in future
            return text

        # Detect language and translate if needed
        lang = self.detect_language(text)
        if lang != "en":
            return self.translate_to_english(text, lang)

        return text


# Singleton instance
_language_agent: Optional[LanguageAgent] = None


def get_language_agent() -> LanguageAgent:
    """Get singleton language agent instance."""
    global _language_agent
    if _language_agent is None:
        _language_agent = LanguageAgent()
    return _language_agent
