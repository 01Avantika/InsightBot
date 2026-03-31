"""
db/database.py — SQLite database manager for InsightBot
Handles users, upload history, analysis history, and chat history
"""

import sqlite3
import bcrypt
import os
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "insightbot.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS uploads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            filename    TEXT    NOT NULL,
            file_type   TEXT    NOT NULL,
            file_path   TEXT    NOT NULL,
            file_size   INTEGER,
            uploaded_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            upload_id   INTEGER NOT NULL,
            analysis    TEXT    NOT NULL,
            insights    TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (upload_id) REFERENCES uploads(id)
        );

        CREATE TABLE IF NOT EXISTS chats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            upload_id   INTEGER,
            role        TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()


# ── User Auth ─────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str) -> dict:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, username, email, created_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row)
    except sqlite3.IntegrityError as e:
        raise ValueError("Username or email already exists.") from e
    finally:
        conn.close()


def verify_user(username: str, password: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row["password"].encode()):
        return {"id": row["id"], "username": row["username"], "email": row["email"]}
    return None


# ── Uploads ───────────────────────────────────────────────────────────────────

def save_upload(user_id: int, filename: str, file_type: str, file_path: str, file_size: int) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO uploads (user_id, filename, file_type, file_path, file_size) VALUES (?, ?, ?, ?, ?)",
        (user_id, filename, file_type, file_path, file_size),
    )
    conn.commit()
    upload_id = cur.lastrowid
    conn.close()
    return upload_id


def get_user_uploads(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM uploads WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Analyses ──────────────────────────────────────────────────────────────────

def save_analysis(user_id: int, upload_id: int, analysis: str, insights: str = "") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO analyses (user_id, upload_id, analysis, insights) VALUES (?, ?, ?, ?)",
        (user_id, upload_id, analysis, insights),
    )
    conn.commit()
    aid = cur.lastrowid
    conn.close()
    return aid


def get_user_analyses(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, u.filename FROM analyses a
           JOIN uploads u ON a.upload_id = u.id
           WHERE a.user_id = ? ORDER BY a.created_at DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Chats ─────────────────────────────────────────────────────────────────────

def save_message(user_id: int, role: str, message: str, upload_id: int | None = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chats (user_id, upload_id, role, message) VALUES (?, ?, ?, ?)",
        (user_id, upload_id, role, message),
    )
    conn.commit()
    conn.close()


def get_user_chats(user_id: int, upload_id: int | None = None) -> list[dict]:
    conn = get_connection()
    if upload_id:
        rows = conn.execute(
            "SELECT * FROM chats WHERE user_id = ? AND upload_id = ? ORDER BY created_at",
            (user_id, upload_id),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM chats WHERE user_id = ? ORDER BY created_at DESC LIMIT 100",
            (user_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_chat(user_id: int, upload_id: int | None = None):
    conn = get_connection()
    if upload_id:
        conn.execute("DELETE FROM chats WHERE user_id = ? AND upload_id = ?", (user_id, upload_id))
    else:
        conn.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
