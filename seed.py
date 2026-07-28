"""Create deterministic synthetic FastSSO tenants and connections."""
from __future__ import annotations

import json
from pathlib import Path

import db
from security import secret_hash


def seed() -> None:
    db.init_schema()
    with db.connect() as conn:
        for table in (
            "authorization_codes", "audit_events", "identities", "connections",
            "domains", "organizations", "applications",
        ):
            conn.execute(f"DELETE FROM {table}")
        conn.execute(
            """INSERT INTO applications
               (id,name,client_id,client_secret_hash,redirect_uris,active,created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (
                "app_fastcrm", "FastCRM demo", "fastcrm-demo",
                secret_hash("fastcrm-demo-secret"),
                json.dumps(["http://localhost:5006/auth/fastsso/callback"]),
                1, db.now(),
            ),
        )
        conn.execute(
            "INSERT INTO organizations (id,name,slug,created_at) VALUES (?,?,?,?)",
            ("org_acme", "Acme Manufacturing", "acme", db.now()),
        )
        conn.execute(
            """INSERT INTO domains
               (id,organization_id,domain,status,created_at) VALUES (?,?,?,?,?)""",
            ("dom_acme", "org_acme", "acme.example", "verified", db.now()),
        )
        conn.execute(
            """INSERT INTO connections
               (id,organization_id,name,protocol,provider,status,config,
                jit_provisioning,created_at) VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                "conn_acme_mock", "org_acme", "Acme educational OIDC",
                "oidc", "generic-oidc", "active",
                json.dumps({
                    "issuer": "https://mock-idp.invalid",
                    "client_id": "not-a-real-client",
                    "mode": "educational_mock",
                }),
                1, db.now(),
            ),
        )
        conn.execute(
            """INSERT INTO identities
               (id,organization_id,connection_id,upstream_subject,email,
                display_name,claims,active,created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                "usr_ada", "org_acme", "conn_acme_mock", "mock|ada",
                "ada@acme.example", "Ada Lovelace",
                json.dumps({
                    "email_verified": True,
                    "given_name": "Ada",
                    "family_name": "Lovelace",
                    "groups": ["engineering", "admins"],
                }),
                1, db.now(),
            ),
        )
    db.audit("seed.completed", "system", detail={"synthetic": True})


if __name__ == "__main__":
    seed()
    print(f"Seeded synthetic FastSSO data at {Path(db.DB_PATH).resolve()}")
