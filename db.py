"""SQLite persistence for FastSSO's educational control and protocol planes."""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

DB_PATH = os.getenv("FASTSSO_DB", str(Path(__file__).with_name("fastsso.sqlite")))

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS applications (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    client_id TEXT NOT NULL UNIQUE,
    client_secret_hash TEXT NOT NULL,
    redirect_uris TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS domains (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    domain TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending','verified')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS connections (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    protocol TEXT NOT NULL CHECK(protocol IN ('saml','oidc')),
    provider TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('draft','active','disabled')),
    config TEXT NOT NULL,
    jit_provisioning INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS identities (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    connection_id TEXT NOT NULL REFERENCES connections(id),
    upstream_subject TEXT NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    claims TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    UNIQUE(connection_id, upstream_subject)
);
CREATE TABLE IF NOT EXISTS authorization_codes (
    code_hash TEXT PRIMARY KEY,
    application_id TEXT NOT NULL REFERENCES applications(id),
    identity_id TEXT NOT NULL REFERENCES identities(id),
    redirect_uri TEXT NOT NULL,
    scope TEXT NOT NULL,
    nonce TEXT,
    code_challenge TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    consumed_at INTEGER
);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    organization_id TEXT,
    target_id TEXT,
    detail TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(UTC).isoformat()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple[Any, ...] = ()) -> None:
    with connect() as conn:
        conn.execute(sql, params)


def audit(
    event_type: str,
    actor: str,
    organization_id: str | None = None,
    target_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    # Protocol payloads, assertions, tokens, secrets, and raw claims do not
    # belong in this table. Callers must provide a deliberately small detail.
    execute(
        """INSERT INTO audit_events
           (event_type, actor, organization_id, target_id, detail, occurred_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event_type, actor, organization_id, target_id,
         json.dumps(detail or {}, sort_keys=True), now()),
    )


def parse_json(row: dict[str, Any], *fields: str) -> dict[str, Any]:
    copy = dict(row)
    for field in fields:
        copy[field] = json.loads(copy[field])
    return copy
