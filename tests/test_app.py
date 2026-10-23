import pytest
from app import app, reset_data

A = {"Authorization": "Bearer tok-patient-a-7f3k"}

@pytest.fixture
def client():
    reset_data()
    return app.test_client()

def test_patient_lists_own_appointments(client):
    response = client.get("/appointments", headers=A)
    assert response.status_code == 200
    data = response.get_json()
    ids = {item["id"] for item in data}
    assert ids == {101, 102}

def test_missing_token_is_rejected(client):
    response = client.get("/appointments/101")
    assert response.status_code == 401
