
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    r=client.get("/api/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_clarification():
    r=client.post("/api/analyze",json={"message":"Biodiversity is declining on my land"})
    assert r.status_code==200
    assert r.json()["status"]=="needs_clarification"

def test_demo():
    r=client.post("/api/analyze",json={"message":"Soil organic carbon: 0.3%. Rainfall: low. Crop: monoculture wheat. Region: semi-arid."})
    assert r.status_code==200
    data=r.json()
    assert data["status"]=="complete"
    assert "recommendation" in data["result"]
    assert len(data["result"]["evidence"])>=1
