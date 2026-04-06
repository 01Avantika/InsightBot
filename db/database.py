"""
db/database.py — SQLite database manager for InsightBot
Handles users, upload history, analysis history, chat history, and OTP verification.
"""

import sqlite3
import bcrypt
import os
import random
import string
from datetime import datetime, timedelta
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
            is_verified INTEGER NOT NULL DEFAULT 0,
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
            FOREIGN KEY (user_id)   REFERENCES users(id),
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

        CREATE TABLE IF NOT EXISTS otp_codes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT    NOT NULL,
            code       TEXT    NOT NULL,
            purpose    TEXT    NOT NULL DEFAULT 'signup',
            expires_at TEXT    NOT NULL,
            used       INTEGER NOT NULL DEFAULT 0
        );
    """)

    # ── Safe migration: add is_verified to existing DBs that predate this column
    try:
        c.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists — fine

    conn.commit()
    conn.close()


# ═════════════════════════════════════════════════════════════════════════════
#  OTP  (new)
# ═════════════════════════════════════════════════════════════════════════════

def generate_otp(email: str, purpose: str = "signup") -> str:
    """
    Generate a fresh 6-digit OTP for the given email + purpose.
    Invalidates any previous unused codes for the same pair.
    Returns the plain-text code (caller must send it to the user).
    """
    code       = "".join(random.choices(string.digits, k=6))
    expires_at = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    # Invalidate old unused codes for this email+purpose
    conn.execute(
        "UPDATE otp_codes SET used=1 WHERE email=? AND purpose=? AND used=0",
        (email, purpose),
    )
    conn.execute(
        "INSERT INTO otp_codes (email, code, purpose, expires_at) VALUES (?,?,?,?)",
        (email, code, purpose, expires_at),
    )
    conn.commit()
    conn.close()
    return code


def verify_otp(email: str, code: str, purpose: str = "signup") -> tuple[bool, str]:
    """
    Validate a submitted OTP.
    Returns (True, "ok") on success or (False, reason_string) on failure.
    Marks the code as used on success or expiry so it cannot be reused.
    """
    conn = get_connection()
    row  = conn.execute(
        """SELECT * FROM otp_codes
           WHERE email=? AND code=? AND purpose=? AND used=0
           ORDER BY id DESC LIMIT 1""",
        (email, code, purpose),
    ).fetchone()

    if not row:
        conn.close()
        return False, "Invalid code — please check and try again."

    expires_at = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S")
    if datetime.utcnow() > expires_at:
        conn.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row["id"],))
        conn.commit()
        conn.close()
        return False, "Code has expired — please request a new one."

    conn.execute("UPDATE otp_codes SET used=1 WHERE id=?", (row["id"],))
    conn.commit()
    conn.close()
    return True, "ok"


# ═════════════════════════════════════════════════════════════════════════════
#  USER AUTH  (your originals, extended for OTP flow)
# ═════════════════════════════════════════════════════════════════════════════

def create_user(username: str, email: str, password: str, verified: bool = False) -> dict:
    """
    Hash password and insert user.
    Pass verified=True after OTP confirmation to set is_verified=1 immediately.
    Raises ValueError on duplicate username / email.
    """
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn   = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password, is_verified) VALUES (?,?,?,?)",
            (username, email, hashed, 1 if verified else 0),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, username, email, is_verified, created_at FROM users WHERE username=?",
            (username,),
        ).fetchone()
        return dict(row)
    except sqlite3.IntegrityError as e:
        msg = str(e).lower()
        if "username" in msg:
            raise ValueError("Username is already taken.")
        raise ValueError("An account with that email already exists.")
    finally:
        conn.close()


def verify_user(username: str, password: str) -> dict | None:
    """
    Verify login credentials.  Accepts username OR email in the first field.
    Returns user dict on success, None on failure.
    NOTE: does NOT block unverified users — that check lives in login.py so
    the UI can show a helpful message instead of a silent None.
    """
    conn = get_connection()
    row  = conn.execute(
        "SELECT * FROM users WHERE username=? OR email=?", (username, username)
    ).fetchone()
    conn.close()
    if not row:
        return None
    if not bcrypt.checkpw(password.encode(), row["password"].encode()):
        return None
    return {"id": row["id"], "username": row["username"],
            "email": row["email"], "is_verified": row["is_verified"]}


def mark_user_verified(email: str):
    """Set is_verified=1 for the given email."""
    conn = get_connection()
    conn.execute("UPDATE users SET is_verified=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()


def get_user_by_email(email: str) -> dict | None:
    conn = get_connection()
    row  = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_username(username: str) -> dict | None:
    conn = get_connection()
    row  = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def email_exists(email: str) -> bool:
    conn = get_connection()
    row  = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return row is not None


def username_exists(username: str) -> bool:
    conn = get_connection()
    row  = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row is not None


# ═════════════════════════════════════════════════════════════════════════════
#  UPLOADS  (unchanged)
# ═════════════════════════════════════════════════════════════════════════════

def save_upload(user_id: int, filename: str, file_type: str,
                file_path: str, file_size: int) -> int:
    conn = get_connection()
    cur  = conn.execute(
        "INSERT INTO uploads (user_id, filename, file_type, file_path, file_size) VALUES (?,?,?,?,?)",
        (user_id, filename, file_type, file_path, file_size),
    )
    conn.commit()
    upload_id = cur.lastrowid
    conn.close()
    return upload_id


def get_user_uploads(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM uploads WHERE user_id=? ORDER BY uploaded_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═════════════════════════════════════════════════════════════════════════════
#  ANALYSES  (unchanged)
# ═════════════════════════════════════════════════════════════════════════════

def save_analysis(user_id: int, upload_id: int, analysis: str, insights: str = "") -> int:
    conn = get_connection()
    cur  = conn.execute(
        "INSERT INTO analyses (user_id, upload_id, analysis, insights) VALUES (?,?,?,?)",
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
           WHERE a.user_id=? ORDER BY a.created_at DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ═════════════════════════════════════════════════════════════════════════════
#  CHATS  (unchanged)
# ═════════════════════════════════════════════════════════════════════════════

def save_message(user_id: int, role: str, message: str,
                 upload_id: int | None = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chats (user_id, upload_id, role, message) VALUES (?,?,?,?)",
        (user_id, upload_id, role, message),
    )
    conn.commit()
    conn.close()


def get_user_chats(user_id: int, upload_id: int | None = None) -> list[dict]:
    conn = get_connection()
    if upload_id:
        rows = conn.execute(
            "SELECT * FROM chats WHERE user_id=? AND upload_id=? ORDER BY created_at",
            (user_id, upload_id),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM chats WHERE user_id=? ORDER BY created_at DESC LIMIT 100",
            (user_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_chat(user_id: int, upload_id: int | None = None):
    conn = get_connection()
    if upload_id:
        conn.execute(
            "DELETE FROM chats WHERE user_id=? AND upload_id=?", (user_id, upload_id)
        )
    else:
        conn.execute("DELETE FROM chats WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()