"""
Agent Orchestrator
=================

Master orchestrator that routes user queries to appropriate specialized agents
and manages conversation context using Groq Llama 3.3.

Author: Jagadeep Mamidi
"""

import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.rag.hybrid_retriever import HybridRetriever
from app.services.llm import get_llm_service

logger = logging.getLogger(__name__)
settings = get_settings()


class ConversationMemory:
    """
    Manages conversation history and context for sessions.
    """

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._sessions: Dict[str, Dict] = defaultdict(
            lambda: {
                "messages": [],
                "user_profile": {},
                "language": "en",
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
            }
        )

    def add_message(
        self, session_id: str, role: str, content: str, metadata: dict = None
    ):
        """Add a message to session history."""
        session = self._sessions[session_id]
        session["messages"].append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
        )
        session["last_activity"] = datetime.utcnow().isoformat()

        if len(session["messages"]) > self.max_turns * 2:
            session["messages"] = session["messages"][-self.max_turns * 2 :]

    def get_history(self, session_id: str) -> Optional[Dict]:
        """Get session history."""
        return self._sessions.get(session_id)

    def get_context_messages(self, session_id: str, last_n: int = 6) -> List[Dict]:
        """Get recent messages for context."""
        session = self._sessions.get(session_id, {})
        messages = session.get("messages", [])
        return messages[-last_n:]

    def update_user_profile(self, session_id: str, profile: dict):
        """Update user profile for personalization."""
        self._sessions[session_id]["user_profile"].update(profile)

    def set_language(self, session_id: str, language: str):
        """Set user's preferred language."""
        self._sessions[session_id]["language"] = language


class AgentOrchestrator:
    """
    Main orchestrator that:
    1. Classifies user intent
    2. Routes to appropriate processing path
    3. Retrieves relevant context via RAG
    4. Generates responses using Groq Llama
    5. Manages conversation flow
    """

    def __init__(self):
        self.memory = ConversationMemory()
        self.retriever = HybridRetriever()
        self.llm = get_llm_service()

        self.intent_categories = {
            "scheme_info": "User wants information about a specific government scheme",
            "eligibility_check": "User wants to check if they are eligible for schemes",
            "application_help": "User needs help with the application process",
            "document_query": "User asks about required documents",
            "benefit_query": "User asks about benefits or amounts",
            "status_check": "User wants to check application status",
            "comparison": "User wants to compare multiple schemes",
            "general_query": "General question about government schemes",
            "greeting": "User greeting or casual conversation",
            "feedback": "User providing feedback",
            "unknown": "Cannot determine the intent",
        }

        logger.info("AgentOrchestrator initialized with Groq Llama 3.3")

    async def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Groq LLM API with retry logic."""
        try:
            if system_prompt:
                return self.llm.complete(prompt, system_prompt=system_prompt)
            return self.llm.complete(prompt)
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise

    async def classify_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify user intent using Groq LLM.
        Returns intent category and confidence score.
        """
        try:
            prompt = f"""Analyze the following user query and classify its intent.

User Query: "{query}"

Possible intents:
{chr(10).join(f"- {k}: {v}" for k, v in self.intent_categories.items())}

Respond with JSON format:
{{"intent": "intent_name", "confidence": 0.0-1.0, "entities": {{"scheme_name": null, "category": null, "state": null}}}}

Only output the JSON, no other text."""

            response = await self._call_llm(prompt)

            import json

            try:
                clean_response = response.strip()
                if clean_response.startswith("```"):
                    clean_response = clean_response.split("```")[1]
                    if clean_response.startswith("json"):
                        clean_response = clean_response[4:]

                result = json.loads(clean_response)
                return result
            except json.JSONDecodeError:
                return {"intent": "general_query", "confidence": 0.5, "entities": {}}

        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {"intent": "general_query", "confidence": 0.5, "entities": {}}

    def _get_language_specific_prompt(self, language: str) -> str:
        """Get language-specific system prompt."""
        prompts = {
            "te": """You are Sahay AI (సహాయ AI), a helpful and empathetic assistant that helps Indian citizens discover and understand government welfare schemes.

NALKAVATCHALU (GUIDELINES):
1. Be warm, friendly, and use simple Telugu that everyone can understand
2. Base your answers on the provided context from official scheme documents
3. If information is not in the context, say so honestly
4. When discussing eligibility, be clear about requirements
5. Provide actionable next steps when possible
6. Use ₹ symbol for Indian Rupees
7. Be culturally sensitive and respectful
8. Always respond in Telugu (తెలుగు)

Keep responses concise but informative.""",
            "hi": """आप Sahay AI (सहाय AI) हैं, जो भारतीय नागरिकों को सरकारी कल्याण योजनाओं को खोजने और समझने में मदद करने वाले सहायक हैं।

दिशानिर्देश (GUIDELINES):
1. गर्मजोशी से बात करें और सरल हिंदी का उपयोग करें
2. अपने उत्तर आधिकारिक योजना दस्तावेजों से प्रदान की गई जानकारी पर आधारित करें
3. यदि जानकारी संदर्भ में नहीं है, तो ईमानदारी से बताएं
4. पात्रता पर चर्चा करते समय आवश्यकताओं के बारे में स्पष्ट रहें
5. जब भी संभव हो, कार्रवाई योग्य अगले कदम प्रदान करें
6. भारतीय रुपये के लिए ₹ प्रतीक का उपयोग करें
7. सांस्कृतिक रूप से संवेदनशील और सम्मानजनक रहें
8. हमेशा हिंदी में जवाब दें

जवाब संक्षिप्त लेकिन जानकारीपूर्ण रखें।""",
            "en": """You are Sahay AI (सहाय AI), a helpful and empathetic assistant that helps Indian citizens discover and understand government welfare schemes.

GUIDELINES:
1. Be warm, friendly, and use simple language that everyone can understand
2. Base your answers on the provided context from official scheme documents
3. If information is not in the context, say so honestly and suggest where to find it
4. When discussing eligibility, be clear about requirements
5. Provide actionable next steps when possible
6. Use ₹ symbol for Indian Rupees
7. Be culturally sensitive and respectful

Keep responses concise but informative (2-4 paragraphs max).""",
        }

        return prompts.get(language, prompts["en"])

    def _clean_response_intro(
        self, response: str, intent: str, history: List[Dict]
    ) -> str:
        """Remove repetitive greeting boilerplate from ongoing non-greeting chats."""
        if intent == "greeting":
            return response.strip()

        assistant_turns = [m for m in history if m.get("role") == "assistant"]
        if not assistant_turns:
            return response.strip()

        cleaned = response.strip()
        cleaned = re.sub(
            r"^(namaste|hello|hi|hey)\s*[\!\.,:\-]*\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"^(i\s*(am|m|would be|'d be)\s+happy\s+to\s+help(?:\s+you)?(?:\s+with[^.?!]*)?[.?!]\s*)",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        return cleaned.strip() or response.strip()

    async def generate_response(
        self,
        query: str,
        context: List[str],
        session_id: str,
        intent_info: Dict,
        user_profile: Optional[Dict] = None,
    ) -> str:
        """
        Generate a response using Groq Llama with RAG context.
        """
        try:
            history = self.memory.get_context_messages(session_id)
            history_text = ""
            if history:
                history_text = "Recent conversation:\n" + "\n".join(
                    [
                        f"{'User' if m['role'] == 'user' else 'Sahay AI'}: {m['content']}"
                        for m in history[-4:]
                    ]
                )

            context_text = (
                "\n\n".join(context)
                if context
                else "No specific scheme information available."
            )

            profile_text = ""
            if user_profile:
                profile_parts = []
                if user_profile.get("state"):
                    profile_parts.append(f"State: {user_profile['state']}")
                if user_profile.get("occupation"):
                    profile_parts.append(f"Occupation: {user_profile['occupation']}")
                if user_profile.get("income"):
                    profile_parts.append(f"Annual Income: ₹{user_profile['income']:,}")
                if profile_parts:
                    profile_text = "User Profile: " + ", ".join(profile_parts)

            session = self.memory.get_history(session_id)
            language = session.get("language", "en") if session else "en"
            system_prompt = self._get_language_specific_prompt(language)

            prompt = f"""{system_prompt}

Do not start the answer with greetings or pleasantries unless the user greeted you first.

{history_text}

{profile_text}

RELEVANT SCHEME INFORMATION:
{context_text}

USER INTENT: {intent_info.get("intent", "general_query")}

USER QUESTION: {query}

SAHAY AI RESPONSE:"""

            response = await self._call_llm(prompt)
            return self._clean_response_intro(
                response,
                intent_info.get("intent", "general_query"),
                history,
            )

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

    async def process(
        self,
        query: str,
        language: str = "en",
        session_id: Optional[str] = None,
        user_profile: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user queries.

        Returns:
            Dict with response, intent, confidence, schemes, and suggested questions
        """
        if not session_id:
            session_id = f"session_{datetime.utcnow().timestamp()}"

        try:
            if user_profile:
                self.memory.update_user_profile(session_id, user_profile)

            self.memory.add_message(session_id, "user", query)
            self.memory.set_language(session_id, language)

            intent_info = await self.classify_intent(query)
            logger.info(f"Intent classified: {intent_info}")

            context = self.retriever.search(query, top_k=5)
            context_texts = [doc.get("content", "") for doc in context]

            response = await self.generate_response(
                query=query,
                context=context_texts,
                session_id=session_id,
                intent_info=intent_info,
                user_profile=user_profile or {},
            )

            self.memory.add_message(
                session_id,
                "assistant",
                response,
                {
                    "intent": intent_info.get("intent"),
                    "confidence": intent_info.get("confidence"),
                },
            )

            schemes = []
            for doc in context[:3]:
                if doc.get("metadata", {}).get("scheme_id"):
                    schemes.append(
                        {
                            "id": doc["metadata"]["scheme_id"],
                            "name": doc["metadata"].get("scheme_name", ""),
                            "category": doc["metadata"].get("category", ""),
                            "benefit_summary": doc["metadata"].get(
                                "benefit_summary", ""
                            ),
                            "eligibility_summary": doc["metadata"].get(
                                "eligibility_summary", ""
                            ),
                        }
                    )

            suggested = await self._generate_suggestions(query, intent_info, response)

            return {
                "response": response,
                "intent": intent_info.get("intent"),
                "confidence": intent_info.get("confidence"),
                "schemes": schemes,
                "suggested_questions": suggested,
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"Query processing error: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "intent": "error",
                "confidence": 0,
                "schemes": [],
                "suggested_questions": [
                    "What schemes am I eligible for?",
                    "Tell me about PM-KISAN",
                ],
                "session_id": session_id,
            }

    async def _generate_suggestions(
        self, query: str, intent_info: Dict, response: str
    ) -> List[str]:
        """Generate contextual follow-up question suggestions."""
        intent = intent_info.get("intent", "general_query")

        suggestions_map = {
            "scheme_info": [
                "What are the eligibility criteria?",
                "How do I apply for this scheme?",
                "What documents are required?",
            ],
            "eligibility_check": [
                "What documents do I need?",
                "How do I apply online?",
                "What is the benefit amount?",
            ],
            "application_help": [
                "What is the deadline?",
                "Where is the nearest center?",
                "How long does approval take?",
            ],
            "document_query": [
                "Can I apply online?",
                "What if I don't have a document?",
                "Where can I get these documents?",
            ],
            "benefit_query": [
                "When will I receive the money?",
                "How is the payment made?",
                "Can family members also benefit?",
            ],
            "greeting": [
                "What schemes am I eligible for?",
                "Tell me about PM-KISAN",
                "How can I check my application status?",
            ],
        }

        return suggestions_map.get(
            intent,
            [
                "What other schemes are available?",
                "Check my eligibility",
                "Help me apply",
            ],
        )

    def get_conversation_history(self, session_id: str) -> Optional[Dict]:
        """Get full conversation history for a session."""
        return self.memory.get_history(session_id)


_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
