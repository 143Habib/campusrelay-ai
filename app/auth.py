"""PBKDF2 password hashing, opaque database sessions, CSRF and login throttling."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import secrets
import time

from fastapi import HTTPException, Request
from .database import connection

ITERATIONS = 310_000
SESSION_SECONDS = 60 * 60 * 12
DUMMY_HASH = "pbkdf2_sha256$310000$4cd218ba77651e256b8f41b93af09bcf$0c0a6a28415dbebf64d66ba0edc293515769f53583d52202450084436ab1df17"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        method, rounds, salt, expected = password_hash.split("$")
        if method != "pbkdf2_sha256" or int(rounds) < 200_000:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    role: str
    csrf: str

    def public(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}


def get_user(request: Request) -> User:
    token = request.cookies.get("cr_session", "")
    if not token or len(token) > 160:
        raise HTTPException(401, detail="Please sign in to continue.")
    with connection(request.app.state.settings.db_path) as db:
        row = db.execute("""
          SELECT u.id, u.name, u.email, u.role, s.csrf_token
          FROM sessions s JOIN users u ON u.id=s.user_id
          WHERE s.token_hash=? AND s.expires_at>?
        """, (hash_token(token), int(time.time()))).fetchone()
    if not row:
        raise HTTPException(401, detail="Your session has expired. Please sign in again.")
    return User(row["id"], row["name"], row["email"], row["role"], row["csrf_token"])


def check_csrf(request: Request, user: User) -> None:
    supplied = request.headers.get("x-csrf-token", "")
    if not supplied or not hmac.compare_digest(supplied, user.csrf):
        raise HTTPException(403, detail="Security token missing or invalid. Refresh the page and retry.")


def check_origin(request: Request) -> None:
    """Reject cross-origin unsafe actions, including unauthenticated login and registration."""
    origin = request.headers.get("origin", "").rstrip("/")
    if not origin:
        return  # Non-browser clients must still meet session + CSRF checks.
    from urllib.parse import urlsplit
    origin_parts = urlsplit(origin)
    if origin_parts.path or origin_parts.query or origin_parts.fragment:
        raise HTTPException(403, detail="Untrusted request origin.")
    expected = str(request.base_url).rstrip("/")
    configured = request.app.state.settings.allowed_origins
    if origin != expected and origin not in configured:
        raise HTTPException(403, detail="Untrusted request origin.")


def require_json(request: Request) -> None:
    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
        raise HTTPException(415, detail="This endpoint requires application/json.")


def throttle_login(path, email: str, ip: str) -> None:
    email_hash = hash_token(email.lower().strip())
    ip_hash = hash_token(ip)
    now = int(time.time())
    with connection(path, write=True) as db:
        db.execute("DELETE FROM login_attempts WHERE occurred_at<?", (now - 900,))
        count = db.execute("""SELECT COUNT(*) AS n FROM login_attempts
             WHERE occurred_at>? AND (identifier_hash=? OR ip_hash=?)""", (now - 900, email_hash, ip_hash)).fetchone()["n"]
        if count >= 8:
            raise HTTPException(429, detail="Too many login attempts. Please try again in 15 minutes.")


def record_login_failure(path, email: str, ip: str) -> None:
    with connection(path, write=True) as db:
        db.execute("INSERT INTO login_attempts(identifier_hash,ip_hash,occurred_at) VALUES (?,?,?)",
                   (hash_token(email.lower().strip()), hash_token(ip), int(time.time())))


def clear_login_attempts(path, email: str, ip: str) -> None:
    with connection(path, write=True) as db:
        db.execute("DELETE FROM login_attempts WHERE identifier_hash=? OR ip_hash=?",
                   (hash_token(email.lower().strip()), hash_token(ip)))


def create_session(path, user_id: int) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    with connection(path, write=True) as db:
        db.execute("DELETE FROM sessions WHERE expires_at<?", (int(time.time()),))
        db.execute("INSERT INTO sessions(token_hash,user_id,csrf_token,expires_at) VALUES (?,?,?,?)",
                   (hash_token(token), user_id, csrf, int(time.time()) + SESSION_SECONDS))
    return token, csrf


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
