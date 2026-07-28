"""Provider-neutral configuration presets.

Live protocol adapters will implement the same normalized identity boundary.
This module intentionally performs configuration validation only.
"""
from __future__ import annotations

from typing import Any

PRESETS: dict[str, dict[str, Any]] = {
    "generic-saml": {
        "name": "Generic SAML 2.0",
        "protocol": "saml",
        "required": ["idp_entity_id", "sso_url", "signing_certificate"],
        "tested": False,
    },
    "okta": {
        "name": "Okta Workforce",
        "protocol": "saml",
        "required": ["metadata_url"],
        "tested": False,
    },
    "entra": {
        "name": "Microsoft Entra ID",
        "protocol": "saml",
        "required": ["metadata_url"],
        "tested": False,
    },
    "google-workspace": {
        "name": "Google Workspace",
        "protocol": "saml",
        "required": ["metadata_xml"],
        "tested": False,
    },
    "generic-oidc": {
        "name": "Generic OpenID Connect",
        "protocol": "oidc",
        "required": ["issuer", "client_id", "client_secret"],
        "tested": False,
    },
}


def public_presets() -> list[dict[str, Any]]:
    return [{"id": key, **value} for key, value in PRESETS.items()]


def validate_connection_config(provider: str, config: dict[str, Any]) -> list[str]:
    preset = PRESETS.get(provider)
    if not preset:
        return [f"Unknown provider preset: {provider}"]
    return [
        f"Missing required setting: {field}"
        for field in preset["required"]
        if not str(config.get(field, "")).strip()
    ]
