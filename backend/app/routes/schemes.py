"""
Schemes Routes
==============

API endpoints for browsing, searching, and filtering government schemes.
"""

import logging
from typing import List, Optional
from enum import Enum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import get_settings, SCHEME_CATEGORIES, INDIAN_STATES

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


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
                "land_size_acres": 2.5
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
            other_criteria=["Must own cultivable land", "Not a government employee", "Not an income tax payer"]
        ),
        eligibility_summary="All landholding farmer families with cultivable land are eligible",
        documents_required=[
            SchemeDocument(name="Aadhaar Card", description="For identity verification"),
            SchemeDocument(name="Land Records", description="Proof of land ownership"),
            SchemeDocument(name="Bank Account Details", description="For direct benefit transfer")
        ],
        application_process="1. Visit pmkisan.gov.in\n2. Click on 'New Farmer Registration'\n3. Enter Aadhaar number and CAPTCHA\n4. Fill the registration form with land details\n5. Submit and note the registration number",
        apply_url="https://pmkisan.gov.in/",
        helpline="155261 / 011-23381092",
        last_updated="2024-01-15"
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
            other_criteria=["Must be listed in SECC 2011 database", "BPL families"]
        ),
        eligibility_summary="BPL families as per SECC 2011 database",
        documents_required=[
            SchemeDocument(name="Aadhaar Card", description="Identity proof"),
            SchemeDocument(name="SECC Database Entry", description="Automatic verification"),
            SchemeDocument(name="Ration Card", description="For family verification", is_mandatory=False)
        ],
        application_process="1. Check eligibility on mera.pmjay.gov.in\n2. Visit nearest CSC or empaneled hospital\n3. Get Ayushman Card created\n4. Use at any empaneled hospital for cashless treatment",
        apply_url="https://pmjay.gov.in/",
        helpline="14555 / 1800-111-565",
        last_updated="2024-01-10"
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
            other_criteria=["Houseless or living in kutcha house", "Rural resident", "Name in PMAY-G Awaas+ list"]
        ),
        eligibility_summary="Houseless rural families without pucca house",
        documents_required=[
            SchemeDocument(name="Aadhaar Card", description="Identity proof"),
            SchemeDocument(name="Job Card (MGNREGA)", description="For rural resident verification"),
            SchemeDocument(name="Bank Account", description="For fund transfer")
        ],
        application_process="1. Check eligibility on pmayg.nic.in\n2. Apply through Gram Panchayat\n3. Verification by Block/District officials\n4. Sanction letter issued\n5. Receive funds in installments",
        apply_url="https://pmayg.nic.in/",
        helpline="1800-11-6446",
        last_updated="2024-01-20"
    )
]


# ==================== Endpoints ====================

@router.get("", response_model=SchemeListResponse)
@router.get("/", response_model=SchemeListResponse)
async def list_schemes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    scheme_type: Optional[SchemeType] = Query(None, description="central, state, or both"),
    state: Optional[str] = Query(None, description="Filter by state"),
    search: Optional[str] = Query(None, description="Search term")
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
            count_result = client.table("schemes").select("id", count="exact").eq("is_active", True).execute()
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
                            benefit_summary=s.get("benefit_amount") or (s.get("benefits", "")[:100] if s.get("benefits") else ""),
                            eligibility_summary=s.get("eligibility_summary", "")
                        )
                        for s in result.data
                    ]
                )
        except Exception as db_err:
            logger.debug(f"Supabase query failed, using fallback: {db_err}")
        
        # Fallback to SAMPLE_SCHEMES
        filtered = SAMPLE_SCHEMES.copy()
        
        if category:
            filtered = [s for s in filtered if s.category.lower() == category.lower()]
        
        if scheme_type:
            filtered = [s for s in filtered if s.scheme_type == scheme_type]
        
        if search:
            search_lower = search.lower()
            filtered = [s for s in filtered if 
                       search_lower in s.name.lower() or 
                       search_lower in s.description.lower()]
        
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
                    eligibility_summary=s.eligibility_summary
                )
                for s in paginated
            ]
        )
        
    except Exception as e:
        logger.error(f"List schemes error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get all scheme categories."""
    return {"categories": SCHEME_CATEGORIES}


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
            result = client.table("schemes").select("*").eq("id", scheme_id).single().execute()
            
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
                        SchemeDocument(**d) for d in (s.get("documents_required") or [])
                        if isinstance(d, dict)
                    ],
                    application_process=s.get("application_process", ""),
                    apply_url=s.get("apply_url"),
                    helpline=s.get("helpline"),
                    last_updated=s.get("last_updated", ""),
                    is_active=s.get("is_active", True)
                )
        except Exception as db_err:
            logger.debug(f"Supabase query failed, using fallback: {db_err}")
        
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
                if request.occupation and request.occupation.lower() in [o.lower() for o in scheme.eligibility.occupation]:
                    matched.append("Occupation matches")
                else:
                    missing.append(f"Requires occupation: {', '.join(scheme.eligibility.occupation)}")
            
            # Check income
            if scheme.eligibility.income_max:
                if request.income and request.income <= scheme.eligibility.income_max:
                    matched.append("Income within limit")
                else:
                    missing.append(f"Income should be below ₹{scheme.eligibility.income_max:,.0f}")
            
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
                            benefit_summary=scheme.benefit_amount or scheme.benefits[:100],
                            eligibility_summary=scheme.eligibility_summary
                        ),
                        match_score=match_score,
                        matched_criteria=matched,
                        missing_criteria=missing
                    )
                )
        
        # Sort by match score descending
        eligible_schemes.sort(key=lambda x: x.match_score, reverse=True)
        
        return EligibilityCheckResponse(
            user_profile=request.model_dump(exclude_none=True),
            total_eligible=len([s for s in eligible_schemes if s.match_score >= 0.5]),
            schemes=eligible_schemes
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
