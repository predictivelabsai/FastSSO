from __future__ import annotations

import base64
import hashlib
import json
from urllib.parse import parse_qs, urlparse

import jwt
from fastapi.testclient import TestClient

import db
from api_app import ADMIN_TOKEN, BASE_URL, app, signing_key
from seed import seed


def challenge(verifier: str) -> str:
    return base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()


def client(tmp_path) -> TestClient:
    db.DB_PATH = str(tmp_path / "test.sqlite")
    seed()
    return TestClient(app)


def test_public_landing_admin_and_saaspass_guide(tmp_path):
    with client(tmp_path) as browser:
        landing = browser.get("/")
        assert landing.status_code == 200
        assert "One sign-on contract" in landing.text
        assert 'href="/integrations/saaspass"' in landing.text
        assert 'href="/admin"' in landing.text
        assert "Organizations</h2>" not in landing.text

        admin = browser.get("/admin")
        assert admin.status_code == 200
        assert "Organizations</h2>" in admin.text

        guide = browser.get("/integrations/saaspass")
        assert guide.status_code == 200
        assert "Connect SAASPASS to FastSSO" in guide.text
        assert "review-ready, not live" in guide.text
        assert "signing_public_key" in guide.text

        presets = browser.get("/api/v1/provider-presets").json()["data"]
        assert any(
            preset["id"] == "saaspass" and preset["tested"] is False
            for preset in presets
        )


def test_discovery_and_scim_capability(tmp_path):
    with client(tmp_path) as browser:
        discovery = browser.get("/.well-known/openid-configuration")
        assert discovery.status_code == 200
        assert discovery.json()["issuer"] == BASE_URL
        assert discovery.json()["code_challenge_methods_supported"] == ["S256"]
        assert browser.get("/.well-known/jwks.json").json()["keys"][0]["alg"] == "RS256"

        scim = browser.get("/scim/v2/ServiceProviderConfig")
        assert scim.status_code == 200
        assert scim.json()["patch"]["supported"] is False
        assert browser.get("/scim/v2/Users").status_code == 501


def test_domain_discovery_and_admin_redaction(tmp_path):
    with client(tmp_path) as browser:
        result = browser.get(
            "/api/v1/discovery", params={"email": "ada@acme.example"}
        ).json()
        assert result["match"] is True
        assert result["connection"]["organization_id"] == "org_acme"

        assert browser.get("/api/v1/admin/connections").status_code == 401
        response = browser.get(
            "/api/v1/admin/connections",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
        assert response.status_code == 200
        assert response.json()["data"][0]["config"] == {"redacted": True}


def test_authorization_code_pkce_round_trip_and_one_time_use(tmp_path):
    verifier = "correct-horse-battery-staple-verifier-1234567890"
    with client(tmp_path) as browser:
        authorize = browser.get(
            "/oauth2/authorize",
            params={
                "client_id": "fastcrm-demo",
                "redirect_uri": "http://localhost:5006/auth/fastsso/callback",
                "response_type": "code",
                "scope": "openid profile email groups",
                "state": "application-state",
                "nonce": "application-nonce",
                "code_challenge": challenge(verifier),
                "code_challenge_method": "S256",
                "login_hint": "ada@acme.example",
            },
            follow_redirects=False,
        )
        assert authorize.status_code == 302
        query = parse_qs(urlparse(authorize.headers["location"]).query)
        assert query["state"] == ["application-state"]
        code = query["code"][0]

        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:5006/auth/fastsso/callback",
            "client_id": "fastcrm-demo",
            "client_secret": "fastcrm-demo-secret",
            "code_verifier": verifier,
        }
        token = browser.post("/oauth2/token", data=form)
        assert token.status_code == 200
        payload = token.json()
        claims = jwt.decode(
            payload["id_token"],
            signing_key.private_key.public_key(),
            algorithms=["RS256"],
            audience="fastcrm-demo",
            issuer=BASE_URL,
        )
        assert claims["email"] == "ada@acme.example"
        assert claims["organization_id"] == "org_acme"
        assert claims["nonce"] == "application-nonce"

        userinfo = browser.get(
            "/oauth2/userinfo",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )
        assert userinfo.status_code == 200
        assert userinfo.json()["groups"] == ["engineering", "admins"]

        replay = browser.post("/oauth2/token", data=form)
        assert replay.status_code == 400
        assert replay.json()["error"] == "invalid_grant"


def test_redirect_uri_and_pkce_are_strict(tmp_path):
    with client(tmp_path) as browser:
        bad_redirect = browser.get(
            "/oauth2/authorize",
            params={
                "client_id": "fastcrm-demo",
                "redirect_uri": "http://localhost:5006.evil.test/callback",
                "response_type": "code",
                "scope": "openid",
                "state": "state",
                "code_challenge": "x" * 43,
                "code_challenge_method": "S256",
                "login_hint": "ada@acme.example",
            },
            follow_redirects=False,
        )
        assert bad_redirect.status_code == 400
        assert bad_redirect.json()["error"] == "invalid_request"

        weak_pkce = browser.get(
            "/oauth2/authorize",
            params={
                "client_id": "fastcrm-demo",
                "redirect_uri": "http://localhost:5006/auth/fastsso/callback",
                "response_type": "code",
                "scope": "openid",
                "state": "state",
                "code_challenge": "plaintext",
                "code_challenge_method": "plain",
                "login_hint": "ada@acme.example",
            },
            follow_redirects=False,
        )
        assert weak_pkce.status_code == 302
        assert "error=invalid_request" in weak_pkce.headers["location"]
