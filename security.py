"""Cryptographic helpers for downstream educational OIDC issuance."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def secret_hash(value: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(value.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${b64url(salt)}${b64url(derived)}"


def verify_secret(value: str, encoded: str) -> bool:
    algorithm, salt_text, expected_text = encoded.split("$", 2)
    if algorithm != "scrypt":
        return False
    salt = base64.urlsafe_b64decode(salt_text + "==")
    expected = base64.urlsafe_b64decode(expected_text + "==")
    actual = hashlib.scrypt(value.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(actual, expected)


class SigningKey:
    def __init__(self, key_dir: str):
        directory = Path(key_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "oidc-signing.pem"
        if path.exists():
            self.private_key = serialization.load_pem_private_key(
                path.read_bytes(), password=None
            )
        else:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048
            )
            path.write_bytes(self.private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            ))
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
        public = self.private_key.public_key().public_numbers()
        self.kid = digest(str(public.n))[:16]

    def jwk(self) -> dict[str, str]:
        numbers = self.private_key.public_key().public_numbers()
        size = (numbers.n.bit_length() + 7) // 8
        return {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": self.kid,
            "n": b64url(numbers.n.to_bytes(size, "big")),
            "e": b64url(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")),
        }

    def issue(
        self, issuer: str, subject: str, audience: str, claims: dict[str, Any],
        ttl_seconds: int, nonce: str | None = None,
    ) -> str:
        issued = int(time.time())
        payload = {
            "iss": issuer,
            "sub": subject,
            "aud": audience,
            "iat": issued,
            "exp": issued + ttl_seconds,
            **claims,
        }
        if nonce:
            payload["nonce"] = nonce
        return jwt.encode(
            payload, self.private_key, algorithm="RS256",
            headers={"kid": self.kid, "typ": "JWT"},
        )
