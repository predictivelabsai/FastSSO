"""Optional FastHTML-style integration sketch for any FastCo sister app.

This is deliberately not imported by FastSSO or by a sister repository.
Use Authlib (or another maintained OIDC client) in a real integration.
"""

FASTSSO_ISSUER = "http://localhost:5015"
CLIENT_ID = "fastcrm-demo"
CALLBACK_URL = "http://localhost:5006/auth/fastsso/callback"


def normalized_session_claims(id_token_claims: dict) -> dict:
    """Map FastSSO's stable OIDC claims to an application session."""
    return {
        "user_id": id_token_claims["sub"],
        "email": id_token_claims["email"],
        "name": id_token_claims.get("name"),
        "organization_id": id_token_claims["organization_id"],
        "groups": id_token_claims.get("groups", []),
        "auth_source": "fastsso",
    }
