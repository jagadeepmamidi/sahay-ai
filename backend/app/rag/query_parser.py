"""Fast heuristic query understanding. No LLM round-trip."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.core.config import INDIAN_STATES, SCHEME_CATEGORIES
from app.knowledge.catalog import load_catalog

OCCUPATION_ALIASES = {
    "farmer": [
        "farmer",
        "kisan",
        "krishi",
        "agriculture",
        "cultivator",
        "farming",
        "rythu",
        "kisaan",
    ],
    "student": ["student", "school", "college", "scholarship", "class", "exam"],
    "self-employed": [
        "self employed",
        "self-employed",
        "shopkeeper",
        "vendor",
        "business",
        "kirana",
        "thela",
        "artisan",
        "msme",
        "startup",
    ],
    "unemployed": ["unemployed", "jobless", "no job", "looking for work", "rozgar"],
    "employee": ["salaried", "private job", "government employee", "job holder"],
}

INTENT_PATTERNS = {
    "greeting": [
        r"\b(hi|hello|hey|namaste|namaskar|good morning|good evening)\b",
        r"^(hi|hello|hey)[\s!.]*$",
    ],
    "eligibility_check": [
        r"\b(eligib|am i|do i qualify|can i get|can i apply|paatr|patra)\b",
        r"\bfor me\b",
        r"\bmy (age|income|state|occupation)\b",
    ],
    "document_query": [r"\b(document|papers|aadhaar|ration card|proof)\b"],
    "application_help": [r"\b(how (do|to) apply|apply online|application|register)\b"],
    "benefit_query": [r"\b(benefit|amount|how much|rs\.|rupee|instalment|money)\b"],
    "status_check": [r"\b(status|track|instalment credited|payment received)\b"],
    "comparison": [r"\b(compare|difference between|vs\.?|versus)\b"],
}


def _normalize(text: str) -> str:
    cleaned = (text or "").lower()
    cleaned = re.sub(r"[-_/]", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\u0900-\u097f\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _alias_index() -> Dict[str, str]:
    index: Dict[str, str] = {}
    for scheme in load_catalog():
        names = [
            scheme["id"],
            scheme["name"],
            scheme.get("full_name", ""),
            *(scheme.get("aliases") or []),
        ]
        for name in names:
            key = _normalize(name)
            if len(key) >= 3:
                index[key] = scheme["id"]
    return index


def parse_query(query: str, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract intent, scheme mentions, occupation, state, and category."""
    raw = query or ""
    normalized = _normalize(raw)
    profile = user_profile or {}

    mentioned_ids: List[str] = []
    alias_index = _alias_index()
    # Longest alias first so "pm kisan" wins over "kisan"
    for alias in sorted(alias_index, key=len, reverse=True):
        if alias in normalized and alias_index[alias] not in mentioned_ids:
            mentioned_ids.append(alias_index[alias])

    occupation = profile.get("occupation")
    if not occupation:
        for canonical, aliases in OCCUPATION_ALIASES.items():
            if any(alias in normalized for alias in aliases):
                occupation = canonical
                break

    state = profile.get("state")
    if not state:
        for candidate in INDIAN_STATES:
            if candidate.lower() in normalized:
                state = candidate
                break

    category = None
    for candidate in SCHEME_CATEGORIES:
        if candidate.lower() in normalized:
            category = candidate
            break

    intent = "general_query"
    confidence = 0.55
    if mentioned_ids and re.search(r"\b(what is|tell me|about|details)\b", normalized):
        intent = "scheme_info"
        confidence = 0.9
    for name, patterns in INTENT_PATTERNS.items():
        if any(re.search(pattern, normalized) for pattern in patterns):
            intent = name
            confidence = 0.82
            break
    if mentioned_ids and intent == "general_query":
        intent = "scheme_info"
        confidence = 0.75
    if occupation and intent == "general_query":
        intent = "eligibility_check"
        confidence = 0.7

    return {
        "intent": intent,
        "confidence": confidence,
        "scheme_ids": mentioned_ids,
        "occupation": occupation,
        "state": state,
        "category": category,
        "normalized_query": normalized,
        "entities": {
            "scheme_name": mentioned_ids[0] if mentioned_ids else None,
            "category": category,
            "state": state,
            "occupation": occupation,
        },
    }
