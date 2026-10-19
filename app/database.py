"""Parameterized SQLite access and idempotent schema initialization."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL CHECK(length(name) BETWEEN 2 AND 80),
  email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('student','staff','admin')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  csrf_token TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_sessions_expiry ON sessions(expires_at);
CREATE TABLE IF NOT EXISTS login_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  identifier_hash TEXT NOT NULL,
  ip_hash TEXT NOT NULL,
  occurred_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_attempts_lookup ON login_attempts(identifier_hash,ip_hash,occurred_at);
CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ref TEXT NOT NULL UNIQUE,
  creator_id INTEGER NOT NULL REFERENCES users(id),
  assignee_id INTEGER REFERENCES users(id),
  title TEXT NOT NULL CHECK(length(title) BETWEEN 8 AND 120),
  description TEXT NOT NULL CHECK(length(description) BETWEEN 20 AND 2000),
  location TEXT NOT NULL CHECK(length(location) BETWEEN 3 AND 120),
  category TEXT NOT NULL CHECK(category IN ('Facilities','IT','Safety','Academic','Transport')),
  priority TEXT NOT NULL CHECK(priority IN ('Low','Medium','High')),
  status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','In Progress','Resolved','Reopened')),
  ai_category TEXT NOT NULL,
  ai_confidence REAL NOT NULL CHECK(ai_confidence >= 0 AND ai_confidence <= 1),
  ai_priority TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_tickets_created ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_tickets_creator ON tickets(creator_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_tickets_status ON tickets(status);
CREATE TABLE IF NOT EXISTS ticket_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  actor_id INTEGER NOT NULL REFERENCES users(id),
  event_type TEXT NOT NULL CHECK(event_type IN ('created','status','assigned','comment')),
  from_status TEXT,
  to_status TEXT,
  note TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_events_ticket ON ticket_events(ticket_id,id);
"""


def connect(path: Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), timeout=20, isolation_level=None, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=20000")
    return db


@contextmanager
def connection(path: Path, write: bool = False):
    db = connect(path)
    try:
        if write:
            db.execute("BEGIN IMMEDIATE")
        yield db
        if write:
            db.commit()
    except Exception:
        if write:
            db.rollback()
        raise
    finally:
        db.close()


def init_database(path: Path) -> None:
    with connection(path) as db:
        db.executescript(SCHEMA)
        db.execute("PRAGMA journal_mode=WAL")
