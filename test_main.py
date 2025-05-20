from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI + Jenkins!"}

def test_soma():
    response = client.get("/soma?a=2&b=3")
    assert response.status_code == 200
    assert response.json() == {"resultado": 5}