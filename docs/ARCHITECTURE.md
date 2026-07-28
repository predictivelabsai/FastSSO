# Architecture

FastSSO is a narrow enterprise connection broker. It separates the protocol
used by a customer's identity provider from the protocol used by an
application.

```text
                        FastSSO
              ┌────────────────────────┐
Enterprise    │ upstream adapters      │
IdP ─────────▶│ SAML SP │ OIDC RP      │
              ├────────────────────────┤
              │ organization discovery │
              │ normalized identity    │
              │ audit and lifecycle    │
              ├────────────────────────┤
Application ◀─│ OIDC OP │ REST facade  │
              └────────────────────────┘
```

## Components

- `api_app.py` is the public protocol surface and small HTML control plane.
- `db.py` owns persistence and audit records.
- `security.py` owns downstream key material, hashing, PKCE helpers, and token
  issuance.
- `providers/` contains upstream provider presets and will hold protocol
  adapters. Adapters must return a normalized identity rather than expose raw
  assertions or provider tokens.
- `seed.py` creates a deterministic mock organization and identity.
- `examples/` contains optional, dependency-free sister-app sketches.

## Stable downstream contract

OIDC is canonical because applications can use mature clients and discovery.
Only Authorization Code with PKCE is supported. The convenience REST endpoint
is an alternate facade over the same future broker transaction, not a second
identity model.

Downstream claims are:

```json
{
  "sub": "broker identity ID",
  "email": "user@example.com",
  "email_verified": true,
  "name": "User Name",
  "given_name": "User",
  "family_name": "Name",
  "groups": ["engineering"],
  "organization_id": "org_example",
  "connection_id": "conn_example"
}
```

Applications remain responsible for authorization. A group claim is input to
an application's policy; FastSSO does not decide what that group may do.

## Trust and tenancy

An organization may have verified domains and multiple upstream connections.
Discovery resolves a verified domain to a connection. Connection credentials
and signing certificates are tenant-scoped. Application redirect URIs are
exact allowlists.

SQLite is the educational default. Persistence functions form a deliberately
small seam for a later PostgreSQL implementation. Short-lived broker state
(authorization requests, replay identifiers, and codes) should move to a
transactional database or Redis before production use.

## Current execution boundary

The synthetic `educational_mock` connection skips an upstream redirect so the
downstream OIDC integration can be exercised. It only recognizes a seeded,
synthetic identity. Other upstream connections and every SCIM mutation return
HTTP 501. This makes incompleteness observable and fail-closed.

## Extension rules

1. Do not parse SAML with generic XML traversal. Use a maintained SAML library,
   hardened local schemas, pinned trust material, and adversarial fixtures.
2. Never log raw assertions, authorization codes, access/ID tokens, client
   secrets, or unfiltered claims.
3. Keep upstream tokens behind the adapter boundary.
4. Add conformance tests before changing a stub to an implemented endpoint.
5. Keep sister-product adapters optional; FastSSO must remain independently
   deployable.
