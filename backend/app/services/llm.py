"""
Sahay AI - LLM Service
========================

Groq API integration for grounded scheme answers.
"""

import logging
from typing import Any, Dict, List, Optional

from groq import APIStatusError, Groq
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import get_settings

logger = logging.getLogger(__name__)

FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
]


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, APIStatusError):
        return exc.status_code in {408, 409, 429, 500, 502, 503, 504}
    return True


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.groq_api_key
        self.model = settings.groq_chat_model or FALLBACK_MODELS[0]
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def _models_to_try(self) -> List[str]:
        models = [self.model]
        for candidate in FALLBACK_MODELS:
            if candidate not in models:
                models.append(candidate)
        return models

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(_retryable),
        reraise=True,
    )
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, temperature=temperature, max_tokens=max_tokens)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is not configured")

        last_error: Optional[Exception] = None
        for model in self._models_to_try():
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if model != self.model:
                    logger.info("Groq fallback model used: %s", model)
                return response.choices[0].message.content
            except APIStatusError as exc:
                last_error = exc
                if exc.status_code in {404, 400}:
                    logger.warning("Groq model %s unavailable (%s). Trying next.", model, exc.status_code)
                    continue
                raise
        raise last_error or RuntimeError("No Groq chat model available")

    def generate_response(
        self,
        query: str,
        context: List[str],
        language: str = "en",
    ) -> str:
        lang_map = {
            "te": "Telugu",
            "hi": "Hindi",
            "en": "English",
            "ta": "Tamil",
            "kn": "Kannada",
            "or": "Odia",
        }
        lang_name = lang_map.get(language, "English")
        system_prompt = (
            f"You are Sahay, a guide for Indian government schemes. "
            f"Answer only from the provided context. Respond in {lang_name}."
        )
        context_text = "\n\n".join(
            f"[Document {i + 1}]: {doc}" for i, doc in enumerate(context)
        )
        prompt = (
            "Based on the following scheme records, answer the user's question.\n\n"
            f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
        )
        return self.complete(prompt, system_prompt=system_prompt)


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
