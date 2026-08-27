from app.knowledge.catalog import get_scheme, load_catalog, match_eligibility
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.query_parser import parse_query


def test_catalog_has_flagship_schemes():
    ids = {scheme["id"] for scheme in load_catalog()}
    assert "pm-kisan" in ids
    assert "pm-jay" in ids
    assert "pmay-g" in ids
    assert "mgnrega" in ids
    assert len(ids) >= 25


def test_legacy_scheme_ids_resolve():
    assert get_scheme("pm-ayushman")["id"] == "pm-jay"
    assert get_scheme("pm-awas-gramin")["id"] == "pmay-g"


def test_parse_farmer_query_extracts_occupation_and_scheme():
    parsed = parse_query("I am a farmer. Am I eligible for PM-KISAN?")
    assert parsed["occupation"] == "farmer"
    assert "pm-kisan" in parsed["scheme_ids"]
    assert parsed["intent"] in {"eligibility_check", "scheme_info"}


def test_retriever_ranks_pm_kisan_for_farmer_income_query():
    retriever = HybridRetriever()
    hits = retriever.search("I am a farmer. How do I get the 6000 rupee support?", top_k=5)
    ids = [hit["id"] for hit in hits]
    assert "pm-kisan" in ids[:2]
    assert hits[0]["score"] > 0


def test_retriever_ranks_ayushman_for_health_cover_query():
    retriever = HybridRetriever()
    hits = retriever.search("How do I get Ayushman Bharat health insurance card?", top_k=5)
    ids = [hit["id"] for hit in hits]
    assert "pm-jay" in ids[:2]


def test_retriever_ranks_mudra_for_shop_loan_query():
    retriever = HybridRetriever()
    hits = retriever.search("I run a small shop. Is there a mudra loan?", top_k=5)
    ids = [hit["id"] for hit in hits]
    assert "mudra" in ids[:3]


def test_eligibility_boosts_farmer_schemes():
    retriever = HybridRetriever()
    profile = {"occupation": "farmer", "has_land": True}
    hits = retriever.search(
        "What schemes can I apply for?",
        top_k=5,
        user_profile=profile,
    )
    ids = [hit["id"] for hit in hits]
    assert "pm-kisan" in ids


def test_eligibility_scores_landholding_farmer():
    scheme = get_scheme("pm-kisan")
    scored = match_eligibility(scheme, {"occupation": "farmer", "has_land": True})
    assert scored["match_score"] >= 0.9
    assert scored["matched_criteria"]


def test_query_path_does_not_need_embeddings():
    retriever = HybridRetriever()
    stats = retriever.get_stats()
    assert stats["mode"] == "catalog_bm25"
    assert stats["has_vector_search"] is False
    assert stats["catalog_schemes"] >= 25
