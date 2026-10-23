import copy
from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = {
    "tok-patient-a-7f3k": {"user_id": 1, "name": "Patient A", "role": "patient"},
    "tok-patient-b-9q2m": {"user_id": 2, "name": "Patient B", "role": "patient"},
    "tok-admin-4x8z": {"user_id": 99, "name": "Clinic Admin", "role": "admin"}
}

SEED_APPOINTMENTS = {
    101: {"id": 101, "patient_id": 1, "clinic": "Harbour Clinic", "starts_at": "2026-11-03T09:00", "status": "booked"},
    102: {"id": 102, "patient_id": 1, "clinic": "Harbour Clinic", "starts_at": "2026-11-10T14:30", "status": "booked"},
    201: {"id": 201, "patient_id": 2, "clinic": "Harbour Clinic", "starts_at": "2026-11-04T11:00", "status": "booked"}
}

APPOINTMENTS = copy.deepcopy(SEED_APPOINTMENTS)

def reset_data():
    global APPOINTMENTS
    APPOINTMENTS.clear()
    APPOINTMENTS.update(copy.deepcopy(SEED_APPOINTMENTS))

def current_user():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        return USERS.get(token)
    return None

def can_access_appointment(user, appointment):
    return user["role"] == "admin" or appointment["patient_id"] == user["user_id"]

@app.route("/appointments", methods=["GET"])
def get_appointments():
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401
    
    if user["role"] == "admin":
        return jsonify(list(APPOINTMENTS.values())), 200
    else:
        filtered = [apt for apt in APPOINTMENTS.values() if apt["patient_id"] == user["user_id"]]
        return jsonify(filtered), 200

@app.route("/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401
    
    apt = APPOINTMENTS.get(appointment_id)
    if not apt:
        return jsonify({"error": "not found"}), 404
    
    if not can_access_appointment(user, apt):
        return jsonify({"error": "not found"}), 404

    return jsonify(apt), 200

@app.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def cancel_appointment(appointment_id):
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401
    
    apt = APPOINTMENTS.get(appointment_id)
    if not apt:
        return jsonify({"error": "not found"}), 404
    
    if not can_access_appointment(user, apt):
        return jsonify({"error": "not found"}), 404

    apt["status"] = "cancelled"
    return jsonify(apt), 200
