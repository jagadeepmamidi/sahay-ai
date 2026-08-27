"""
Agent Orchestrator
==================

Single-pass RAG: parse query, retrieve scheme records, generate one grounded
answer. Intent classification is heuristic, not an extra LLM round-trip.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.rag.hybrid_retriever import get_retriever
from app.rag.query_parser import parse_query
from app.services.llm import get_llm_service

logger = logging.getLogger(__name__)
settings = get_settings()

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
}


class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._sessions: Dict[str, Dict] = defaultdict(
            lambda: {
                "messages": [],
                "user_profile": {},
                "language": "en",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
            }
        )

    def add_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        session = self._sessions[session_id]
        session["messages"].append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
            }
        )
        session["last_activity"] = datetime.now(timezone.utc).isoformat()
        if len(session["messages"]) > self.max_turns * 2:
            session["messages"] = session["messages"][-self.max_turns * 2 :]

    def get_history(self, session_id: str) -> Optional[Dict]:
        return self._sessions.get(session_id)

    def get_context_messages(self, session_id: str, last_n: int = 6) -> List[Dict]:
        session = self._sessions.get(session_id, {})
        return session.get("messages", [])[-last_n:]

    def update_user_profile(self, session_id: str, profile: dict):
        self._sessions[session_id]["user_profile"].update(profile)

    def set_language(self, session_id: str, language: str):
        self._sessions[session_id]["language"] = language


class AgentOrchestrator:
    def __init__(self):
        self.memory = ConversationMemory()
        self.retriever = get_retriever()
        self.llm = get_llm_service()
        logger.info("AgentOrchestrator ready (catalog RAG, single LLM pass)")

    def _format_scheme_record(self, doc: Dict[str, Any], index: int) -> str:
        meta = doc.get("metadata") or {}
        scheme = doc.get("scheme") or {}
        docs = scheme.get("documents_required") or []
        doc_line = ", ".join(item.get("name") for item in docs if item.get("name")) or "See official portal"
        return (
            f"[SCHEME {index}] {meta.get('scheme_name') or scheme.get('name')}\n"
            f"Official name: {scheme.get('full_name') or meta.get('full_name') or ''}\n"
            f"Category: {meta.get('category')}\n"
            f"Ministry: {scheme.get('ministry') or meta.get('ministry') or ''}\n"
            f"Benefit: {scheme.get('benefits') or meta.get('benefit_summary')}\n"
            f"Eligibility: {scheme.get('eligibility_summary') or meta.get('eligibility_summary')}\n"
            f"Documents: {doc_line}\n"
            f"How to apply: {scheme.get('application_process') or ''}\n"
            f"Official URL: {scheme.get('apply_url') or meta.get('apply_url') or ''}\n"
            f"Helpline: {scheme.get('helpline') or 'Not listed'}"
        )

    def _template_response(self, query: str, hits: List[Dict[str, Any]], intent: str) -> str:
        if intent == "greeting":
            return (
                "Namaste. I can help you find central government schemes, check likely "
                "eligibility, and point you to the official application page. Tell me your "
                "work, state, or the scheme name."
            )
        if not hits:
            return (
                "I do not have a matching scheme in the current catalog for that question. "
                "Try a scheme name such as PM-KISAN or Ayushman Bharat, or describe your "
                "occupation and need. You can also search the official catalogue at "
                "https://www.myscheme.gov.in/"
            )

        lines = [
            "Here are the closest official scheme records for your question. Confirm final "
            "eligibility on the ministry portal before you apply."
        ]
        for doc in hits[:3]:
            meta = doc.get("metadata") or {}
            scheme = doc.get("scheme") or {}
            name = meta.get("scheme_name") or scheme.get("name")
            lines.append("")
            lines.append(f"{name}")
            lines.append(f"Benefit: {scheme.get('benefits') or meta.get('benefit_summary')}")
            lines.append(
                f"Who it is for: {scheme.get('eligibility_summary') or meta.get('eligibility_summary')}"
            )
            apply_url = scheme.get("apply_url") or meta.get("apply_url")
            if apply_url:
                lines.append(f"Apply or read more: {apply_url}")
        return "\n".join(lines)

    def _system_prompt(self, language: str) -> str:
        language_name = LANGUAGE_NAMES.get(language, "English")
        return f"""You are Sahay, a public-scheme guide for Indian citizens.

Rules:
- Use ONLY the scheme records in the user message. Do not invent amounts, dates, deadlines, or eligibility rules.
- If a detail is missing from the records, say so and point to the official URL.
- Prefer short, practical answers. Lead with the direct answer, then 1-3 matching schemes.
- For each scheme include benefit, who it is for, one next step, and the official URL if present.
- Do not start with a greeting unless the user greeted you.
- Never claim you have submitted an application or checked a live government database.
- Respond in {language_name}. Keep official scheme names in their common English form.
- Do not use em dashes. Use commas, periods, or a hyphen.
"""

    async def generate_response(
        self,
        query: str,
        context: List[str],
        session_id: str,
        intent_info: Dict,
        user_profile: Optional[Dict] = None,
        hits: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        language = "en"
        session = self.memory.get_history(session_id)
        if session:
            language = session.get("language", "en")

        if not settings.groq_api_key:
            return self._template_response(query, hits or [], intent_info.get("intent", "general_query"))

        history = self.memory.get_context_messages(session_id)
        history_text = ""
        if history:
            history_text = "Recent conversation:\n" + "\n".join(
                f"{'User' if m['role'] == 'user' else 'Sahay'}: {m['content']}"
                for m in history[-4:]
            )

        profile_text = ""
        if user_profile:
            parts = [
                f"{key}: {value}"
                for key, value in user_profile.items()
                if value not in (None, "")
            ]
            if parts:
                profile_text = "User profile: " + ", ".join(parts)

        prompt = f"""{history_text}

{profile_text}

SCHEME RECORDS:
{chr(10).join(context) if context else "No matching scheme records."}

USER INTENT: {intent_info.get("intent")}
USER QUESTION: {query}

Write the answer now."""
        try:
            response = self.llm.complete(
                prompt,
                system_prompt=self._system_prompt(language),
                temperature=0.2,
                max_tokens=700,
            )
            return self._clean_response_intro(
                self._sanitize_copy(response),
                intent_info.get("intent", "general_query"),
                history,
            )
        except Exception as exc:
            logger.error("LLM generation failed, using template: %s", exc)
            return self._template_response(query, hits or [], intent_info.get("intent", "general_query"))

    def _sanitize_copy(self, text: str) -> str:
        cleaned = text or ""
        for old, new in (("\u2014", "-"), ("\u2013", "-"), ("\u2011", "-"), ("\u00a0", " ")):
            cleaned = cleaned.replace(old, new)
        return cleaned

    def _clean_response_intro(self, response: str, intent: str, history: List[Dict]) -> str:
        if intent == "greeting":
            return (response or "").strip()
        assistant_turns = [m for m in history if m.get("role") == "assistant"]
        if not assistant_turns:
            return (response or "").strip()
        cleaned = (response or "").strip()
        cleaned = re.sub(
            r"^(namaste|hello|hi|hey)\s*[!.:\-]*\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        return cleaned.strip() or (response or "").strip()

    async def classify_intent(self, query: str) -> Dict[str, Any]:
        return parse_query(query)

    async def process(
        self,
        query: str,
        language: str = "en",
        session_id: Optional[str] = None,
        user_profile: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        if not session_id:
            session_id = f"session_{datetime.now(timezone.utc).timestamp()}"

        try:
            if user_profile:
                self.memory.update_user_profile(session_id, user_profile)
            self.memory.add_message(session_id, "user", query)
            self.memory.set_language(session_id, language)

            search_query = query
            if language != "en":
                try:
                    from app.agents.language_agent import get_language_agent

                    search_query = get_language_agent().translate_to_english(query, language)
                except Exception as exc:
                    logger.warning("Query translation skipped: %s", exc)
                    search_query = query

            intent_info = parse_query(search_query, user_profile)
            hits: List[Dict[str, Any]] = []
            if intent_info.get("intent") != "greeting":
                hits = self.retriever.search(
                    search_query, top_k=5, user_profile=user_profile
                )

            context_texts = [
                self._format_scheme_record(doc, index + 1) for index, doc in enumerate(hits)
            ]
            response = await self.generate_response(
                query=query,
                context=context_texts,
                session_id=session_id,
                intent_info=intent_info,
                user_profile=user_profile or {},
                hits=hits,
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
            seen = set()
            for doc in hits[:4]:
                meta = doc.get("metadata") or {}
                scheme_id = meta.get("scheme_id") or doc.get("id")
                if not scheme_id or scheme_id in seen:
                    continue
                seen.add(scheme_id)
                schemes.append(
                    {
                        "id": scheme_id,
                        "name": meta.get("scheme_name") or "",
                        "category": meta.get("category") or "",
                        "benefit_summary": meta.get("benefit_summary") or "",
                        "eligibility_summary": meta.get("eligibility_summary") or "",
                        "apply_url": meta.get("apply_url"),
                    }
                )

            return {
                "response": response,
                "intent": intent_info.get("intent"),
                "confidence": intent_info.get("confidence"),
                "schemes": schemes,
                "suggested_questions": self._generate_suggestions(intent_info, schemes),
                "session_id": session_id,
                "retrieval_count": len(hits),
            }
        except Exception as exc:
            logger.error("Query processing error: %s", exc, exc_info=True)
            return {
                "response": "I could not complete that request. Please try again with a scheme name or a short description of your work and need.",
                "intent": "error",
                "confidence": 0,
                "schemes": [],
                "suggested_questions": [
                    "Tell me about PM-KISAN",
                    "What health cover can my family get?",
                    "I am a farmer in Maharashtra. What can I apply for?",
                ],
                "session_id": session_id,
            }

    def _generate_suggestions(self, intent_info: Dict, schemes: List[Dict]) -> List[str]:
        if schemes:
            name = schemes[0].get("name") or "this scheme"
            return [
                f"What documents are needed for {name}?",
                f"How do I apply for {name}?",
                "What else might I be eligible for?",
            ]
        intent = intent_info.get("intent")
        mapping = {
            "greeting": [
                "I am a farmer. Which schemes fit me?",
                "Tell me about Ayushman Bharat",
                "How does PM-KISAN pay the Rs. 6,000?",
            ],
            "eligibility_check": [
                "I need housing support in a village",
                "What scholarships can a student apply for?",
                "Are there loans for a small shop?",
            ],
        }
        return mapping.get(
            intent,
            [
                "What schemes am I eligible for?",
                "Tell me about PM-KISAN",
                "How do I apply for Ayushman Bharat?",
            ],
        )

    def get_conversation_history(self, session_id: str) -> Optional[Dict]:
        return self.memory.get_history(session_id)


_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
