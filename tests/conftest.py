import os
import tempfile
import pytest

import database.db

db_fd, db_path = tempfile.mkstemp()
os.close(db_fd)
database.db.DB_PATH = db_path

from app import app as _app


_counter = [0]


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    try:
        if os.path.exists(db_path):
            os.unlink(db_path)
    except PermissionError:
        pass


@pytest.fixture
def app():
    yield _app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_user_id():
    db = database.db.get_db()
    user = db.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
    db.close()
    return user["id"]


@pytest.fixture
def empty_user_id():
    _counter[0] += 1
    db = database.db.get_db()
    email = f"empty{_counter[0]}@test.com"
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Empty User", email, "fakehash"),
    )
    db.commit()
    uid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return uid


@pytest.fixture
def auth_client(client):
    client.post(
        "/login",
        data={"email": "demo@spendly.com", "password": "demo123"},
        follow_redirects=True,
    )
    return client
