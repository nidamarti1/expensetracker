import os
import sqlite3
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'spendly.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def create_user(name, email, password):
    password_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    expenses = [
        (user_id, 42.50,  "Food",          (today - timedelta(days=1)).isoformat(),  "Grocery run"),
        (user_id, 18.00,  "Transport",     (today - timedelta(days=3)).isoformat(),  "Uber ride"),
        (user_id, 120.00, "Bills",         (today - timedelta(days=5)).isoformat(),  "Electricity bill"),
        (user_id, 35.74,  "Health",        (today - timedelta(days=7)).isoformat(),  "Pharmacy"),
        (user_id, 15.00,  "Entertainment", (today - timedelta(days=10)).isoformat(), "Netflix subscription"),
        (user_id, 89.00,  "Shopping",      (today - timedelta(days=12)).isoformat(), "Amazon order"),
        (user_id, 10.00,  "Other",         (today - timedelta(days=14)).isoformat(), "Miscellaneous"),
        (user_id, 16.00,  "Food",          (today - timedelta(days=16)).isoformat(), "Restaurant dinner"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()
