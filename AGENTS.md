# Repository Guidelines

## Scope

FastSSO is an educational enterprise SSO broker, not a password store or
authorization engine. Keep it independent from FastCo sister applications;
integration examples must remain optional.

## Structure

`api_app.py` owns HTTP/OIDC/SCIM endpoint contracts, `db.py` persistence,
`security.py` downstream crypto helpers, `providers/` upstream adapters and
presets, `seed.py` synthetic fixtures, `docs/` architecture/security notes,
and `tests/` contract and security-invariant tests.

## Security rules

Never log assertions, tokens, authorization codes, secrets, private keys, or
unfiltered claims. Security-sensitive unfinished behavior must fail closed
with an explicit 501. Do not implement SAML parsing from raw XML helpers.
Follow `docs/THREAT_MODEL.md`, use maintained protocol libraries, and add
malicious/conformance fixtures before enabling an endpoint.

## Development

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.sample .env
.venv/bin/python seed.py
.venv/bin/uvicorn api_app:app --port 5015
.venv/bin/python -m pytest -q
```

Use Python 3.12, type hints, parameterized SQL, concise docstrings, and
deterministic synthetic data. Never commit `.env`, SQLite databases, or keys.
