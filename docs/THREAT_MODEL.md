# Threat model

FastSSO sits on an authentication trust boundary. This document describes the
minimum review required before an educational stub is promoted to live code.

## Assets

- Upstream IdP credentials and signing certificates.
- FastSSO signing private keys.
- Authorization codes, sessions, and replay identifiers.
- User identifiers, attributes, and group membership.
- Organization/domain routing configuration.
- Application client credentials and redirect URI registrations.

## Primary threats and required controls

| Threat | Required control |
|---|---|
| SAML XML signature wrapping | Hardened library, schema validation before use, exact signed-element selection, malicious fixture tests |
| Forged or misrouted assertion | Validate signature, issuer, destination, audience, recipient, subject confirmation, and connection |
| Assertion replay | One-time request/assertion ID store with bounded expiry |
| OIDC code injection or interception | `state`, `nonce`, Authorization Code flow, mandatory S256 PKCE, exact callback |
| Token substitution | Verify issuer, audience, signature algorithm, key ID, expiry, nonce, and subject |
| Tenant confusion | Resolve organization and connection before consuming identity; include tenant in every lookup |
| Domain takeover | DNS or application-authorized verification; globally unique normalized domains |
| Open redirect | Exact registered URI comparison; never prefix or wildcard comparison |
| Secret disclosure | Encryption at rest, external secret manager option, redacted APIs and logs |
| Key compromise | Separate signing/encryption keys, rotation, key IDs, expiry monitoring, incident revocation |
| Account linking takeover | Require verified email plus explicit tenant policy; prefer immutable upstream subject |
| Enumeration | Uniform unauthenticated discovery policy and rate limiting |
| SCIM cross-tenant write | Per-directory bearer credential, tenant-scoped lookup, filtering limits, idempotency and audit |
| Deprovisioning race | Transactional disable, session revocation policy, ordered/idempotent SCIM events |

## SAML acceptance checklist

The ACS must remain disabled until it has tests proving:

- XML external entities and remote schemas are disabled.
- A locally trusted schema validates before any security-relevant selection.
- Only configured IdP keys are trusted; assertion `KeyInfo` cannot override
  local trust.
- Response and/or assertion signatures follow an explicit connection policy.
- `InResponseTo`, destination, audience, recipient, issuer, time conditions,
  and subject confirmation are checked.
- Request IDs and assertion IDs cannot be reused.
- Clock skew is bounded and configurable.
- SHA-1 and insecure canonicalization/signature algorithms are rejected.
- Encrypted assertions use a separate, protected key.
- IdP-initiated login is off by default.

Reference: [OWASP SAML Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html).

## Operational work before production

- External security review.
- OIDC conformance suite.
- SAML interoperability matrix and malicious assertion corpus.
- PostgreSQL plus shared replay/session storage.
- Envelope encryption or managed KMS.
- TLS/proxy configuration, secure admin authentication, CSRF protection,
  rate limiting, monitoring, backups, and tested key rotation.
