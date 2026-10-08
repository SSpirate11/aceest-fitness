"""Client management API (ported from Aceestver-2.x / 3.x Tkinter screens)."""
import sqlite3

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

from aceest import fitness
from aceest.db import get_db

bp = Blueprint("clients", __name__, url_prefix="/api")

WORKOUT_TYPES = {"Strength", "Hypertrophy", "Cardio", "Mobility"}


def _client_or_404(name):
    row = get_db().execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    return dict(row) if row else None


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    row = get_db().execute(
        "SELECT password_hash, role FROM users WHERE username = ?",
        (data.get("username", ""),),
    ).fetchone()
    if row and check_password_hash(row["password_hash"], data.get("password", "")):
        return jsonify(message="Login successful", role=row["role"])
    return jsonify(error="Invalid credentials"), 401


@bp.get("/clients")
def list_clients():
    rows = get_db().execute("SELECT * FROM clients ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("/clients")
def create_client():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(error="name is required"), 400
    program = (data.get("program") or "").upper()
    calories = None
    if data.get("weight") is not None:
        calories = fitness.calculate_calories(data["weight"], program)
    try:
        db = get_db()
        db.execute(
            "INSERT INTO clients (name, age, height, weight, program, calories,"
            " membership_end) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, data.get("age"), data.get("height"), data.get("weight"),
             program or None, calories, data.get("membership_end")),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error=f"Client '{name}' already exists"), 409
    return jsonify(_client_or_404(name)), 201


@bp.get("/clients/<name>")
def get_client(name):
    client = _client_or_404(name)
    if client is None:
        return jsonify(error="Client not found"), 404
    if client["height"] and client["weight"]:
        bmi, category = fitness.calculate_bmi(client["weight"], client["height"])
        client["bmi"] = {"value": bmi, "category": category}
    client["membership_status"] = fitness.membership_status(client["membership_end"])
    return jsonify(client)


@bp.post("/clients/<name>/progress")
def add_progress(name):
    if _client_or_404(name) is None:
        return jsonify(error="Client not found"), 404
    data = request.get_json(silent=True) or {}
    adherence = int(data.get("adherence", -1))
    if not 0 <= adherence <= 100 or not data.get("week"):
        return jsonify(error="week and adherence (0-100) are required"), 400
    db = get_db()
    db.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
               (name, data["week"], adherence))
    db.commit()
    return jsonify(client=name, week=data["week"], adherence=adherence), 201


@bp.get("/clients/<name>/progress")
def get_progress(name):
    rows = get_db().execute(
        "SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY id",
        (name,)).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("/clients/<name>/workouts")
def add_workout(name):
    if _client_or_404(name) is None:
        return jsonify(error="Client not found"), 404
    data = request.get_json(silent=True) or {}
    if data.get("workout_type") not in WORKOUT_TYPES:
        return jsonify(error=f"workout_type must be one of {sorted(WORKOUT_TYPES)}"), 400
    duration = int(data.get("duration_min", 0))
    if duration <= 0 or not data.get("date"):
        return jsonify(error="date and positive duration_min are required"), 400
    db = get_db()
    db.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)"
        " VALUES (?, ?, ?, ?, ?)",
        (name, data["date"], data["workout_type"], duration, data.get("notes", "")))
    db.commit()
    return jsonify(client=name, date=data["date"], workout_type=data["workout_type"],
                   duration_min=duration), 201


@bp.get("/clients/<name>/workouts")
def get_workouts(name):
    rows = get_db().execute(
        "SELECT date, workout_type, duration_min, notes FROM workouts"
        " WHERE client_name = ? ORDER BY date DESC", (name,)).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.get("/clients/<name>/membership")
def check_membership(name):
    client = _client_or_404(name)
    if client is None:
        return jsonify(error="Client not found"), 404
    return jsonify(client=name, membership_end=client["membership_end"],
                   status=fitness.membership_status(client["membership_end"]))

