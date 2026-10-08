"""SQLite persistence layer (schema ported from Aceestver-2.x / 3.x)."""
import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    age INTEGER,
    height REAL,
    weight REAL,
    program TEXT,
    calories INTEGER,
    membership_end TEXT
);
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    week TEXT NOT NULL,
    adherence INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    date TEXT NOT NULL,
    workout_type TEXT NOT NULL,
    duration_min INTEGER NOT NULL,
    notes TEXT
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    if not db.execute("SELECT 1 FROM users WHERE username = 'admin'").fetchone():
        password = os.environ.get("ACEEST_ADMIN_PASSWORD", "admin")
        db.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", generate_password_hash(password), "Admin"),
        )
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
