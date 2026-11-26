import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import UUID

from .models import Session

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sessions.sqlite3"


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY, repository TEXT NOT NULL,
            task TEXT NOT NULL, status TEXT NOT NULL
        )""")
        db.commit()


def save(session: Session):
    with closing(sqlite3.connect(DB_PATH)) as db:
        db.execute(
            "INSERT INTO sessions (id, repository, task, status) VALUES (?, ?, ?, ?)",
            (str(session.id), session.repository, session.task, session.status),
        )
        db.commit()


def find(session_id: UUID) -> Session | None:
    with closing(sqlite3.connect(DB_PATH)) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM sessions WHERE id = ?", (str(session_id),)).fetchone()
    return Session(**dict(row)) if row is not None else None
