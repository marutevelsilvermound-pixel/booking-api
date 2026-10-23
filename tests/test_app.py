import pytest
from app import app, reset_data

A = {"Authorization": "Bearer tok-patient-a-7f3k"}
B = {"Authorization": "Bearer tok-patient-b-9q2m"}
ADMIN = {"Authorization": "Bearer tok-admin-4x8z"}


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


def test_patient_can_view_own_appointment(client):
    response = client.get("/appointments/101", headers=A)
    assert response.status_code == 200
    assert response.get_json()["id"] == 101


def test_patient_cannot_view_another_patients_appointment(client):
    response = client.get("/appointments/201", headers=A)
    assert response.status_code == 404


def test_admin_can_view_any_appointment(client):
    response = client.get("/appointments/201", headers=ADMIN)
    assert response.status_code == 200
    assert response.get_json()["id"] == 201


def test_patient_cannot_cancel_another_patients_appointment(client):
    response = client.delete("/appointments/201", headers=A)
    assert response.status_code == 404
    assert response.get_json()["error"] == "not found"

    own_data = client.get("/appointments/201", headers=B).get_json()
    assert own_data["status"] == "booked"


def test_patient_can_cancel_own_appointment(client):
    response = client.delete("/appointments/101", headers=A)
    assert response.status_code == 200
    assert response.get_json()["status"] == "cancelled"
