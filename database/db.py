import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = "expense_tracker.db"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()["cnt"]
    if count > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    today = date.today()
    seed_expenses = [
        (user_id, 45.50, "Food", (today - timedelta(days=28)).isoformat(), "Weekly groceries"),
        (user_id, 35.00, "Transport", (today - timedelta(days=25)).isoformat(), "Metro recharge"),
        (user_id, 120.00, "Bills", (today - timedelta(days=21)).isoformat(), "Electricity bill"),
        (user_id, 25.00, "Health", (today - timedelta(days=18)).isoformat(), "Pharmacy"),
        (user_id, 30.00, "Entertainment", (today - timedelta(days=14)).isoformat(), "Movie tickets"),
        (user_id, 55.00, "Shopping", (today - timedelta(days=10)).isoformat(), "New headphones"),
        (user_id, 15.74, "Food", (today - timedelta(days=7)).isoformat(), "Morning coffee"),
        (user_id, 20.00, "Other", (today - timedelta(days=3)).isoformat(), "Gift wrapping"),
    ]

    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        seed_expenses,
    )
    conn.commit()
    conn.close()
