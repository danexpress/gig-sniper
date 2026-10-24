import sqlite3
from contextlib import contextmanager

import config
from models import Gig

SCHEMA = """
CREATE TABLE IF NOT EXISTS gigs (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT,
    url TEXT NOT NULL,
    description TEXT,
    rate TEXT,
    remote BOOLEAN,
    posted_at TEXT,
    fetched_at TEXT NOT NULL,
    score INTEGER,
    score_reason TEXT,
    pitch TEXT,
    notified BOOLEAN NOT NULL DEFAULT 0
);
"""


@contextmanager
def connect(db_path: str | None = None):
    conn = sqlite3.connect(db_path or config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str | None = None):
    with connect(db_path) as conn:
        conn.execute(SCHEMA)


def exists(conn, gig_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM gigs WHERE id = ?", (gig_id,)).fetchone()
    return row is not None


def insert_gig(conn, gig: Gig):
    conn.execute(
        """
        INSERT OR IGNORE INTO gigs
        (id, source, title, company, url, description, rate, remote,
         posted_at, fetched_at, score, score_reason, pitch, notified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            gig.id, gig.source, gig.title, gig.company, gig.url, gig.description,
            gig.rate, gig.remote, gig.posted_at, gig.fetched_at,
            gig.score, gig.score_reason, gig.pitch, gig.notified,
        ),
    )


def get_pending_digest(conn, threshold: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM gigs WHERE notified = 0 AND score >= ? ORDER BY score DESC",
        (threshold,),
    ).fetchall()
    return [dict(r) for r in rows]


def mark_notified(conn, gig_ids: list[str]):
    if not gig_ids:
        return
    conn.executemany("UPDATE gigs SET notified = 1 WHERE id = ?", [(i,) for i in gig_ids])
