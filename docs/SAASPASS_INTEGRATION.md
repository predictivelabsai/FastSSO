# SAASPASS integration guide

> **Status:** design only. FastSSO's upstream OIDC adapter is not live. Keep
> the callback fail-closed until the validation and conformance gates below
> pass. This guide was reviewed against the public SAASPASS documentation on
> 9 August 2026.

## Recommended architecture

Configure SAASPASS as a tenant-scoped upstream OpenID Connect identity
provider. SAASPASS authenticates the workforce user and applies MFA. FastSSO
validates and normalizes that identity, then completes its separate downstream
OIDC Authorization Code + PKCE flow for the application.

```text
SAASPASS                 FastSSO                         Application
upstream IdP + MFA  -->  OIDC RP / identity broker  --> OIDC client + policy
```

Never forward SAASPASS tokens to an application. Applications should receive
only FastSSO-issued tokens and remain responsible for their own authorization.

## SAASPASS configuration

1. Add a **Generic OIDC** application in the customer's SAASPASS company.
2. Register the exact callback
   `https://<fastsso-host>/oidc/<connection_id>/callback`; do not use a
   wildcard.
3. Use Authorization Code and enable its PKCE variant if supported for the
   tenant. Request only `openid email profile`.
4. Assign a small pilot group.
5. Record the App Key, App Password, expected issuer, and the
   application-specific signing public key from the Developers tab.
6. Confirm signing algorithms, nonce behavior, key rotation, and the exact
   production issuer with SAASPASS.

The planned FastSSO connection shape is:

```json
{
  "provider": "saaspass",
  "protocol": "oidc",
  "issuer": "<exact iss claim confirmed by SAASPASS>",
  "client_id": "<SAASPASS App Key>",
  "client_secret": "<secret-manager reference>",
  "signing_public_key": "<pinned application public key>",
  "authorization_endpoint": "https://www.saaspass.com/sd/oauth/authorize",
  "token_endpoint": "https://www.saaspass.com/sd/oauth/token",
  "userinfo_endpoint": "https://www.saaspass.com/sd/oauth/userinfo",
  "scopes": ["openid", "email", "profile"]
}
```

The public reference does not publish a JWKS URI and shows an HTTP issuer in
its token-validation example despite using HTTPS endpoints. Do not guess.
Capture a non-production token, confirm its exact `iss`, obtain the public key
through an authenticated admin channel, and pin both to the tenant connection.

## Broker flow

1. Validate the downstream client, exact redirect URI, `state`, `nonce`, and
   S256 PKCE request.
2. Resolve the verified email domain to its organization and SAASPASS
   connection.
3. Store a one-time upstream transaction containing that tenant context,
   random state, nonce, and a separate PKCE verifier.
4. Redirect to SAASPASS `/sd/oauth/authorize`.
5. On callback, consume and validate state before exchanging the code
   server-to-server at `/sd/oauth/token`.
6. Validate the signed ID token, normalize the identity, and only then issue
   FastSSO's downstream authorization code.

SAASPASS documents `code_challenge_method=SHA-256`, while the standard wire
value is normally `S256`. Verify the accepted value in the test tenant and
capture it in an interoperability fixture; do not silently retry variants in
production.

## Claim mapping

| SAASPASS input | FastSSO treatment |
|---|---|
| `sub` | Store as the upstream subject; link by `(connection_id, sub)` |
| `email` | Require verified email and a verified tenant domain |
| `name`, `given_name`, `family_name` | Normalize when present; all are optional |
| `saaspass_id` | Keep as private adapter metadata unless explicitly required |
| groups/assignments | Do not map until an authoritative claim or API is confirmed |
| tenant context | Set `organization_id` and `connection_id` inside FastSSO |

Email must not be the only durable account key. SAASPASS documents that one
user may have multiple profiles, potentially with the same email.

## Security and conformance gates

- Allowlist HTTPS upstream hosts; block private/link-local metadata targets and
  unsafe redirects.
- Always verify the ID-token signature with the pinned key. Reject unexpected
  algorithms, unknown key IDs, and unsigned tokens even if vendor examples
  describe signature verification as optional.
- Validate exact issuer, client-ID audience, expiry, issued-at bounds, subject,
  and nonce when supported. Any nonce limitation needs an explicit review.
- Consume transaction state, authorization code, and token `jti` once.
- Never log raw codes, tokens, secrets, public/private key material, or
  unfiltered claims.
- Enforce TLS verification, strict timeouts, response-size limits, and
  `no-store` handling.
- Test wrong issuer/audience/key, expiry, replay, state and PKCE mismatch,
  missing email, multiple profiles, and upstream errors.

## Lifecycle and alternatives

SAASPASS also documents SAML, proprietary HTTP account APIs, OTP/widgets, and
dynamic client registration (DCR). Treat these as separate phases:

- Enable SAML only after FastSSO's hardened SAML acceptance checklist passes.
- Do not call general account-management REST operations “SCIM” without
  confirmed SCIM semantics and deprovisioning behavior.
- Prefer manually reviewed client registration initially. DCR adds a
  high-value bearer credential and wider provisioning authority.
- Avoid proprietary OTP/widget flows for the broker boundary when OIDC is
  available.

## Rollout

1. Capture a non-production contract: sample tokens, signing key, issuer,
   PKCE/nonce behavior, errors, and rotation procedure.
2. Implement the adapter in `providers/` with encrypted credentials and
   transactional one-time state.
3. Pass malicious and conformance fixtures before replacing HTTP 501.
4. Pilot one organization, domain, application, and small SAASPASS group with
   short sessions and a tested rollback.
5. Document credential rotation, tenant offboarding, and incident revocation;
   monitor only redacted events and identifiers.

## Official references

- [SAASPASS API Reference](https://developer.saaspass.com/): Generic OIDC,
  Authorization Code, PKCE, token and UserInfo endpoints, public-key
  validation, REST services, and DCR.
- [SAASPASS](https://saaspass.com/): product overview.
- [FastSSO threat model](THREAT_MODEL.md) and
  [architecture](ARCHITECTURE.md): local trust boundaries and release gates.

Vendor behavior can change. Re-verify the authenticated SAASPASS Admin Portal
and live protocol metadata during implementation.
