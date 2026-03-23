"""
Schemes Routes
==============

API endpoints for browsing, searching, and filtering government schemes.
"""

import logging
import re
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import INDIAN_STATES, SCHEME_CATEGORIES, get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

CATEGORY_ORDER = [
    "Agriculture",
    "Health",
    "Education",
    "Housing",
    "Women & Child",
    "Social Welfare",
    "Employment",
    "Business & Entrepreneurship",
    "Financial Inclusion",
    "Rural Development",
    "Urban Development",
    "General",
]

CATEGORY_PATTERNS = {
    "Agriculture": [
        "agriculture",
        "farmers welfare",
        "farmer",
        "crop",
        "kisan",
    ],
    "Health": ["health", "wellness", "medical", "hospital", "insurance"],
    "Education": [
        "education",
        "learning",
        "scholarship",
        "student",
        "school",
        "college",
    ],
    "Housing": ["housing", "shelter", "awas", "house"],
    "Women & Child": ["women and child", "women child", "girl child", "maternal"],
    "Social Welfare": [
        "social welfare",
        "social security",
        "empowerment",
        "community support",
    ],
    "Employment": ["skills", "skill", "employment", "livelihood", "training", "job"],
    "Business & Entrepreneurship": [
        "business",
        "entrepreneurship",
        "entrepreneur",
        "startup",
        "msme",
    ],
    "Financial Inclusion": [
        "financial inclusion",
        "banking",
        "financial services",
        "insurance",
        "credit",
        "loan",
    ],
    "Rural Development": ["rural", "village", "panchayat", "environment"],
    "Urban Development": [
        "urban",
        "transport",
        "infrastructure",
        "sanitation",
        "utility",
        "municipal",
        "city",
    ],
}


def _slugify(value: str) -> str:
    """Create a stable, URL-safe scheme id from free text."""
    if not value:
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug


def _humanize_scheme_name(name: str) -> str:
    """Convert machine/file style names into readable labels."""
    if not name:
        return name
    cleaned = name.replace("_", " ").replace("-", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if cleaned.isupper():
        return cleaned
    return cleaned


def _infer_category(name: str, content: str) -> str:
    """Infer category when metadata category is missing."""
    text = f"{name} {content}".lower()

    keyword_map = {
        "Education": ["scholarship", "stipend", "ugc", "aicte", "student", "education"],
        "Health": ["health", "medical", "hospital", "insurance", "wellness"],
        "Agriculture": ["kisan", "farmer", "agriculture", "crop"],
        "Housing": ["awas", "housing", "house", "shelter"],
        "Employment": ["employment", "job", "skill", "training", "livelihood"],
        "Women & Child": ["women", "child", "girl", "maternal"],
        "Business & Entrepreneurship": ["business", "entrepreneur", "startup", "msme"],
        "Financial Inclusion": ["bank", "loan", "credit", "finance", "subsidy"],
        "Rural Development": ["rural", "village", "panchayat"],
        "Urban Development": ["urban", "city", "municipal"],
    }

    for category, keywords in keyword_map.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "General"


def _sanitize_category_text(value: str) -> str:
    """Normalize raw category strings for reliable matching."""
    cleaned = (value or "").strip().lower()
    cleaned = cleaned.replace("&", " and ")
    cleaned = re.sub(r"[/|;]+", ",", cleaned)
    cleaned = re.sub(r"[^a-z0-9,\s]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" ,")


def _normalize_category(raw_category: str, name: str, content: str) -> str:
    """Map noisy dataset categories into a small curated set."""
    if raw_category:
        cleaned = _sanitize_category_text(raw_category)
        candidates = [part.strip() for part in cleaned.split(",") if part.strip()]
        if cleaned:
            candidates.append(cleaned)

        for candidate in candidates:
            for canonical, patterns in CATEGORY_PATTERNS.items():
                if any(pattern in candidate for pattern in patterns):
                    return canonical

    return _infer_category(name, content)


def _load_chroma_schemes() -> dict:
    """
    Build one scheme record per scheme_id/scheme_name from Chroma metadata.
    Returns dict keyed by scheme_id.
    """
    from app.db.chroma import get_chroma_client

    chroma = get_chroma_client()
    total = chroma.count()
    if total == 0:
        return {}

    rows = chroma.get(limit=total)
    ids = rows.get("ids") or []
    docs = rows.get("documents") or []
    metas = rows.get("metadatas") or []

    schemes = {}

    for idx, chunk_id in enumerate(ids):
        metadata = metas[idx] or {}
        content = (docs[idx] or "").strip()

        name = (
            metadata.get("scheme_name")
            or metadata.get("name")
            or metadata.get("title")
            or metadata.get("label")
            or metadata.get("source_file")
            or metadata.get("source_id")
            or chunk_id
        )
        name = _humanize_scheme_name(str(name).strip())

        scheme_id = (
            metadata.get("scheme_id")
            or _slugify(name)
            or _slugify(str(metadata.get("source_id") or ""))
            or str(chunk_id)
        )
        scheme_id = str(scheme_id).strip()

        raw_category = str(metadata.get("category") or "").strip()
        category = _normalize_category(raw_category, name, content)
        benefit = metadata.get("benefit_summary") or metadata.get("benefits") or ""
        eligibility = (
            metadata.get("eligibility_summary") or metadata.get("eligibility") or ""
        )
        source_url = metadata.get("source_url") or metadata.get("official_link") or None

        record = schemes.get(scheme_id)
        if not record:
            record = {
                "id": scheme_id,
                "name": name,
                "category": category,
                "benefit_summary": str(benefit)[:200],
                "eligibility_summary": str(eligibility)[:240],
                "description": content[:1200],
                "application_process": str(metadata.get("application_process") or "")[
                    :1200
                ],
                "apply_url": source_url,
            }
            schemes[scheme_id] = record
            continue

        if not record.get("benefit_summary") and benefit:
            record["benefit_summary"] = str(benefit)[:200]
        if not record.get("eligibility_summary") and eligibility:
            record["eligibility_summary"] = str(eligibility)[:240]
        if not record.get("description") and content:
            record["description"] = content[:1200]
        if not record.get("application_process") and metadata.get(
            "application_process"
        ):
            record["application_process"] = str(metadata.get("application_process"))[
                :1200
            ]
        if not record.get("apply_url") and source_url:
            record["apply_url"] = source_url
        if record.get("category") == "General":
            record["category"] = _normalize_category(
                raw_category,
                record.get("name", ""),
                record.get("description", ""),
            )

    return schemes


def _load_sample_schemes_as_dict() -> dict:
    """Expose SAMPLE_SCHEMES in dict format compatible with Chroma records."""
    result = {}
    for s in SAMPLE_SCHEMES:
        result[s.id] = {
            "id": s.id,
            "name": s.name,
            "category": _normalize_category(s.category, s.name, s.description),
            "benefit_summary": s.benefit_amount or s.benefits or "",
            "eligibility_summary": s.eligibility_summary or "",
            "description": s.description or "",
            "application_process": s.application_process or "",
            "apply_url": s.apply_url,
        }
    return result


# ==================== Enums ====================


class SchemeType(str, Enum):
    CENTRAL = "central"
    STATE = "state"
    BOTH = "both"


class BeneficiaryType(str, Enum):
    INDIVIDUAL = "individual"
    FAMILY = "family"
    ORGANIZATION = "organization"


# ==================== Models ====================


class EligibilityCriteria(BaseModel):
    """Eligibility criteria for a scheme."""

    age_min: Optional[int] = None
    age_max: Optional[int] = None
    income_max: Optional[float] = None
    gender: Optional[str] = None
    occupation: Optional[List[str]] = None
    caste_category: Optional[List[str]] = None
    states: Optional[List[str]] = None
    other_criteria: Optional[List[str]] = None


class SchemeDocument(BaseModel):
    """Required documents for applying."""

    name: str
    description: str
    is_mandatory: bool = True


class SchemeDetail(BaseModel):
    """Complete scheme details."""

    id: str
    name: str
    name_hindi: Optional[str] = None
    category: str
    scheme_type: SchemeType
    ministry: str
    description: str
    benefits: str
    benefit_amount: Optional[str] = None
    eligibility: EligibilityCriteria
    eligibility_summary: str
    documents_required: List[SchemeDocument]
    application_process: str
    apply_url: Optional[str] = None
    helpline: Optional[str] = None
    last_updated: str
    is_active: bool = True


class SchemeListItem(BaseModel):
    """Scheme summary for list view."""

    id: str
    name: str
    name_hindi: Optional[str] = None
    category: str
    scheme_type: SchemeType
    benefit_summary: str
    eligibility_summary: str
    is_active: bool = True


class SchemeListResponse(BaseModel):
    """Paginated scheme list response."""

    success: bool = True
    total: int
    page: int
    page_size: int
    total_pages: int
    schemes: List[SchemeListItem]


class EligibilityCheckRequest(BaseModel):
    """User profile for eligibility checking."""

    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    income: Optional[float] = None
    occupation: Optional[str] = None
    caste_category: Optional[str] = None
    is_bpl: Optional[bool] = None
    has_land: Optional[bool] = None
    land_size_acres: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "gender": "male",
                "state": "Maharashtra",
                "income": 100000,
                "occupation": "farmer",
                "is_bpl": True,
                "has_land": True,
                "land_size_acres": 2.5,
            }
        }


class EligibleScheme(BaseModel):
    """Scheme with eligibility match score."""

    scheme: SchemeListItem
    match_score: float = Field(..., ge=0, le=1, description="Eligibility match 0-1")
    matched_criteria: List[str]
    missing_criteria: List[str]


class EligibilityCheckResponse(BaseModel):
    """Response with eligible schemes."""

    success: bool = True
    user_profile: dict
    total_eligible: int
    schemes: List[EligibleScheme]


# ==================== Sample Data (Replace with DB) ====================

SAMPLE_SCHEMES = [
    SchemeDetail(
        id="pm-kisan",
        name="PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        name_hindi="प्रधानमंत्री किसान सम्मान निधि",
        category="Agriculture",
        scheme_type=SchemeType.CENTRAL,
        ministry="Ministry of Agriculture & Farmers Welfare",
        description="PM-KISAN is a Central Sector scheme with 100% funding from Government of India. It provides income support to all landholding farmers' families to supplement their financial needs.",
        benefits="Direct income support of ₹6,000 per year to farmer families",
        benefit_amount="₹6,000 per year (₹2,000 every 4 months)",
        eligibility=EligibilityCriteria(
            occupation=["farmer"],
            other_criteria=[
                "Must own cultivable land",
                "Not a government employee",
                "Not an income tax payer",
            ],
        ),
        eligibility_summary="All landholding farmer families with cultivable land are eligible",
        documents_required=[
            SchemeDocument(
                name="Aadhaar Card", description="For identity verification"
            ),
            SchemeDocument(name="Land Records", description="Proof of land ownership"),
            SchemeDocument(
                name="Bank Account Details", description="For direct benefit transfer"
            ),
        ],
        application_process="1. Visit pmkisan.gov.in\n2. Click on 'New Farmer Registration'\n3. Enter Aadhaar number and CAPTCHA\n4. Fill the registration form with land details\n5. Submit and note the registration number",
        apply_url="https://pmkisan.gov.in/",
        helpline="155261 / 011-23381092",
        last_updated="2024-01-15",
    ),
    SchemeDetail(
        id="pm-ayushman",
        name="Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana)",
        name_hindi="प्रधानमंत्री जन आरोग्य योजना",
        category="Health",
        scheme_type=SchemeType.CENTRAL,
        ministry="Ministry of Health and Family Welfare",
        description="World's largest health insurance scheme providing free health coverage up to ₹5 lakh per family per year for secondary and tertiary care hospitalization.",
        benefits="Free health coverage up to ₹5 lakh per family per year",
        benefit_amount="Up to ₹5,00,000 per year",
        eligibility=EligibilityCriteria(
            income_max=200000,
            other_criteria=["Must be listed in SECC 2011 database", "BPL families"],
        ),
        eligibility_summary="BPL families as per SECC 2011 database",
        documents_required=[
            SchemeDocument(name="Aadhaar Card", description="Identity proof"),
            SchemeDocument(
                name="SECC Database Entry", description="Automatic verification"
            ),
            SchemeDocument(
                name="Ration Card",
                description="For family verification",
                is_mandatory=False,
            ),
        ],
        application_process="1. Check eligibility on mera.pmjay.gov.in\n2. Visit nearest CSC or empaneled hospital\n3. Get Ayushman Card created\n4. Use at any empaneled hospital for cashless treatment",
        apply_url="https://pmjay.gov.in/",
        helpline="14555 / 1800-111-565",
        last_updated="2024-01-10",
    ),
    SchemeDetail(
        id="pm-awas-gramin",
        name="Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)",
        name_hindi="प्रधानमंत्री आवास योजना - ग्रामीण",
        category="Housing",
        scheme_type=SchemeType.CENTRAL,
        ministry="Ministry of Rural Development",
        description="Provides financial assistance to houseless and those living in kutcha/dilapidated houses for construction of pucca house with basic amenities.",
        benefits="Financial assistance for house construction in rural areas",
        benefit_amount="₹1.20 lakh (plains) / ₹1.30 lakh (hilly areas)",
        eligibility=EligibilityCriteria(
            other_criteria=[
                "Houseless or living in kutcha house",
                "Rural resident",
                "Name in PMAY-G Awaas+ list",
            ]
        ),
        eligibility_summary="Houseless rural families without pucca house",
        documents_required=[
            SchemeDocument(name="Aadhaar Card", description="Identity proof"),
            SchemeDocument(
                name="Job Card (MGNREGA)", description="For rural resident verification"
            ),
            SchemeDocument(name="Bank Account", description="For fund transfer"),
        ],
        application_process="1. Check eligibility on pmayg.nic.in\n2. Apply through Gram Panchayat\n3. Verification by Block/District officials\n4. Sanction letter issued\n5. Receive funds in installments",
        apply_url="https://pmayg.nic.in/",
        helpline="1800-11-6446",
        last_updated="2024-01-20",
    ),
]


# ==================== Endpoints ====================


@router.get("", response_model=SchemeListResponse)
@router.get("/", response_model=SchemeListResponse)
async def list_schemes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    scheme_type: Optional[SchemeType] = Query(
        None, description="central, state, or both"
    ),
    state: Optional[str] = Query(None, description="Filter by state"),
    search: Optional[str] = Query(None, description="Search term"),
):
    """
    Get paginated list of government schemes with optional filters.
    """
    try:
        # Try Supabase first
        try:
            from app.db.supabase_client import get_supabase

            client = get_supabase()

            query = client.table("schemes").select("*").eq("is_active", True)

            if category:
                query = query.eq("category", category)
            if scheme_type:
                query = query.eq("scheme_type", scheme_type.value)
            if search:
                query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")

            # Get total count
            count_result = (
                client.table("schemes")
                .select("id", count="exact")
                .eq("is_active", True)
                .execute()
            )
            total = count_result.count or 0

            # Pagination
            offset = (page - 1) * page_size
            result = query.range(offset, offset + page_size - 1).execute()

            if result.data and len(result.data) > 0:
                total_pages = (total + page_size - 1) // page_size
                return SchemeListResponse(
                    total=total,
                    page=page,
                    page_size=page_size,
                    total_pages=total_pages,
                    schemes=[
                        SchemeListItem(
                            id=s["id"],
                            name=s["name"],
                            name_hindi=s.get("name_hindi"),
                            category=s.get("category", "General"),
                            scheme_type=s.get("scheme_type", "central"),
                            benefit_summary=s.get("benefit_amount")
                            or (
                                s.get("benefits", "")[:100] if s.get("benefits") else ""
                            ),
                            eligibility_summary=s.get("eligibility_summary", ""),
                        )
                        for s in result.data
                    ],
                )
        except Exception as db_err:
            logger.debug(f"Supabase query failed, using fallback: {db_err}")

        # Try merged catalog (sample + Chroma) next
        try:
            merged = _load_sample_schemes_as_dict()
            merged.update(_load_chroma_schemes())
            merged_schemes = list(merged.values())
            if merged_schemes:
                filtered = merged_schemes

                normalized_filter = (
                    _normalize_category(category, "", "") if category else None
                )

                if normalized_filter:
                    filtered = [
                        s
                        for s in filtered
                        if s.get("category", "").lower() == normalized_filter.lower()
                    ]

                if search:
                    search_lower = search.lower()
                    filtered = [
                        s
                        for s in filtered
                        if search_lower in s.get("name", "").lower()
                        or search_lower in s.get("description", "").lower()
                        or search_lower in s.get("eligibility_summary", "").lower()
                        or search_lower in s.get("benefit_summary", "").lower()
                    ]

                if filtered:
                    filtered = sorted(filtered, key=lambda s: s.get("name", "").lower())
                    total = len(filtered)
                    total_pages = (total + page_size - 1) // page_size
                    start = (page - 1) * page_size
                    end = start + page_size
                    paginated = filtered[start:end]

                    return SchemeListResponse(
                        total=total,
                        page=page,
                        page_size=page_size,
                        total_pages=total_pages,
                        schemes=[
                            SchemeListItem(
                                id=s["id"],
                                name=s["name"],
                                name_hindi=None,
                                category=s.get("category", "General"),
                                scheme_type=SchemeType.CENTRAL,
                                benefit_summary=s.get("benefit_summary") or "",
                                eligibility_summary=s.get("eligibility_summary")
                                or "Click for more details",
                            )
                            for s in paginated
                        ],
                    )
        except Exception as chroma_err:
            logger.debug(f"Chroma query failed, using sample fallback: {chroma_err}")

        # Fallback to SAMPLE_SCHEMES
        filtered = SAMPLE_SCHEMES.copy()

        if category:
            filtered = [s for s in filtered if s.category.lower() == category.lower()]

        if scheme_type:
            filtered = [s for s in filtered if s.scheme_type == scheme_type]

        if search:
            search_lower = search.lower()
            filtered = [
                s
                for s in filtered
                if search_lower in s.name.lower()
                or search_lower in s.description.lower()
            ]

        # Pagination
        total = len(filtered)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        paginated = filtered[start:end]

        return SchemeListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            schemes=[
                SchemeListItem(
                    id=s.id,
                    name=s.name,
                    name_hindi=s.name_hindi,
                    category=s.category,
                    scheme_type=s.scheme_type,
                    benefit_summary=s.benefit_amount or s.benefits[:100],
                    eligibility_summary=s.eligibility_summary,
                )
                for s in paginated
            ],
        )

    except Exception as e:
        logger.error(f"List schemes error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get categories, preferring live values from ChromaDB."""
    try:
        merged_categories = {
            _normalize_category(
                (s.get("category") or "").strip(), s.get("name", ""), ""
            )
            for s in {
                **_load_sample_schemes_as_dict(),
                **_load_chroma_schemes(),
            }.values()
            if (s.get("category") or "").strip()
        }
        ordered = [
            category for category in CATEGORY_ORDER if category in merged_categories
        ]
        if ordered:
            return {"categories": ordered}
    except Exception as e:
        logger.debug(f"Categories from Chroma unavailable: {e}")

    fallback = [
        category for category in CATEGORY_ORDER if category in SCHEME_CATEGORIES
    ]
    return {"categories": fallback or CATEGORY_ORDER}


@router.get("/states")
async def get_states():
    """Get all Indian states and UTs."""
    return {"states": INDIAN_STATES}


@router.get("/{scheme_id}", response_model=SchemeDetail)
async def get_scheme_details(scheme_id: str):
    """
    Get detailed information about a specific scheme.
    """
    try:
        # Try Supabase first
        try:
            from app.db.supabase_client import get_supabase

            client = get_supabase()
            result = (
                client.table("schemes")
                .select("*")
                .eq("id", scheme_id)
                .single()
                .execute()
            )

            if result.data:
                s = result.data
                return SchemeDetail(
                    id=s["id"],
                    name=s["name"],
                    name_hindi=s.get("name_hindi"),
                    category=s.get("category", "General"),
                    scheme_type=s.get("scheme_type", "central"),
                    ministry=s.get("ministry", ""),
                    description=s.get("description", ""),
                    benefits=s.get("benefits", ""),
                    benefit_amount=s.get("benefit_amount"),
                    eligibility_summary=s.get("eligibility_summary", ""),
                    eligibility=EligibilityCriteria(),
                    documents_required=[
                        SchemeDocument(**d)
                        for d in (s.get("documents_required") or [])
                        if isinstance(d, dict)
                    ],
                    application_process=s.get("application_process", ""),
                    apply_url=s.get("apply_url"),
                    helpline=s.get("helpline"),
                    last_updated=s.get("last_updated", ""),
                    is_active=s.get("is_active", True),
                )
        except Exception as db_err:
            logger.debug(f"Supabase query failed, using fallback: {db_err}")

        # Try ChromaDB next
        try:
            chroma_scheme = _load_chroma_schemes().get(scheme_id)
            if chroma_scheme:
                description = chroma_scheme.get("description") or chroma_scheme["name"]
                return SchemeDetail(
                    id=chroma_scheme["id"],
                    name=chroma_scheme["name"],
                    name_hindi=None,
                    category=chroma_scheme.get("category", "General"),
                    scheme_type=SchemeType.CENTRAL,
                    ministry="",
                    description=description,
                    benefits=chroma_scheme.get("benefit_summary") or "",
                    benefit_amount=chroma_scheme.get("benefit_summary") or None,
                    eligibility_summary=chroma_scheme.get("eligibility_summary")
                    or "Refer official guidelines",
                    eligibility=EligibilityCriteria(),
                    documents_required=[],
                    application_process=chroma_scheme.get("application_process")
                    or "Refer official scheme portal for application steps.",
                    apply_url=chroma_scheme.get("apply_url"),
                    helpline=None,
                    last_updated="",
                    is_active=True,
                )
        except Exception as chroma_err:
            logger.debug(f"Chroma detail lookup failed: {chroma_err}")

        # Fallback to SAMPLE_SCHEMES
        scheme = next((s for s in SAMPLE_SCHEMES if s.id == scheme_id), None)

        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")

        return scheme

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get scheme error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/eligibility", response_model=EligibilityCheckResponse)
async def check_eligibility(request: EligibilityCheckRequest):
    """
    Check which schemes a user is eligible for based on their profile.
    Returns schemes sorted by eligibility match score.
    """
    try:
        eligible_schemes = []

        for scheme in SAMPLE_SCHEMES:
            matched = []
            missing = []

            # Check occupation
            if scheme.eligibility.occupation:
                if request.occupation and request.occupation.lower() in [
                    o.lower() for o in scheme.eligibility.occupation
                ]:
                    matched.append("Occupation matches")
                else:
                    missing.append(
                        f"Requires occupation: {', '.join(scheme.eligibility.occupation)}"
                    )

            # Check income
            if scheme.eligibility.income_max:
                if request.income and request.income <= scheme.eligibility.income_max:
                    matched.append("Income within limit")
                else:
                    missing.append(
                        f"Income should be below ₹{scheme.eligibility.income_max:,.0f}"
                    )

            # Check state
            if scheme.eligibility.states:
                if request.state and request.state in scheme.eligibility.states:
                    matched.append("State eligible")
                elif request.state:
                    missing.append(f"Not available in {request.state}")

            # Calculate match score
            total_criteria = len(matched) + len(missing)
            if total_criteria > 0:
                match_score = len(matched) / total_criteria
            else:
                match_score = 0.5  # Neutral if no specific criteria

            # Include if any match or no strict criteria
            if match_score > 0 or len(missing) == 0:
                eligible_schemes.append(
                    EligibleScheme(
                        scheme=SchemeListItem(
                            id=scheme.id,
                            name=scheme.name,
                            name_hindi=scheme.name_hindi,
                            category=scheme.category,
                            scheme_type=scheme.scheme_type,
                            benefit_summary=scheme.benefit_amount
                            or scheme.benefits[:100],
                            eligibility_summary=scheme.eligibility_summary,
                        ),
                        match_score=match_score,
                        matched_criteria=matched,
                        missing_criteria=missing,
                    )
                )

        # Sort by match score descending
        eligible_schemes.sort(key=lambda x: x.match_score, reverse=True)

        return EligibilityCheckResponse(
            user_profile=request.model_dump(exclude_none=True),
            total_eligible=len([s for s in eligible_schemes if s.match_score >= 0.5]),
            schemes=eligible_schemes,
        )

    except Exception as e:
        logger.error(f"Eligibility check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/quick")
async def quick_search(q: str = Query(..., min_length=2, description="Search query")):
    """
    Quick search for schemes by name or keywords.
    Returns top 5 matching schemes.
    """
    try:
        search_lower = q.lower()
        matches = []

        for scheme in SAMPLE_SCHEMES:
            score = 0
            if search_lower in scheme.name.lower():
                score += 10
            if scheme.name_hindi and search_lower in scheme.name_hindi:
                score += 8
            if search_lower in scheme.description.lower():
                score += 5
            if search_lower in scheme.category.lower():
                score += 3

            if score > 0:
                matches.append({"scheme": scheme.name, "id": scheme.id, "score": score})

        matches.sort(key=lambda x: x["score"], reverse=True)

        return {"results": matches[:5]}

    except Exception as e:
        logger.error(f"Quick search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
