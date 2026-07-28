"""FastSSO educational enterprise connection broker."""
from __future__ import annotations

import html
import json
import os
import secrets
import time
from contextlib import asynccontextmanager
from urllib.parse import urlencode, urlparse

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, Field

import db
from providers import public_presets
from security import SigningKey, b64url, digest, verify_secret

load_dotenv()

BASE_URL = os.getenv("FASTSSO_BASE_URL", "http://localhost:5015").rstrip("/")
KEY_DIR = os.getenv("FASTSSO_KEY_DIR", ".keys")
ADMIN_TOKEN = os.getenv("FASTSSO_ADMIN_TOKEN", "change-me")
CODE_TTL = int(os.getenv("FASTSSO_CODE_TTL_SECONDS", "300"))
TOKEN_TTL = int(os.getenv("FASTSSO_TOKEN_TTL_SECONDS", "3600"))
signing_key = SigningKey(KEY_DIR)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_schema()
    if not db.one("SELECT id FROM applications LIMIT 1"):
        from seed import seed
        seed()
    yield


app = FastAPI(
    title="FastSSO",
    version="0.1.0",
    description=(
        "Educational, provider-neutral enterprise SSO broker. The downstream "
        "OIDC demo is executable; upstream SAML/OIDC and SCIM mutations fail "
        "closed until their validators are implemented."
    ),
    license_info={"name": "MIT"},
    lifespan=lifespan,
)


def admin_auth(authorization: str | None = Header(default=None)) -> None:
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(401, "Admin bearer token required")


def unimplemented(feature: str) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "error": "not_implemented",
            "feature": feature,
            "educational_status": True,
            "message": (
                "This security-sensitive contract is documented but disabled "
                "until validation and conformance tests are complete."
            ),
        },
    )


def oidc_error(error: str, description: str, status: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": error, "error_description": description},
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )


def esc(value: object) -> str:
    return html.escape(str(value))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    apps = db.rows("SELECT name,client_id,redirect_uris,active FROM applications")
    orgs = db.rows(
        """SELECT o.id,o.name,o.slug,COUNT(DISTINCT d.id) domains,
                  COUNT(DISTINCT c.id) connections
           FROM organizations o
           LEFT JOIN domains d ON d.organization_id=o.id
           LEFT JOIN connections c ON c.organization_id=o.id
           GROUP BY o.id ORDER BY o.name"""
    )
    connections = db.rows(
        """SELECT c.name,c.protocol,c.provider,c.status,o.name organization
           FROM connections c JOIN organizations o ON o.id=c.organization_id
           ORDER BY o.name,c.name"""
    )
    events = db.rows(
        "SELECT event_type,actor,occurred_at FROM audit_events ORDER BY id DESC LIMIT 8"
    )
    rows = lambda values: "".join(
        "<tr>" + "".join(f"<td>{esc(v)}</td>" for v in row.values()) + "</tr>"
        for row in values
    )
    return f"""<!doctype html><html><head><title>FastSSO</title>
<style>
body{{font:15px system-ui;margin:0;background:#f5f7fb;color:#172033}}
header{{background:#111b36;color:white;padding:28px 5vw}}
main{{max-width:1100px;margin:28px auto;padding:0 22px}}
.warning{{background:#fff4ce;border:1px solid #e5bd44;padding:14px;border-radius:8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}}
section{{background:white;padding:20px;border:1px solid #dde3ef;border-radius:10px}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:9px;border-bottom:1px solid #edf0f5;text-align:left}}
code{{background:#edf1f7;padding:2px 5px;border-radius:4px}}a{{color:#3157c8}}
</style></head><body>
<header><h1>FastSSO</h1><p>Enterprise connection broker · control plane</p></header>
<main><p class="warning"><strong>Educational release.</strong> Live upstream
authentication and SCIM mutations are disabled. The seeded connection is a
clearly labelled mock used to exercise the downstream OIDC contract.</p>
<div class="grid">
<section><h2>Organizations</h2><table><tr><th>ID</th><th>Name</th><th>Slug</th><th>Domains</th><th>Connections</th></tr>{rows(orgs)}</table></section>
<section><h2>Applications</h2><table><tr><th>Name</th><th>Client ID</th><th>Redirect URIs</th><th>Active</th></tr>{rows(apps)}</table></section>
<section><h2>Connections</h2><table><tr><th>Name</th><th>Protocol</th><th>Provider</th><th>Status</th><th>Organization</th></tr>{rows(connections)}</table></section>
<section><h2>Recent audit events</h2><table><tr><th>Event</th><th>Actor</th><th>Time</th></tr>{rows(events)}</table></section>
</div><p><a href="/docs">OpenAPI</a> ·
<a href="/.well-known/openid-configuration">OIDC discovery</a> ·
<a href="/api/v1/provider-presets">provider presets</a> ·
<a href="/scim/v2/ServiceProviderConfig">SCIM capability</a></p>
</main></body></html>"""


@app.get("/health", tags=["System"])
def health() -> dict:
    return {
        "status": "ok",
        "version": app.version,
        "educational": True,
        "upstream_protocols_live": False,
    }


@app.get("/.well-known/openid-configuration", tags=["OIDC provider"])
def discovery() -> dict:
    return {
        "issuer": BASE_URL,
        "authorization_endpoint": f"{BASE_URL}/oauth2/authorize",
        "token_endpoint": f"{BASE_URL}/oauth2/token",
        "userinfo_endpoint": f"{BASE_URL}/oauth2/userinfo",
        "jwks_uri": f"{BASE_URL}/.well-known/jwks.json",
        "revocation_endpoint": f"{BASE_URL}/oauth2/revoke",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["openid", "profile", "email", "groups"],
        "claims_supported": [
            "iss", "sub", "aud", "exp", "iat", "nonce", "email",
            "email_verified", "name", "given_name", "family_name",
            "groups", "organization_id", "connection_id",
        ],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
    }


@app.get("/.well-known/jwks.json", tags=["OIDC provider"])
def jwks() -> dict:
    return {"keys": [signing_key.jwk()]}


@app.get("/oauth2/authorize", tags=["OIDC provider"])
def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: str,
    nonce: str | None = None,
    login_hint: str | None = Query(default=None),
) -> Response:
    application = db.one(
        "SELECT * FROM applications WHERE client_id=? AND active=1", (client_id,)
    )
    if not application:
        return oidc_error("unauthorized_client", "Unknown or disabled client")
    if redirect_uri not in json.loads(application["redirect_uris"]):
        return oidc_error("invalid_request", "redirect_uri is not registered")
    if response_type != "code":
        params = urlencode({"error": "unsupported_response_type", "state": state})
        return RedirectResponse(f"{redirect_uri}?{params}", status_code=302)
    if "openid" not in scope.split():
        params = urlencode({"error": "invalid_scope", "state": state})
        return RedirectResponse(f"{redirect_uri}?{params}", status_code=302)
    if code_challenge_method != "S256" or len(code_challenge) < 43:
        params = urlencode({
            "error": "invalid_request", "error_description": "S256 PKCE required",
            "state": state,
        })
        return RedirectResponse(f"{redirect_uri}?{params}", status_code=302)
    if not login_hint or "@" not in login_hint:
        return oidc_error(
            "interaction_required",
            "The educational flow requires login_hint for domain discovery",
        )
    domain = login_hint.rsplit("@", 1)[1].lower()
    connection = db.one(
        """SELECT c.*,d.organization_id FROM domains d
           JOIN connections c ON c.organization_id=d.organization_id
           WHERE lower(d.domain)=? AND d.status='verified' AND c.status='active'
           ORDER BY c.id LIMIT 1""",
        (domain,),
    )
    if not connection:
        return oidc_error("access_denied", "No active connection for this domain")
    config = json.loads(connection["config"])
    if config.get("mode") != "educational_mock":
        return unimplemented(f"upstream_{connection['protocol']}_authentication")
    identity = db.one(
        """SELECT * FROM identities
           WHERE connection_id=? AND lower(email)=? AND active=1""",
        (connection["id"], login_hint.lower()),
    )
    if not identity:
        return oidc_error("access_denied", "Mock identity is not seeded")
    raw_code = secrets.token_urlsafe(32)
    db.execute(
        """INSERT INTO authorization_codes
           (code_hash,application_id,identity_id,redirect_uri,scope,nonce,
            code_challenge,expires_at,consumed_at)
           VALUES (?,?,?,?,?,?,?,?,NULL)""",
        (
            digest(raw_code), application["id"], identity["id"], redirect_uri,
            scope, nonce, code_challenge, int(time.time()) + CODE_TTL,
        ),
    )
    db.audit(
        "oidc.authorization_code.issued", "educational-mock",
        connection["organization_id"], application["id"],
        {"client_id": client_id, "scope": scope.split()},
    )
    params = urlencode({"code": raw_code, "state": state})
    return RedirectResponse(f"{redirect_uri}?{params}", status_code=302)


@app.post("/oauth2/token", tags=["OIDC provider"])
def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code_verifier: str = Form(...),
) -> Response:
    if grant_type != "authorization_code":
        return oidc_error("unsupported_grant_type", "Only authorization_code is supported")
    application = db.one(
        "SELECT * FROM applications WHERE client_id=? AND active=1", (client_id,)
    )
    if not application or not verify_secret(
        client_secret, application["client_secret_hash"]
    ):
        return oidc_error("invalid_client", "Client authentication failed", 401)
    record = db.one(
        """SELECT ac.*,i.organization_id,i.connection_id,i.email,i.display_name,
                  i.claims,i.active identity_active
           FROM authorization_codes ac
           JOIN identities i ON i.id=ac.identity_id
           WHERE ac.code_hash=?""",
        (digest(code),),
    )
    if (
        not record or record["consumed_at"] is not None
        or record["expires_at"] < int(time.time())
        or record["application_id"] != application["id"]
        or record["redirect_uri"] != redirect_uri
        or not record["identity_active"]
    ):
        return oidc_error("invalid_grant", "Authorization code is invalid or expired")
    challenge = b64url(__import__("hashlib").sha256(code_verifier.encode()).digest())
    if not secrets.compare_digest(challenge, record["code_challenge"]):
        return oidc_error("invalid_grant", "PKCE verification failed")
    # Atomic consume prevents a second successful exchange.
    with db.connect() as conn:
        changed = conn.execute(
            """UPDATE authorization_codes SET consumed_at=?
               WHERE code_hash=? AND consumed_at IS NULL""",
            (int(time.time()), digest(code)),
        ).rowcount
    if changed != 1:
        return oidc_error("invalid_grant", "Authorization code was already consumed")
    upstream = json.loads(record["claims"])
    claims = {
        "email": record["email"],
        "email_verified": bool(upstream.get("email_verified", False)),
        "name": record["display_name"],
        "given_name": upstream.get("given_name"),
        "family_name": upstream.get("family_name"),
        "groups": upstream.get("groups", []),
        "organization_id": record["organization_id"],
        "connection_id": record["connection_id"],
    }
    token_value = signing_key.issue(
        BASE_URL, record["identity_id"], client_id, claims, TOKEN_TTL, record["nonce"]
    )
    db.audit(
        "oidc.token.issued", "token-endpoint", record["organization_id"],
        application["id"], {"client_id": client_id},
    )
    return JSONResponse(
        {
            "access_token": token_value,
            "token_type": "Bearer",
            "expires_in": TOKEN_TTL,
            "id_token": token_value,
            "scope": record["scope"],
        },
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )


def bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer token required")
    return authorization[7:]


@app.get("/oauth2/userinfo", tags=["OIDC provider"])
def userinfo(value: str = Depends(bearer_token)) -> dict:
    import jwt
    try:
        claims = jwt.decode(
            value, signing_key.private_key.public_key(), algorithms=["RS256"],
            issuer=BASE_URL, options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Invalid access token") from exc
    return {
        key: claims[key] for key in (
            "sub", "email", "email_verified", "name", "given_name",
            "family_name", "groups", "organization_id", "connection_id",
        ) if key in claims
    }


@app.post("/oauth2/revoke", tags=["OIDC provider"])
def revoke() -> Response:
    # JWT access tokens are short-lived and not persisted in this release.
    return Response(status_code=200)


@app.get("/api/v1/provider-presets", tags=["Public API"])
def provider_presets() -> dict:
    return {"data": public_presets()}


@app.get("/api/v1/discovery", tags=["Public API"])
def domain_discovery(email: str) -> dict:
    if "@" not in email:
        raise HTTPException(422, "A complete email address is required")
    domain = email.rsplit("@", 1)[1].lower()
    found = db.one(
        """SELECT o.id organization_id,o.name organization_name,c.id connection_id,
                  c.protocol,c.provider
           FROM domains d JOIN organizations o ON o.id=d.organization_id
           JOIN connections c ON c.organization_id=o.id
           WHERE lower(d.domain)=? AND d.status='verified' AND c.status='active'
           ORDER BY c.id LIMIT 1""",
        (domain,),
    )
    # Production deployments should use a uniform response or authenticated
    # discovery policy to avoid revealing customer enrollment.
    return {"match": bool(found), "connection": found}


class SessionExchange(BaseModel):
    protocol: str = Field(pattern="^(saml|oidc)$")
    assertion_or_code: str
    application_id: str


@app.post("/api/v1/sessions/exchange", tags=["Public API"])
def session_exchange(_request: SessionExchange) -> Response:
    return unimplemented("rest_session_exchange")


@app.get("/api/v1/admin/organizations", dependencies=[Depends(admin_auth)], tags=["Admin API"])
def admin_organizations() -> dict:
    return {"data": db.rows("SELECT * FROM organizations ORDER BY name")}


@app.get("/api/v1/admin/connections", dependencies=[Depends(admin_auth)], tags=["Admin API"])
def admin_connections() -> dict:
    records = db.rows("SELECT * FROM connections ORDER BY created_at")
    for record in records:
        record["config"] = {"redacted": True}
    return {"data": records}


@app.get("/saml/{connection_id}/metadata", tags=["SAML service provider"])
def saml_metadata(connection_id: str) -> Response:
    connection = db.one(
        "SELECT * FROM connections WHERE id=? AND protocol='saml'", (connection_id,)
    )
    if not connection:
        raise HTTPException(404, "SAML connection not found")
    entity = f"{BASE_URL}/saml/{connection_id}/metadata"
    acs = f"{BASE_URL}/saml/{connection_id}/acs"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
 entityID="{html.escape(entity)}">
 <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true"
  protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
  <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
  <md:AssertionConsumerService
   Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
   Location="{html.escape(acs)}" index="0" isDefault="true"/>
 </md:SPSSODescriptor>
</md:EntityDescriptor>"""
    return Response(xml, media_type="application/samlmetadata+xml")


@app.post("/saml/{connection_id}/acs", tags=["SAML service provider"])
def saml_acs(connection_id: str) -> Response:
    return unimplemented(f"saml_assertion_consumer:{connection_id}")


SCIM_URN = "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"


@app.get("/scim/v2/ServiceProviderConfig", tags=["SCIM"])
def scim_config() -> dict:
    return {
        "schemas": [SCIM_URN],
        "patch": {"supported": False},
        "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
        "filter": {"supported": False, "maxResults": 0},
        "changePassword": {"supported": False},
        "sort": {"supported": False},
        "etag": {"supported": False},
        "authenticationSchemes": [{
            "type": "oauthbearertoken",
            "name": "Bearer token (planned)",
            "description": "Not accepted by the educational stub.",
            "specUri": "https://www.rfc-editor.org/rfc/rfc6750",
            "primary": True,
        }],
        "documentationUri": f"{BASE_URL}/docs",
    }


@app.get("/scim/v2/Schemas", tags=["SCIM"])
def scim_schemas() -> Response:
    return unimplemented("scim_schemas")


@app.get("/scim/v2/ResourceTypes", tags=["SCIM"])
def scim_resource_types() -> Response:
    return unimplemented("scim_resource_types")


@app.api_route(
    "/scim/v2/Users{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    tags=["SCIM"],
)
def scim_users(path: str = "") -> Response:
    return unimplemented(f"scim_users{path}")


@app.api_route(
    "/scim/v2/Groups{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    tags=["SCIM"],
)
def scim_groups(path: str = "") -> Response:
    return unimplemented(f"scim_groups{path}")
