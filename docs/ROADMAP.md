# Roadmap

## 0.1 — executable educational foundation

- [x] Multi-tenant schema and synthetic seed.
- [x] Downstream OIDC discovery, code + PKCE, JWKS, token, and userinfo.
- [x] REST session-exchange contract.
- [x] Generic/provider preset registry.
- [x] SAML metadata/ACS endpoint shapes.
- [x] SCIM capability and resource endpoint shapes.
- [x] Optional sister-app integration sketch.
- [x] Architecture, threat model, comparison, tests, and Docker.

## 0.2 — live upstream OIDC

- [ ] Discovery with SSRF-safe issuer policy.
- [ ] Authorization transaction storage and callback.
- [ ] State, nonce, PKCE, signature, issuer, and audience validation.
- [ ] UserInfo policy and normalized claim mapper.
- [ ] Client secret encryption and rotation.
- [ ] Google, Entra, Okta, and generic interoperability fixtures.

## 0.3 — live upstream SAML

- [ ] Select and audit maintained SAML implementation.
- [ ] Metadata import with hardened XML and explicit trust review.
- [ ] Signed AuthnRequest and ACS validation.
- [ ] Replay cache and bounded clock skew.
- [ ] Encrypted assertion support with separate keys.
- [ ] Okta, Entra, Google Workspace, and generic setup guides.
- [ ] Malicious assertion corpus and interoperability tests.

## 0.4 — SCIM provisioning

- [ ] Per-directory bearer tokens stored as hashes.
- [ ] RFC 7643 User and Group schemas.
- [ ] RFC 7644 filtering, pagination, PATCH, and error envelopes.
- [ ] Idempotent create/update/disable semantics.
- [ ] Group membership and deprovisioning events.
- [ ] Okta and Entra test suites.

## Production-readiness gate

PostgreSQL, shared replay storage, envelope encryption/KMS, admin SSO and
authorization, CSRF and rate limits, webhook signatures, key rotation,
conformance suites, deployment guides, observability, backups, and an external
security assessment.
