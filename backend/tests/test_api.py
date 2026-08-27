from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_schemes_catalog_lists_flagship_records():
    response = client.get("/api/v1/schemes", params={"page_size": 50})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 25
    ids = {item["id"] for item in payload["schemes"]}
    assert "pm-kisan" in ids
    assert "pm-jay" in ids


def test_scheme_detail_includes_official_url():
    response = client.get("/api/v1/schemes/pm-kisan")
    assert response.status_code == 200
    payload = response.json()
    assert payload["apply_url"] == "https://pmkisan.gov.in/"
    assert "6,000" in payload["benefits"] or "6000" in payload["benefits"]


def test_chat_returns_pm_kisan_for_named_query():
    response = client.post(
        "/api/v1/chat",
        json={"message": "Tell me about PM-KISAN", "language": "en"},
    )
    assert response.status_code == 200
    payload = response.json()
    ids = [item["id"] for item in payload.get("schemes") or []]
    assert "pm-kisan" in ids
    assert "pmkisan.gov.in" in payload["message"].lower() or "6,000" in payload["message"] or "6000" in payload["message"]


def test_eligibility_ranks_farmer_schemes():
    response = client.post(
        "/api/v1/schemes/eligibility",
        json={"occupation": "farmer", "has_land": True, "age": 40},
    )
    assert response.status_code == 200
    payload = response.json()
    top = payload["schemes"][0]
    assert top["scheme"]["id"] in {"pm-kisan", "pmfby", "kcc", "pmksy"}
    assert top["match_score"] >= 0.5
