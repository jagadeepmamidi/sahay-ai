"""
Sahay AI - LLM Service
========================

Groq API integration for LLM completions.
Uses Llama 3.3 70B for fast, free inference.

Author: Jagadeep Mamidi
"""

import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from tenacity.retry import retry_if_exception_type
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using Groq API.
    
    Uses Llama 3.3 70B for fast inference on free tier.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.groq_api_key
        self.model = settings.groq_chat_model
        
        self.client = Groq(api_key=self.api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30)
    )
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity (0-1)
            max_tokens: Max response length
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30)
    )
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Continue a chat conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Creativity (0-1)
            max_tokens: Max response length
            
        Returns:
            Assistant's response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def generate_response(
        self,
        query: str,
        context: List[str],
        language: str = "en"
    ) -> str:
        """
        Generate a response using RAG context.
        
        Args:
            query: User's question
            context: Retrieved document chunks
            language: Response language
            
        Returns:
            Generated response
        """
        lang_map = {
            "te": "Telugu",
            "hi": "Hindi",
            "en": "English",
            "ta": "Tamil",
            "kn": "Kannada",
            "or": "Odia"
        }
        lang_name = lang_map.get(language, "English")
        
        system_prompt = f"""You are Sahay AI, a helpful assistant that helps Indian citizens 
        find government welfare schemes. Answer questions based on the provided context.
        Always respond in {lang_name} language unless the user writes in English.
        Keep responses concise and informative."""
        
        context_text = "\n\n".join([f"[Document {i+1}]: {doc}" for i, doc in enumerate(context)])
        
        prompt = f"""Based on the following information about government schemes, 
        answer the user's question:

Context:
{context_text}

Question: {query}

Answer:"""
        
        return self.complete(prompt, system_prompt=system_prompt)


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create singleton LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
