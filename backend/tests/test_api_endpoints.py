from fastapi.testclient import TestClient

from app.main import app


SAMPLE_INCIDENT = {
    "event_type": "accident",
    "corridor": "Outer Ring Road",
    "zone": "East",
    "description": "Multi-vehicle crash blocking two lanes near a junction",
    "severity": "critical",
    "metadata": {"source": "test"},
}


def test_required_endpoints_work_without_external_credentials():
    with TestClient(app) as client:
        assert client.get("/api/v1/health").status_code == 200

        for path in [
            "/api/v1/predict/closure",
            "/api/v1/predict/priority",
            "/api/v1/predict/clearance",
            "/api/v1/predict/resources",
            "/api/v1/retrieve/similar",
            "/api/v1/intelligence/cause",
        ]:
            response = client.post(path, json=SAMPLE_INCIDENT)
            assert response.status_code == 200, response.text

        analyze = client.post("/api/v1/analyze", json=SAMPLE_INCIDENT)
        assert analyze.status_code == 200, analyze.text
        payload = analyze.json()
        assert payload["closure_prediction"]
        assert payload["priority"]
        assert payload["clearance"]
        assert payload["resources"]
        assert payload["similar_incidents"]
        assert payload["copilot_summary"]

        copilot = client.post(
            "/api/v1/copilot",
            json={"question": "What should officers do?", "analysis": payload},
        )
        assert copilot.status_code == 200, copilot.text

        for path in [
            "/api/v1/dashboard/kpis",
            "/api/v1/dashboard/incidents",
            "/api/v1/dashboard/heatmap",
            "/api/v1/dashboard/corridors",
            "/api/v1/dashboard/resources",
        ]:
            response = client.get(path)
            assert response.status_code == 200, response.text
