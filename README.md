# FastSSO

FastSSO is an open-source, self-hostable **enterprise SSO integration broker**.
An application integrates once through OpenID Connect (OIDC) or the small REST
API, while each customer organization can bring a SAML 2.0 or OIDC identity
provider.

FastSSO is deliberately narrower than Clerk, Auth0, Keycloak, or a complete
identity platform. It does not store passwords and it is not an authorization
engine. Its job is to illustrate the integration layer between:

```text
Okta / Entra / Google / generic SAML or OIDC
                         │
                         ▼
                      FastSSO
                         │
                  OIDC or REST API
                         ▼
             your independent application
```

> **Educational status:** the downstream OIDC demo is executable. Upstream
> OIDC/SAML and SCIM surfaces are intentionally visible but incomplete.
> Unimplemented security-sensitive paths fail closed with HTTP 501. Do not use
> this release as a production identity system.

## What is included

- Multi-tenant applications, organizations, verified domains, and connections.
- Provider-neutral connection models with Okta, Microsoft Entra ID, Google
  Workspace, generic SAML, and generic OIDC presets.
- Downstream OIDC discovery, authorization-code + PKCE token exchange, JWKS,
  userinfo, and revocation-shaped endpoints.
- A REST discovery/session contract for applications that do not want OIDC.
- SAML SP metadata and ACS endpoint shapes.
- SCIM 2.0 discovery plus explicit user/group provisioning stubs.
- An admin dashboard, audit events, deterministic synthetic demo data, and
  optional integration examples for any FastCo sister application.
- Architecture, threat model, protocol notes, and incumbent comparison.

See [the SSO provider comparison](docs/sso_provider_comparison.md) for how
FastSSO differs from Clerk, WorkOS, Ory Polis, SuperTokens, Logto, Supabase
Auth, Keycloak, ZITADEL, Authentik, and other incumbents.

## Quickstart

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.sample .env
.venv/bin/python seed.py
.venv/bin/uvicorn api_app:app --host 0.0.0.0 --port 5015
```

Open:

- Product landing page: <http://localhost:5015/>
- Admin dashboard: <http://localhost:5015/admin>
- SAASPASS integration guide: <http://localhost:5015/integrations/saaspass>
- OpenAPI: <http://localhost:5015/docs>
- OIDC discovery: <http://localhost:5015/.well-known/openid-configuration>
- SCIM capabilities: <http://localhost:5015/scim/v2/ServiceProviderConfig>

The seeded confidential client is `fastcrm-demo` /
`fastcrm-demo-secret`. Its redirect URI is
`http://localhost:5006/auth/fastsso/callback`.

## Example OIDC flow

Generate a PKCE verifier and its SHA-256 challenge. Then open:

```text
/oauth2/authorize
  ?client_id=fastcrm-demo
  &redirect_uri=http://localhost:5006/auth/fastsso/callback
  &response_type=code
  &scope=openid%20profile%20email
  &state=application-generated-state
  &nonce=application-generated-nonce
  &code_challenge=BASE64URL_SHA256_VERIFIER
  &code_challenge_method=S256
  &login_hint=ada@acme.example
```

The educational mock connection issues an authorization code. Exchange it at
`POST /oauth2/token` with the original verifier. Real upstream authentication
will replace this mock boundary without changing the downstream contract.

## Integration choices

Applications may use:

1. Standards-first OIDC (recommended).
2. `POST /api/v1/sessions/exchange`, a convenience REST contract currently
   stubbed until upstream assertion exchange is implemented.
3. A reverse-proxy or framework adapter built on either contract.

The examples in `examples/` are optional snippets. FastSSO has no imports from,
database access to, or runtime dependency on FastCRM, FastERP, or another
FastCo product.

For a concrete upstream design, read the
[SAASPASS integration guide](docs/SAASPASS_INTEGRATION.md). It recommends a
tenant-scoped Generic OIDC connection and records the validation and rollout
gates that must pass before the adapter can replace its fail-closed boundary.

## Development

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall api_app.py db.py security.py providers seed.py
docker compose up --build
```

## Deployment

FastSSO is catalogued in the sibling FastDevOps control plane and deploys from
`main` to `https://sso.fastsme.com`. An active push-only GitHub webhook starts
the Coolify deployment automatically. With FastDevOps checked out beside this
repository:

```bash
python scripts/coolify.py status
python scripts/coolify.py env --sync --yes
python scripts/coolify.py deploy --yes
```

Copy `.env.coolify.sample` entries into the ignored `.env`; never commit API
tokens or the FastSSO admin token.

Read [architecture](docs/ARCHITECTURE.md),
[the threat model](docs/THREAT_MODEL.md), and
[the implementation roadmap](docs/ROADMAP.md) before extending protocol code.

## SCIM status

SCIM is included in the API and data model so integrations can be designed
early. `ServiceProviderConfig`, `Schemas`, and `ResourceTypes` advertise the
planned surface. User and Group mutation endpoints return HTTP 501 until
authentication, filtering, pagination, idempotency, and deprovisioning
semantics are implemented and tested.

## License

MIT.
