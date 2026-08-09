"""Public, dependency-free HTML pages for FastSSO."""
from __future__ import annotations

from urllib.parse import quote


ACCENT = "#0f766e"
FAVICON = "data:image/svg+xml," + quote(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#0f766e"/><path d="M8 10.5h16M8 16h11M8 21.5h16" stroke="white" stroke-width="3" stroke-linecap="round"/><circle cx="22" cy="16" r="3" fill="#99f6e4"/></svg>""",
    safe="",
)

BASE_CSS = """
:root{--accent:#0f766e;--accent-dark:#115e59;--tint:#f0fdfa;--ink:#10231f;--muted:#5f6f6b;--line:#dce7e4;--paper:#fff;--warn:#fff8e6}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit}.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:12px;z-index:20;background:#fff;padding:10px 14px;border:2px solid var(--accent);border-radius:8px}
.nav{height:70px;display:flex;align-items:center;gap:28px;max-width:1180px;margin:auto;padding:0 24px;border-bottom:1px solid var(--line)}.brand{display:flex;align-items:center;gap:10px;margin-right:auto;color:var(--ink);text-decoration:none;font-weight:780;letter-spacing:-.02em}.mark{width:32px;height:32px;border-radius:10px;background:var(--accent);display:grid;place-items:center;color:#fff;font-size:14px}.nav-links{display:flex;align-items:center;gap:24px}.nav-link{color:var(--muted);font-size:14px;font-weight:650;text-decoration:none}.nav-link:hover,.nav-link:focus{color:var(--accent)}
.button{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:11px 18px;text-decoration:none;font-size:14px;font-weight:720;border:1px solid transparent}.button.primary{background:var(--accent);color:#fff}.button.primary:hover{background:var(--accent-dark)}.button.secondary{border-color:var(--line);background:#fff;color:var(--ink)}
.kicker{display:block;color:var(--accent);font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.16em}.hero{max-width:1180px;margin:auto;padding:94px 24px 82px;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(360px,.9fr);gap:72px;align-items:center}.hero h1{font-size:clamp(44px,6.4vw,76px);line-height:1.01;letter-spacing:-.055em;margin:20px 0 24px;max-width:790px}.lede{font-size:19px;line-height:1.7;color:var(--muted);max-width:720px;margin:0}.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}.micro{font-size:12px;color:var(--muted);margin-top:18px}
.broker{border:1px solid var(--line);border-radius:24px;padding:22px;background:linear-gradient(150deg,#fff 25%,var(--tint));box-shadow:0 28px 75px rgba(15,118,110,.12)}.broker-label{display:flex;align-items:center;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:18px}.live-dot{display:inline-flex;align-items:center;gap:6px}.live-dot:before{content:"";width:7px;height:7px;background:#eab308;border-radius:50%}.flow{display:grid;gap:12px}.flow-node{padding:15px 16px;background:#fff;border:1px solid var(--line);border-radius:14px}.flow-node strong{display:block;font-size:14px}.flow-node span{display:block;color:var(--muted);font-size:12px;margin-top:4px}.flow-arrow{text-align:center;color:var(--accent);font-weight:800}.broker-core{border-color:#5eead4;background:#f0fdfa}.protocols{display:flex;gap:7px;flex-wrap:wrap;margin-top:16px}.chip{padding:6px 9px;border-radius:999px;background:#fff;border:1px solid var(--line);font-size:11px;font-weight:700;color:var(--accent-dark)}
.band{background:var(--tint);border-block:1px solid #c9eee7}.feature-grid{max-width:1180px;margin:auto;padding:68px 24px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:rgba(255,255,255,.9);border:1px solid #cce7e2;border-radius:20px;padding:26px}.card .number{color:var(--accent);font-size:12px;font-weight:800}.card h2,.card h3{letter-spacing:-.02em;margin:22px 0 9px}.card h2{font-size:21px}.card p{color:var(--muted);line-height:1.65;margin:0}
.section{max-width:1180px;margin:auto;padding:82px 24px}.section-heading{max-width:760px}.section h2{font-size:clamp(30px,4vw,44px);letter-spacing:-.04em;margin:14px 0}.section-heading>p{font-size:17px;line-height:1.7;color:var(--muted)}.integration-card{display:grid;grid-template-columns:.8fr 1.2fr;gap:34px;margin-top:34px;border:1px solid var(--line);border-radius:24px;padding:32px;background:#fff;box-shadow:0 18px 55px rgba(16,35,31,.06)}.partner-name{font-size:34px;font-weight:820;letter-spacing:-.04em}.partner-tag{display:inline-block;margin-top:10px;color:var(--accent);font-size:11px;font-weight:800;letter-spacing:.13em;text-transform:uppercase}.integration-card p{color:var(--muted);line-height:1.65}.mini-flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:9px;align-items:center;margin:18px 0 25px}.mini-flow span{background:var(--tint);border:1px solid #c9eee7;border-radius:10px;padding:12px 9px;text-align:center;font-size:12px;font-weight:700}.mini-flow b{color:var(--accent)}
.security{background:#10231f;color:#fff}.security-inner{max-width:1180px;margin:auto;padding:76px 24px;display:grid;grid-template-columns:.8fr 1.2fr;gap:70px}.security .kicker{color:#5eead4}.security h2{font-size:40px;letter-spacing:-.04em;margin:14px 0}.security p{color:#bcd0ca;line-height:1.7}.check-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.check{padding:17px;border:1px solid #31504a;border-radius:14px;color:#d7e6e1;font-size:13px}.check:before{content:"✓";color:#5eead4;font-weight:800;margin-right:9px}.dev{display:grid;grid-template-columns:1fr auto;align-items:center;gap:40px}.link-row{display:flex;gap:18px;flex-wrap:wrap;margin-top:20px}.text-link{color:var(--accent);font-weight:720;text-decoration:none}.text-link:hover{text-decoration:underline}.footer{max-width:1180px;margin:auto;padding:30px 24px 50px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-size:13px}
@media(max-width:860px){.nav-links .nav-link:nth-child(-n+3){display:none}.hero,.integration-card,.security-inner{grid-template-columns:1fr}.hero{padding-top:68px}.broker{max-width:560px}.feature-grid{grid-template-columns:1fr}.security-inner{gap:28px}.dev{grid-template-columns:1fr}}
@media(max-width:560px){.nav{padding:0 16px}.nav-links{gap:10px}.nav-links .button{padding:9px 13px}.hero,.section{padding-left:18px;padding-right:18px}.hero h1{font-size:43px}.mini-flow{grid-template-columns:1fr}.mini-flow b{transform:rotate(90deg);text-align:center}.check-grid{grid-template-columns:1fr}.footer{flex-direction:column}.integration-card{padding:22px}}
"""

GUIDE_CSS = """
.guide-shell{max-width:1180px;margin:auto;padding:56px 24px 90px;display:grid;grid-template-columns:240px minmax(0,760px);gap:66px}.toc{position:sticky;top:28px;align-self:start;border:1px solid var(--line);border-radius:16px;padding:18px}.toc strong{display:block;margin-bottom:10px}.toc a{display:block;color:var(--muted);font-size:13px;text-decoration:none;padding:7px 0}.toc a:hover{color:var(--accent)}.guide h1{font-size:clamp(40px,6vw,64px);letter-spacing:-.05em;line-height:1.04;margin:18px 0}.guide h2{font-size:29px;letter-spacing:-.035em;margin:58px 0 16px;scroll-margin-top:24px}.guide h3{font-size:19px;margin:28px 0 10px}.guide p,.guide li{color:var(--muted);line-height:1.72}.guide li+li{margin-top:7px}.status{background:var(--warn);border:1px solid #f1d899;border-radius:14px;padding:16px 18px;margin:28px 0;color:#69521e;line-height:1.55}.diagram{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center;gap:9px;margin:24px 0}.diagram div{background:var(--tint);border:1px solid #c9eee7;border-radius:12px;padding:18px 10px;text-align:center}.diagram strong{display:block}.diagram span{display:block;color:var(--muted);font-size:11px;margin-top:5px}.diagram b{color:var(--accent)}table{border-collapse:collapse;width:100%;margin:20px 0;font-size:14px}th,td{padding:13px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.55}th{color:var(--ink);font-size:12px;text-transform:uppercase;letter-spacing:.06em}td{color:var(--muted)}code{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;background:#eef4f2;border-radius:5px;padding:2px 5px;color:#164e46}pre{overflow:auto;background:#10231f;color:#dcfce7;padding:20px;border-radius:14px;line-height:1.55}pre code{background:transparent;color:inherit;padding:0}.callout{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:24px 0}.source-list a{color:var(--accent)}
@media(max-width:820px){.guide-shell{grid-template-columns:1fr}.toc{position:static}.diagram{grid-template-columns:1fr}.diagram b{transform:rotate(90deg);text-align:center}.guide-shell{gap:30px}}
"""


def _head(title: str, description: str, extra_css: str = "") -> str:
    return f"""<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{description}">
<link rel="icon" href="{FAVICON}"><link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap">
<style>{BASE_CSS}{extra_css}</style></head>"""


def _nav() -> str:
    return """<a class="skip" href="#content">Skip to content</a><nav class="nav" aria-label="Primary">
<a class="brand" href="/"><span class="mark">FS</span><span>FastSSO</span></a>
<div class="nav-links"><a class="nav-link" href="/#product">Product</a><a class="nav-link" href="/#security">Security</a>
<a class="nav-link" href="/#integrations">Integrations</a><a class="nav-link" href="/docs">API</a>
<a class="button secondary" href="/admin">Sign In</a></div></nav>"""


def _footer() -> str:
    return """<footer class="footer"><span>FastSSO is an educational, open-source FastSME project.</span>
<span><a href="https://fastsme.com/products">FastSME products</a> · <a href="https://github.com/predictivelabsai/FastSSO">Source code</a></span></footer>"""


def landing_page() -> str:
    """Render the anonymous FastSSO product landing page."""
    return f"""<!doctype html><html lang="en">{_head(
        "FastSSO · Enterprise identity connection broker",
        "Connect applications once to tenant-specific enterprise identity providers through a stable OIDC contract.",
    )}<body>{_nav()}<main id="content">
<section class="hero"><div><span class="kicker">Enterprise identity connections</span>
<h1>One sign-on contract. Every customer’s identity provider.</h1>
<p class="lede">FastSSO gives independent applications one standards-first OIDC boundary while each customer brings SAASPASS, Okta, Entra, Google Workspace, or another SAML/OIDC provider.</p>
<div class="actions"><a class="button primary" href="/integrations/saaspass">Read the SAASPASS guide</a><a class="button secondary" href="/docs">Explore the API</a></div>
<p class="micro">Educational release · downstream OIDC runs today · unfinished upstream authentication fails closed</p></div>
<div class="broker" aria-label="FastSSO connection flow"><div class="broker-label"><span>Identity route</span><span class="live-dot">Guarded preview</span></div>
<div class="flow"><div class="flow-node"><strong>Customer identity</strong><span>SAASPASS · Okta · Entra · SAML/OIDC</span></div><div class="flow-arrow">↓</div>
<div class="flow-node broker-core"><strong>FastSSO broker</strong><span>Discovery · normalization · audit boundary</span></div><div class="flow-arrow">↓</div>
<div class="flow-node"><strong>Your application</strong><span>Authorization Code + S256 PKCE</span></div></div>
<div class="protocols"><span class="chip">OIDC</span><span class="chip">SAML 2.0</span><span class="chip">SCIM-shaped</span><span class="chip">Tenant-aware</span></div></div></section>
<section class="band" id="product"><div class="feature-grid">
<article class="card"><span class="number">01</span><h2>Integrate once</h2><p>Applications use one discoverable OIDC issuer instead of owning a different enterprise protocol integration for every customer.</p></article>
<article class="card"><span class="number">02</span><h2>Keep tenants separate</h2><p>Verified domains select tenant-scoped connections. Exact redirect allowlists and normalized subjects preserve the trust boundary.</p></article>
<article class="card"><span class="number">03</span><h2>See what is unfinished</h2><p>Security-sensitive adapters remain explicit HTTP 501 responses until validation, replay protection, and conformance tests are complete.</p></article>
</div></section>
<section class="section" id="integrations"><div class="section-heading"><span class="kicker">Integration guide</span><h2>Start with SAASPASS.</h2><p>Use SAASPASS for workforce authentication and MFA, then let FastSSO normalize that identity into the same downstream contract every Fast* application can consume.</p></div>
<article class="integration-card"><div><div class="partner-name">SAASPASS</div><span class="partner-tag">Proposed upstream OIDC partner</span><p>SAASPASS documents Generic OIDC, Authorization Code, PKCE, signed ID tokens, UserInfo, SAML, and REST integration options.</p><a class="text-link" href="https://saaspass.com/" target="_blank" rel="noopener noreferrer">Visit SAASPASS ↗</a></div>
<div><div class="mini-flow"><span>SAASPASS<br>MFA + identity</span><b>→</b><span>FastSSO<br>validation + mapping</span><b>→</b><span>Fast* app<br>OIDC + PKCE</span></div>
<p>The recommended first implementation is tenant-scoped Generic OIDC. It keeps SAASPASS credentials and tokens behind the adapter boundary while FastSSO emits stable claims such as <code>sub</code>, <code>email</code>, <code>organization_id</code>, and <code>connection_id</code>.</p>
<a class="button primary" href="/integrations/saaspass">Open the deep-dive guide</a></div></article></section>
<section class="security" id="security"><div class="security-inner"><div><span class="kicker">Built around the trust boundary</span><h2>Secure by being explicit.</h2><p>FastSSO is not a password store or authorization engine. It brokers authentication and leaves application policy with the application.</p></div>
<div class="check-grid"><div class="check">Exact registered callback matching</div><div class="check">Mandatory downstream S256 PKCE</div><div class="check">Tenant-scoped identity mapping</div><div class="check">Redacted admin connection data</div><div class="check">Short-lived, one-time codes</div><div class="check">Fail-closed unfinished adapters</div></div></div></section>
<section class="section dev"><div><span class="kicker">For developers</span><h2>A small, inspectable protocol surface.</h2><p class="lede">Use discovery and mature OIDC clients, review the threat model, and test locally with deterministic synthetic identities.</p><div class="link-row"><a class="text-link" href="/.well-known/openid-configuration">OIDC discovery →</a><a class="text-link" href="/docs">OpenAPI →</a><a class="text-link" href="/api/v1/provider-presets">Provider presets →</a></div></div><a class="button secondary" href="https://github.com/predictivelabsai/FastSSO">View source ↗</a></section>
</main>{_footer()}</body></html>"""


def saaspass_guide_page() -> str:
    """Render the SAASPASS-to-FastSSO integration design guide."""
    return f"""<!doctype html><html lang="en">{_head(
        "SAASPASS integration guide · FastSSO",
        "A security-first implementation guide for connecting SAASPASS to FastSSO with Generic OpenID Connect.",
        GUIDE_CSS,
    )}<body>{_nav()}<main id="content" class="guide-shell">
<aside class="toc" aria-label="On this page"><strong>On this page</strong><a href="#decision">Architecture decision</a><a href="#setup">Configuration</a><a href="#flow">Authentication flow</a><a href="#claims">Claim mapping</a><a href="#validation">Validation gates</a><a href="#lifecycle">Lifecycle options</a><a href="#rollout">Rollout plan</a><a href="#sources">Sources</a></aside>
<article class="guide"><span class="kicker">Integration guide · reviewed 9 August 2026</span><h1>Connect SAASPASS to FastSSO.</h1>
<p class="lede">The cleanest boundary is SAASPASS as the upstream workforce identity provider and FastSSO as the broker that presents one stable OIDC contract to independent applications.</p>
<div class="status"><strong>Design status:</strong> review-ready, not live. FastSSO’s upstream OIDC callback is intentionally unimplemented. The adapter must continue to fail closed until metadata, token validation, replay handling, and conformance fixtures pass.</div>

<h2 id="decision">1. Architecture decision</h2><p>Use a tenant-specific <strong>Generic OIDC</strong> application in the SAASPASS Admin Portal. SAASPASS performs workforce authentication and MFA. FastSSO validates the returned identity, binds it to the selected organization and connection, and issues a separate downstream authorization code to the requesting application.</p>
<div class="diagram"><div><strong>SAASPASS</strong><span>Upstream IdP + MFA</span></div><b>→</b><div><strong>FastSSO</strong><span>OIDC RP + identity broker</span></div><b>→</b><div><strong>Application</strong><span>OIDC client + authorization</span></div></div>
<p>This split avoids passing SAASPASS access or ID tokens to applications. It also means applications never need a SAASPASS client secret and remain independent of the provider chosen by another tenant.</p>
<table><thead><tr><th>System</th><th>Owns</th><th>Must not own</th></tr></thead><tbody><tr><td>SAASPASS</td><td>User authentication, MFA method, workforce assignment</td><td>Fast* application authorization policy</td></tr><tr><td>FastSSO</td><td>Tenant routing, upstream token validation, identity normalization, downstream code issuance</td><td>Passwords or business permissions</td></tr><tr><td>Application</td><td>Session, roles, permissions, local deprovisioning response</td><td>SAASPASS tokens or tenant IdP credentials</td></tr></tbody></table>

<h2 id="setup">2. Configuration</h2><h3>In SAASPASS</h3><ol><li>Create or select the customer company and add a <strong>Generic OIDC</strong> application.</li><li>Register the exact planned callback: <code>https://&lt;fastsso-host&gt;/oidc/&lt;connection_id&gt;/callback</code>. Do not use wildcards.</li><li>Select Authorization Code; enable its PKCE variant if the tenant supports it. Request only <code>openid email profile</code>.</li><li>Assign a small pilot group. Record the App Key (client ID), App Password, expected issuer value, and the application-specific signing public key shown in the Developers tab.</li><li>Confirm key-rotation procedure, supported signing algorithms, nonce behavior, and production issuer with SAASPASS before enabling traffic.</li></ol>
<h3>In FastSSO</h3><p>Create a tenant-scoped connection using the <code>saaspass</code> preset. Store the secret outside source control and encrypt it at rest before production.</p>
<pre><code>{{
  "provider": "saaspass",
  "protocol": "oidc",
  "issuer": "&lt;exact iss claim confirmed by SAASPASS&gt;",
  "client_id": "&lt;SAASPASS App Key&gt;",
  "client_secret": "&lt;secret-manager reference&gt;",
  "signing_public_key": "&lt;pinned application public key&gt;",
  "authorization_endpoint": "https://www.saaspass.com/sd/oauth/authorize",
  "token_endpoint": "https://www.saaspass.com/sd/oauth/token",
  "userinfo_endpoint": "https://www.saaspass.com/sd/oauth/userinfo",
  "scopes": ["openid", "email", "profile"]
}}</code></pre>
<div class="callout"><p><strong>Metadata caveat.</strong> The public SAASPASS reference documents endpoints and an application-specific public key, but does not expose a JWKS URI in that reference. Its example issuer uses <code>http://www.saaspass.com</code> even though protocol calls use HTTPS. Treat neither value as an assumption: capture a test token, confirm the exact <code>iss</code>, obtain the key through an authenticated admin channel, and pin both in the connection.</p></div>

<h2 id="flow">3. Authentication flow</h2><ol><li>The application sends a normal downstream request to FastSSO with <code>state</code>, <code>nonce</code>, and an S256 PKCE challenge.</li><li>FastSSO validates the client and exact redirect URI, discovers the organization from the verified email domain, and selects its SAASPASS connection.</li><li>FastSSO creates a one-time upstream transaction containing organization, connection, downstream request, random state, nonce, and a separate PKCE verifier.</li><li>The browser goes to SAASPASS <code>/sd/oauth/authorize</code> for authentication and MFA.</li><li>The callback rejects missing/mismatched state, errors, expired transactions, or a reused transaction before exchanging the code server-to-server at <code>/sd/oauth/token</code>.</li><li>FastSSO validates the ID token and maps the identity. Only then does it issue its own short-lived downstream code and resume the application flow.</li></ol>
<p>SAASPASS documents <code>code_challenge_method=SHA-256</code>; the standards value is normally <code>S256</code>. Verify the accepted wire value in an isolated tenant and add it as an interoperability fixture instead of silently trying both in production.</p>

<h2 id="claims">4. Claim mapping and account linking</h2><table><thead><tr><th>SAASPASS input</th><th>FastSSO output</th><th>Policy</th></tr></thead><tbody><tr><td><code>sub</code></td><td>Stored as upstream subject</td><td>Primary immutable link within this connection</td></tr><tr><td><code>email</code></td><td><code>email</code></td><td>Require the verified SAASPASS email and a verified tenant domain</td></tr><tr><td><code>name</code>, <code>given_name</code>, <code>family_name</code></td><td>Normalized profile claims</td><td>Optional; absence must not fail authentication</td></tr><tr><td><code>saaspass_id</code></td><td>Private adapter metadata</td><td>Do not expose downstream unless a documented need exists</td></tr><tr><td>SAASPASS assignments/groups</td><td><code>groups</code></td><td>No mapping until an authoritative supported claim/API is confirmed</td></tr><tr><td>Connection context</td><td><code>organization_id</code>, <code>connection_id</code></td><td>Set by FastSSO, never trusted from upstream claims</td></tr></tbody></table>
<p>Use the tuple <code>(connection_id, upstream sub)</code> as the durable identity key. Email is routing and profile data, not the sole account-linking key; SAASPASS notes that a user may have multiple profiles.</p>

<h2 id="validation">5. Non-negotiable validation gates</h2><ul><li>Allowlist the HTTPS SAASPASS hosts and block redirects or metadata fetches to private/link-local networks.</li><li>Validate ID-token signature with the pinned tenant/application key; reject algorithm changes, unknown <code>kid</code>, and unsigned tokens. FastSSO must not follow the vendor reference’s suggestion that signature checking may be optional.</li><li>Validate exact issuer, client ID audience, expiry, issued-at bounds, subject, and nonce when supported. Require an explicit reviewed fallback if SAASPASS cannot round-trip nonce.</li><li>Consume state, authorization code, token <code>jti</code>, and transaction identifiers once. Keep raw codes and tokens out of logs, database diagnostics, audit metadata, and error responses.</li><li>Use strict timeouts, response-size limits, TLS verification, <code>application/x-www-form-urlencoded</code> token requests, and <code>no-store</code> handling.</li><li>Add fixtures for wrong issuer/audience/key, expired token, replay, state mismatch, missing email, multi-profile subjects, PKCE mismatch, and upstream error responses.</li></ul>

<h2 id="lifecycle">6. Lifecycle and alternative channels</h2><p>SAASPASS also documents SAML, its HTTP API, application/company-scoped tokens, OTP checks, and dynamic client registration. These are separate phases:</p><ul><li><strong>SAML:</strong> useful for tenants standardized on SAML, but only after FastSSO’s hardened SAML acceptance checklist is complete.</li><li><strong>HTTP account APIs:</strong> assess for assignment and deprovisioning only after clarifying whether they provide the lifecycle semantics FastSSO needs. Do not treat generic REST account operations as SCIM.</li><li><strong>Dynamic client registration:</strong> avoid initially. Manual, reviewed per-tenant registration has a smaller blast radius; DCR introduces a high-value bearer credential.</li><li><strong>OTP/widgets/custom SSO callback:</strong> not the preferred broker boundary because they add proprietary flows and can weaken the clean OIDC validation model.</li></ul>

<h2 id="rollout">7. Rollout plan</h2><ol><li><strong>Contract capture:</strong> obtain a non-production tenant, public signing key, sample tokens, issuer confirmation, PKCE/nonce behavior, error catalogue, and key-rotation procedure.</li><li><strong>Adapter:</strong> implement an OIDC client behind <code>providers/</code> with encrypted credentials and transactional one-time state.</li><li><strong>Adversarial tests:</strong> pass malicious and conformance fixtures before replacing HTTP 501.</li><li><strong>Pilot:</strong> one organization, one verified domain, one assigned group, short sessions, and a tested break-glass rollback.</li><li><strong>Operate:</strong> monitor only redacted event types and identifiers; document credential rotation, tenant offboarding, and incident revocation.</li></ol>

<h2 id="sources">Official sources</h2><ul class="source-list"><li><a href="https://developer.saaspass.com/" target="_blank" rel="noopener noreferrer">SAASPASS API Reference</a> — Generic OIDC, PKCE, token, UserInfo, public-key validation, REST services, and DCR.</li><li><a href="https://saaspass.com/" target="_blank" rel="noopener noreferrer">SAASPASS product site</a> — product and company overview.</li><li><a href="/docs">FastSSO OpenAPI</a>, <a href="https://github.com/predictivelabsai/FastSSO/blob/main/docs/THREAT_MODEL.md">threat model</a>, and <a href="https://github.com/predictivelabsai/FastSSO/blob/main/docs/ARCHITECTURE.md">architecture</a> — broker contracts and release gates.</li></ul>
<p class="micro">Vendor capabilities and documentation can change. Re-verify the authenticated SAASPASS Admin Portal configuration and live protocol metadata during implementation.</p>
</article></main>{_footer()}</body></html>"""
