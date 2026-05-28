# RISKRADAR Expansion — Security Implementation Plan

Executive summary
-----------------
This document translates the expansion threat model into an actionable implementation plan for backend, frontend, and DevOps. It defines mandatory controls, a prioritized checklist, verification steps, owners, and release gates so new travel, collaboration, and assistant features are production-ready and hardened.

Scope
-----
- All new features: events ingestion, routing, itineraries, packing, trip sharing, Golby assistant.
- Sensitive data: `user_health_profile`, sharing tokens, PII, audit logs, backups.
- Integrations: routing providers, event/place/lodging scrapers, LLM providers.

Backfill security coverage for newly planned features
-----------------------------------------------------
- Forecast extensions: lock down provider credentials, validate any new weather fields against provider schemas, and treat forecast enrichment as untrusted external data until normalized. Add tests for cache poisoning, stale data fallback, and missing-field behavior for `uvi`, `dew_point`, `visibility`, `pressure`, and `feels_like`.
- Astronomy and celestial timing: treat sunrise, sunset, moonrise, moonset, moon phase, moon illumination, and special events like supermoons or blood moons as provider-sourced data that must be validated, time-zoned correctly, and cached with freshness metadata.
- Place allergen extraction: treat menus, OCR output, and free-text venue content as hostile input. Sanitize extracted text, run prompt-injection and HTML-scrubbing checks, preserve provenance for every extracted allergen, and require confidence thresholds plus manual-review fallback for ambiguous results.
- Tide and outbreak feeds: require allowlisted providers, source trust tiers, and freshness checks. Outbreak or disease advisories must be clearly labeled as informational, never diagnostic, and any high-impact recommendation must pass clinician-review gating.
- Multimodal routing: protect route-provider calls with hostname allowlists, quotas, and response integrity checks. Sign and version route snapshots, reject malformed legs, and ensure degraded mode is available if the primary provider or an alternative transit feed is unavailable.
- Trip import connectors: imports from ICS, PNR, email, or similar sources must be opt-in, sandboxed, size-limited, and redacted before storage. Strip attachments unless explicitly needed, enforce MIME/type validation, and keep imported PII out of logs and analytics.
- Health- and allergy-linked recommendations: all new health-adjacent features must use `backend/services/health_guardrails.py` before any LLM output is shown. If a backfill feature can surface prescriptive advice, it must expose `{why, confidence, sources[], timestamp}` and `clinician_review_required` when the rule set or confidence threshold requires escalation.

Required controls for all backfill work:
- Data provenance and trust tier on every externally sourced record.
- Strict schema validation and dead-letter quarantine for malformed records.
- Explicit user consent where itinerary import or health data is involved.
- Redaction of health, itinerary, and sharing data in shared/public views.
- Security tests for provider outage, malformed payloads, injection attempts, and permission bypass.

Threat model summary
--------------------
- Account takeover and session compromise
- Broken authorization / IDOR / privilege escalation
- Injection (SQL, HTML, JS), CSRF, SSRF, open-redirects
- Prompt-injection and unsafe LLM outputs
- Data leakage via logs, caches, backups, or third parties
- Supply-chain compromise (dependencies, containers, CI)
- Abuse and DDoS, link-enumeration, scraping
- Malicious/poisoned external data
- Insider misuse and leaked secrets

Governance & program-level controls
----------------------------------
- Security owner: assign a named security champion for the expansion work (must be in sprint 0).
- Living risk register: per-feature STRIDE entries, owners, mitigations, verification date.
- Security gates: no feature promoted beyond canary until critical/high findings are closed.
- Change control: all DB migrations require preflight and backup snapshot.

Implementation priorities (first 8 weeks)
---------------------------------------
1. Phase 0 (Week 1) — Baseline: threat model, owners, CI gates, SBOM, SAST configured.
2. Phase 1 (Weeks 2–4) — Auth & Authorization: RBAC, row-level checks, MFA for privileged users, session rotation.
3. Phase 2 (Weeks 3–6) — Data protection: field-level encryption, backups, secure deletion, redaction.
4. Phase 3 (Weeks 4–8) — API hardening: CORS allowlist, security headers, rate limiting, WAF rules.
5. Phase 4 (Weeks 5–10) — LLM & provider safety: prompt-injection filters, citation checks, human-review gates.
6. Phase 5 (Weeks 6–12) — CI/CD & supply chain: dependency pinning, SBOM, signed builds, DAST, container/IaC scanning.
7. Phase 6 (Weeks 8–14) — Observability & IR: security telemetry, drill runbooks, restore rehearsals, pentest.

Phase-by-Phase Breakdown
------------------------
The following expands each prioritized phase into concrete implementation tasks, file-level touchpoints, verification steps, and recommended owners. Follow these steps in order per sprint and mark the living risk register as each verification completes.

Phase 0 — Baseline (Week 1)
Goals:
- Assign security owner and leads; publish living risk register entry for expansion.
- Configure CI gates and basic scanning (SAST, secret-scan); generate initial SBOM.

Implementation tasks:
- Create `docs/expansion/living_risk_register.yaml` with STRIDE entries and owners.
- Add CI jobs: `ci/sast.yml`, `ci/secret_scan.yml`, and SBOM generation step (e.g., `pip-licenses` or `syft`).
- Add minimal staging DAST scaffold for OWASP ZAP run on staging deploy.

Key files & places:
- `docs/expansion/RISKRADAR_EXPANSION_SECURITYPLAN.md` (this file)
- CI: `.github/workflows/` or `ci/` folder; `pyproject.toml`/`requirements.txt` for SBOM.

Verification:
- CI jobs run and produce reports; SBOM artifact present in CI artifacts.
- Living risk register entry created and assigned.

Risk Controls:
- Gate prevents Phase 1 work from merging to canary until CI scans pass (low/med findings triaged).

Owner: Security owner (TBD), CI engineer.

Phase 1 — Auth & Authorization (Weeks 2–4)
Goals:
- Implement RBAC and row-level authorization; centralize authorization helper and session hardening.

Implementation tasks:
- Add `backend/auth/permissions.py` and central `backend/auth/authorize.py` with `authorize_user_action()` API; refactor handlers in `backend/api/*` to call it.
- Implement session/token changes in `backend/auth/security.py`: short TTLs, refresh-token rotation, persist refresh-token identifiers and revocation list (DB table `refresh_tokens`).
- Add MFA hooks for admin/support flows and step-up flows for high-risk actions.

Key files & places:
- `backend/auth/security.py`, `backend/auth/permissions.py`, `backend/api/router.py`, `backend/db/migrations/` (add `refresh_tokens` table).

Verification:
- Unit tests: `backend/tests/test_security.py` covering token rotation, revocation, and reuse detection.
- Integration tests: simulate refresh rotation, revoked refresh behavior, and step-up flows.

Risk Controls:
- Enforce short TTLs and detection of refresh reuse; log and alert on reuse.

Owner: Backend lead, Security owner.

Phase 2 — Data Protection (Weeks 3–6)
Goals:
- Encrypt sensitive fields, ensure encrypted backups, add secure deletion workflows.

Implementation tasks:
- Add field-level encryption helpers in `backend/db/crypto.py` and integrate with KMS-backed envelope encryption (abstract KMS via `backend/config/kms.py`).
- Mark sensitive columns in `backend/db/models.py` (e.g., `user_health_profile`, `share_token_hash`) and add migration scripts to re-encrypt existing values where needed.
- Implement secure deletion script `tools/secure_delete.py` that removes from DB, cache (Redis), and flags backup purge workflows.

Key files & places:
- `backend/db/crypto.py`, `backend/config/settings.py` (vault/KMS references), DB migrations.

Verification:
- Automated tests that assert encrypted column contents are not plaintext in DB snapshots; restore drill confirms backups decrypt correctly using rotated keys.

Risk Controls:
- KMS key rotation policy and restricted key access; require two-person approval for key rotation in prod.

Owner: DevOps lead, Backend lead.

Phase 3 — API Hardening (Weeks 4–8)
Goals:
- Apply CORS allowlist, security headers, rate limiting, and WAF rules; SSRF protections.

Implementation tasks:
- Add middleware in `backend/main.py`: `SecurityHeadersMiddleware`, `CORSAllowlist`, and `RateLimitMiddleware` (use a pluggable provider, e.g., Redis-backed leaky bucket).
- Harden outbound calls with an `outbound_proxy` layer that enforces hostname allowlist and timeouts; update scrapers to use it.
- Define WAF rule set (Cloud or on-prem) and map OWASP ZAP findings into WAF rules for staging.

Key files & places:
- `backend/main.py`, `backend/middleware/security.py`, `backend/scrapers/*`, `infrastructure/waf/` or IaC templates.

Verification:
- Automated integration tests for CORS, CSP headers, and SSRF attempt rejection; simulate high-rate traffic and confirm rate-limit headers and blocking.

Risk Controls:
- Circuit-breakers on third-party calls; fail closed to degraded safe mode when providers fail.

Owner: Backend lead, DevOps lead.

Phase 4 — LLM & Provider Safety (Weeks 5–10)
Goals:
- Implement guardrails, prompt-safety pipeline, citation enforcement, human-review gating for high-risk outputs.

Implementation tasks:
- Implement `backend/services/health_guardrails.py` with deterministic checks and a `review_queue` interface for flagged outputs.
- Add prompt-safety preprocessor: `backend/llm/pipeline.py` that sanitizes inputs, tokenizes for prompt-injection heuristics, and calls a safety classifier.
- Require `sources[]` and `confidence` from LLM; build caching for sampled outputs and a human-review dashboard (minimal `backend/api/reviews.py`).

Key files & places:
- `backend/services/health_guardrails.py`, `backend/llm/pipeline.py`, `backend/api/reviews.py`, frontend review UI pages (if required).

Verification:
- Unit tests for guardrail triggers; end-to-end tests that a flagged response enters the review queue and is suppressed until human approval.

Risk Controls:
- Human-in-the-loop gating for clinically-sensitive or safety-critical recommendations; confidence threshold enforcement.

Owner: Backend lead, LLM owner.

Phase 5 — CI/CD & Supply Chain (Weeks 6–12)
Goals:
- Harden build and release pipeline, add DAST, container/IaC scanning, signed artifacts, and SBOM enforcement.

Implementation tasks:
- Add DAST job that runs OWASP ZAP against staging; add container image scanning step and IaC security check (e.g., Checkov/TFSec).
- Enforce signed builds and store provenance metadata; publish SBOM for every release artifact.
- Add dependency pinning policy and automated PRs for dependency bumps with a staged rollout process.

Key files & places:
- `ci/` jobs, container build scripts, IaC templates, SBOM artifacts.

Verification:
- DAST run results available in CI; critical findings block promotion to canary until remediated.

Risk Controls:
- Build provenance and signed artifacts prevent tampered releases; SBOMs enable quick CVE triage.

Owner: DevOps lead, Security owner.

Phase 6 — Observability & Incident Response (Weeks 8–14)
Goals:
- Instrument security telemetry, finalize IR runbooks, conduct restore and tabletop drills, and schedule external pentest.

Implementation tasks:
- Add security metrics to observability stack (auth failures, link enumeration rates, guardrail triggers) and wire alerts to PagerDuty or on-call rotation.
- Publish IR runbooks in `docs/IR/` and run a quarterly drill exercising token compromise and restore workflows.
- Schedule and manage a third-party pentest; implement a remediation tracker and retest plan.

Key files & places:
- `docs/IR/`, observability dashboards, alert rules in monitoring/alerts config.

Verification:
- Successful restore drill and tabletop exercise report; pentest report and remediation verification documented in living risk register.

Risk Controls:
- Timebound remediation SLAs and gating: no GA until pentest critical issues closed and restore drill passed.

Owner: Security owner, DevOps lead.

Feature-specific hardening checklist for new planned capabilities
-----------------------------------------------------------------

Forecast expansion
- Treat forecast providers as untrusted external dependencies; require host allowlists, timeouts, and circuit-breakers in the fetch layer.
- Validate every incoming payload against a strict schema and drop unexpected fields instead of passing them through to the API.
- Add tests for stale cache reuse, missing `uvi` values, and provider outages that force degraded-mode summaries.

Astronomy and celestial timing
- Use a trusted astronomy provider or library for sunrise/sunset and lunar calculations; validate timezone, date boundaries, and daylight-saving transitions.
- Cache moon-phase and sunrise/sunset responses with explicit freshness timestamps and fall back to the last-known safe value when the provider is unavailable.
- Reject malformed celestial event records and keep special events such as blood moons and supermoons as informational, not safety-critical, unless paired with other risk signals.

Place allergen extraction and place safety
- Run OCR/text extraction in a bounded parser path and reject HTML, script tags, or oversized payloads before classification.
- Require confidence thresholds for allergen matches; low-confidence extractions must be held in a review queue or dead-letter table.
- Ensure guardrails consume only normalized allergen metadata and never raw menu text unless the user explicitly opts into review.

Tide, weather, and outbreak feeds
- Keep source trust tiers and freshness timestamps attached to every record.
- Disallow medical-style advice unless deterministic guardrails approve the output and the UI displays uncertainty language.
- Add source-specific tests to prove that malformed or stale advisories do not surface as actionable recommendations.

Multimodal routing and travel risk
- Enforce provider-specific quota limits and store immutable snapshots of route responses for audit and rollback.
- Reject route legs that lack valid geometry, timestamps, or provider metadata.
- Keep a safe fallback path when a provider or transit feed is unavailable, and label the response clearly as degraded.

Import connectors
- Make all import features opt-in, revocable, and easy to disable per user.
- Apply content-type validation, attachment scanning, and size limits before parsing PNR, ICS, or email content.
- Minimize retention: only store normalized itinerary data required for the trip, and redact raw message content from logs and analytics.

Security verification additions
- Add unit and integration tests for each backfill feature covering provider outage, malformed payloads, permission bypass, and consent enforcement.
- Add privacy checks to confirm health, itinerary, and sharing data do not leak through shared/public views.
- Include backfill feature checks in release gates before canary promotion.

Backend checklist (detailed)
----------------------------
Core auth & session
- Enforce least-privilege RBAC and object-level authorization in `backend/auth/permissions.py` and `backend/api/router.py`.
- Centralize authorization checks into a single `authorize_user_action(user, resource, action)` helper and use across controllers.
- Add MFA for privileged roles (admin/support) and optional for end users; store MFA configuration securely.
- Implement short-lived access tokens + refresh tokens with reuse detection and rotation. Persist refresh token revocation lists.

Public link & sharing
- Use cryptographically strong opaque tokens (at least 128 bits) and HMAC-sign tokens with server key; store only token hashes.
- Enforce one-time revocation and maintain per-token attempt counters. Block by IP on >10 failed attempts/hour.
- When returning shared data, use field-level view transformations: `public_view()`, `collaborator_view()`, `owner_view()`.

Input validation & injection protection
- Use parameterized queries for all DB access; require linter/static checks to detect raw string interpolation.
- Strict request schemas (Pydantic) for all routes; reject unknown fields and enforce limits on collection sizes.
- Validate and sanitize HTML where needed; use a safe renderer for templates (`backend/templates/*`).
- Implement SSRF protections: whitelist provider hostnames, run outbound requests through a proxy that enforces allowlist.

LLM & recommendation safety
- Implement `backend/services/health_guardrails.py` to run deterministic checks before any LLM output is used. Flag `clinician_review_required` when triggered.
- Prompt- and input-filtering pipeline: remove or escape user-injected control tokens; run a prompt-safety classifier before calling LLM.
- Require citation tokens: every LLM response must include `sources[]` and a confidence score; suppress outputs below threshold.
- Cache sampled LLM outputs, and log inputs/outputs to a guarded review queue for human triage.

Data protection & secure storage
- Encrypt sensitive columns using a managed KMS (Azure/AWS/GCP). Fields: health profile, share tokens, PII, refresh token hashes.
- Ensure database backups are encrypted and access-controlled; rotate keys and test restores quarterly.
- Implement secure deletion workflows to purge data from primary DB, replicas, caches (Redis), and backups where required.

Rate limiting & abuse detection
- Add per-user and per-IP rate limits (configured in `backend/auth/security.py` and middleware), and response headers (`X-RateLimit-*`).
- Add anomaly detection rules: spikes in share link attempts, repeated route recompute requests, scraping patterns.
- Integrate WAF rules and bot mitigation (Cloud WAF or on-prem WAF) to block credential stuffing and DDoS.

Logging & audit
- Emit structured JSON logs with request_id, user_id (when available), action, resource_id, outcome. Use `logging_utils.py`.
- Ensure logs redact PII and secrets by default; allow temporary escalation to full logs via an audited workflow.
- Persist immutable audit entries for sharing actions, permission changes, login failures, and guardrail triggers.

Testing & CI
- Add unit tests for auth, share token lifecycle, row-level authorization, and guardrail rules under `backend/tests/test_security.py`.
- Add integration tests simulating link-enumeration, expired link, revoked link, and provider failure scenarios.
- Fail CI on critical SAST/DAST/secret-scan findings.

Frontend checklist (detailed)
-----------------------------
Token handling & auth UX
- Store access tokens in memory; use refresh tokens in secure, httpOnly cookies where web-based; mobile use secure keystore.
- Clear auth state on logout, revoke refresh token server-side, and avoid persistent debug logs containing tokens.
- Implement step-up auth UX for risky actions (e.g., change sharing permissions) and make MFA flow clear and recoverable.

Redaction & privacy
- Default all shared views to redact sensitive fields (health, device tokens). Implement view modes for `public`, `collaborator`, `owner`.
- In settings UI (`frontend/RiskRadar/app/main/settings.tsx`) show clear consent toggles for `user_health_profile` and export/delete actions.

Safe rendering and CSP
- Enforce a strict CSP header and ensure frontend avoids `unsafe-inline` JS/CSS; use nonce-based scripts for dynamic content.
- Prevent clickjacking and frame embedding; set `X-Frame-Options: DENY`.

Defensive UX
- Show explicit warnings for low-confidence recommendations, suppressed LLM outputs, and degraded modes.
- Handle expired/revoked links with clear messages and report options.

DevOps & CI/CD checklist (detailed)
----------------------------------
Secure SDLC
- Add SAST (e.g., Bandit/Brakeman/ESLint rules), DAST (e.g., OWASP ZAP), secret scanning (truffleHog/Repo-Audit), dependency scanning (Dependabot, Snyk) to CI.
- Generate SBOMs for Python dependencies, containers, and IaC. Pin dependencies and require approval for upgrades for critical libs.
- Container image scanning and signature verification; reject images with critical findings.

Infrastructure hardening
- Use least-privilege IAM roles, and enforce mTLS or managed service identities for inter-service calls where possible.
- Store secrets in managed vaults (HashiCorp Vault, Azure KeyVault), rotate keys monthly or on suspicion of compromise.
- Network: enforce private subnets for databases; restrict egress; use NAT/proxy to control outbound provider calls.

Resilience & recovery
- Automated daily encrypted backups with retention policy aligned to compliance; test restore quarterly.
- Define RTO/RPO and document runbooks for DB restore, key compromise, and provider compromise.

WAF & edge protections
- Deploy WAF rules for credential stuffing, SQLi/XSS patterns, and rate-limit enforcement.
- Configure CDN edge caching with origin protection and bot mitigation.

Supply chain protections
- Pin dependencies, review high-risk transitive packages, and produce SBOMs. Require signed commits/releases for production artifacts.

Observability & incident response
--------------------------------
- Security telemetry: auth failures, unusual authorization denials, link enumeration, provider anomalies, guardrail triggers.
- Alerting: page on sustained brute-force attempts, data exfiltration indicators, or critical guardrail failures.
- IR runbooks: token compromise, provider compromise, data leak, unsafe assistant output. Run quarterly tabletop exercises.

Verification & release gates
--------------------------
- CI gates: SAST/secret-scan/dependency-scan must pass; DAST runs on staging and must have no critical findings.
- Pre-canary checklist: pass security tests, complete pentest remediation, restore drill success, feature-flag rollback paths.
- Canary monitoring: security telemetry for 48h with defined thresholds; block rollout if anomalies detected.

Owner & contact matrix
----------------------
- Security owner: [TBD] (must be assigned during Phase 0).
- Backend lead: [TBD]
- Frontend lead: [TBD]
- DevOps lead: [TBD]

Appendix: Quick tasks per repo file
---------------------------------
- `backend/auth/security.py`: implement token rotation, refresh token revocation lists, HMAC token hashing, MFA hooks.
- `backend/main.py`: tighten CORS config, add security headers middleware, integrate rate-limit middleware.
- `backend/config/settings.py`: move secrets to vault references; add feature toggles for canary and security flags.
- `frontend/RiskRadar/utils/api.ts`: ensure Authorization header patterns, handle 401 -> token refresh, block unsafe redirects.
- `backend/tests/test_security.py`: add unit/integration tests for all critical flows.

Next steps
----------
1. Assign owners & add living risk register entry (Phase 0).
2. Implement sprint tasks mapped above and update `docs/expansion/RISKRADAR_SPRINT_ROADMAP.md` with security subtasks.
3. Run CI security scans; fix critical findings and repeat until green.
4. Schedule third-party pentest and tabletop IR drill before GA.

Notes on guarantees
-------------------
Security is a risk-reduction discipline: this plan enforces defense-in-depth and verifiable release gates. It cannot logically claim absolute perfect security (no system can), but it does create airtight processes, automation, and verification so RiskRadar minimizes real-world risk and responds rapidly if an incident occurs.
