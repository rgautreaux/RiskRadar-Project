# Noah Benoit — Security Completions by Sprint
**Role:** Security Lead | INFX 490 Capstone — Team 6 (RiskRadar)

---

## Contribution Breakdown by Sprint

| Sprint | Security | Backend | Database | Frontend |
|--------|----------|---------|----------|----------|
| Sprint 1 | 25% | 50% | 10% | 15% |
| Sprint 2 | 25% | 40% | 30% | 5% |
| Sprint 3 | 15% | 25% | 60% | 0% |

**Methodology:** Noah's role is static analysis, auditing, reporting, and documentation. He identifies issues and produces plans, but does not write code or execute migrations. Implementation credit is distributed to the teammates who actually build the fixes. Each sprint's percentages reflect the full weight of work generated — Noah's share is the identification and planning layer only; the larger shares belong to the developers writing the program.

| Finding / Plan | Noah's Role | Who Gets Implementation Credit |
|---|---|---|
| LLM Prompt (Sprint 1) | Designed security constraints | Max / Backend — builds and integrates the LLM API |
| SBOM (Sprint 1) | Documented the tech stack | Backend, Frontend, Database — they built the stack being catalogued |
| Security Questionnaire (Sprint 1) | Created and distributed | Whole team — filled it out; drives future dev decisions |
| Plaintext email storage | Identified, documented, assigned | Qui (backend encryption logic), Rebecca (schema + migration) |
| JWT hardcoded default | Identified, wrote Key Management Plan | Qui (backend startup validation + env config) |
| CORS wildcard origin | Identified, assigned fix | Qui (backend CORS config) |
| No rate limiting on login | Identified, assigned fix | Qui (backend slowapi middleware) |
| Email uniqueness post-encryption | Identified, designed HMAC-SHA256 approach | Qui (query logic), Rebecca (schema) |
| Email Encryption schema changes | Designed schema plan | Rebecca (database implementation) |
| Migration / rollback scripts | Reviewed and flagged issues | Rebecca (script revision + execution) |
| User Security Plan (all phases) | Authored full roadmap | Rebecca (DB/migration/staging), Qui (backend code changes) |
| GDPR/CCPA roadmap | Authored compliance plan | Team (execution across roles) |

**Sprint 1 reasoning:** Noah writes the questionnaire, SBOM, and LLM prompt. But the SBOM documents what the backend, frontend, and database teams actually built. The LLM prompt is a backend artifact Max implements. Backend carries 50%, frontend 15%, and database 10% because those are the roles whose actual code and infrastructure is being catalogued and planned around.

**Sprint 2 reasoning:** Every finding Noah flags gets fixed by Qui (CORS, rate limiting, JWT startup check, bcrypt confirmation) or Rebecca (schema design, migration scripts). The audit report, GDPR/CCPA review, key management plan, and schema impact doc are all planning documents — the heavier implementation work falls to backend (40%) and database (30%). Frontend carries 5% for consent/notification UI implications in the GDPR roadmap.

**Sprint 3 reasoning:** The User Security Plan drives SB2-23 entirely. Rebecca executes all three migration phases — schema changes, migration/rollback scripts, staging validation, and migration logging — which is why database dominates at 60%. Qui handles the backend auth/API code changes (25%). Noah authored the roadmap but none of the implementation, keeping security at 15%.

---

## Sprint 1
*Jira Tasks: SCRUM-6, SCRUM-13, SCRUM-16 | Scope & Foundation Phase*

---

### Security Questionnaire
**Jira:** SCRUM-13 — *Security Questionnaire and Contingency Measures*

Created and distributed the Mobile App Security Questionnaire to define how RiskRadar would handle security across the team. Collected completed responses from Ben, Celeste, Qui, and Max. Responses informed the SBOM, Threat Model, and Risk Register.

---

### SBOM (Software Bill of Materials)
**Jira:** SCRUM-6 — *SBOM built from Security Questionnaire, Threat Model, and Risk Register*

Produced the initial Software Bill of Materials for RiskRadar (March 3, 2026), cataloging all frontend, backend, database, and infrastructure dependencies with versions, vendors, and licenses. Maintained and updated the SBOM as of March 16, 2026 to reflect post-meeting corrections and source code changes.

---

### LLM Prompt for News Scraper
**Jira:** SCRUM-16 — *Project Foundational Prompt*

Designed a prompt injection-resistant system prompt for the app's AI-powered article formatter. Included explicit defenses against XSS, SQL injection, and prompt injection patterns found in scraped web content, ensuring the LLM treats all scraped input as untrusted data.

---

## Sprint 2
*Jira Tasks: SB2-01/02, SB2-03, SB2-08, SB2-20, SB2-21 | March 10 – March 28, 2026*

---

### Codebase Security Audit
**Jira:** SB2-03 (bcrypt/SHA-256) · SB2-01/02 (JWT) · SB2-20 (CORS) · SB2-21 (Rate Limiting)

Reviewed 5 backend files (`backend/db/models.py`, `backend/api/users.py`, `backend/auth/security.py`, `backend/config/settings.py`, `.env.example`) and identified 7 findings classified by severity with specific file and line references. Findings covered plaintext email storage (HIGH), bcrypt already live with outdated Tech Stack Reference (INFO), JWT hardcoded default fallback (HIGH), CORS wildcard origin (MEDIUM), missing rate limiting on login (MEDIUM), email uniqueness logic pending encryption (MEDIUM), and solid existing test coverage (POSITIVE). Action items assigned to teammates.

*Completed: March 22, 2026*

---

### GDPR/CCPA Compliance Review
**Jira:** SB2-03 · SB2-08 — *(Security Hardening / Environment Setup)*

Mapped all RiskRadar user data (email, password hash, display name, ZIP code, GPS coordinates, device token, preferences, behavioral data) against GDPR and CCPA requirements. Identified 9 compliance gaps and produced a prioritized compliance roadmap with pre-launch and post-launch action items covering data minimization, right to erasure, consent mechanisms, and breach notification procedures.

*Completed: March 22, 2026*

---

### Key Management Plan
**Jira:** SB2-01/02 (JWT Secret) · SB2-08 (Secrets/Env Setup)

Documented full procedures for generating, storing, rotating, and recovering both the JWT secret key and the AES-256 email encryption key. Covered AWS Secrets Manager integration, strong key generation commands, startup validation check to prevent deployment with the placeholder default, and rotation schedules.

*Completed: March 22, 2026*

---

### Email Encryption Considerations
**Jira:** SB2-03 · SB2-23 (pre-work) — *(Security Hardening)*

Independently evaluated three AES-256 encryption approaches for email storage: non-deterministic GCM (Option A), deterministic fixed-IV (Option B), and HMAC-SHA256 + GCM hybrid (Option C). Recommended Option C with full tradeoff justification covering security, searchability, and uniqueness enforcement. Specified the required schema changes (new `email_encrypted`, `email_hmac`, `email_iv` columns) and new environment variables (`EMAIL_ENCRYPTION_KEY`, `EMAIL_HMAC_KEY`).

*Completed: March 22, 2026*

---

### Email Encryption Considerations — Schema Impact
**Jira:** SB2-03 · SB2-23 (pre-work) — *(Security Hardening)*

Defined the exact database columns to add, the code files requiring updates (`backend/db/models.py`, `backend/api/users.py`, `backend/auth/security.py`), and all logic changes needed across the backend to implement the recommended Option C encryption approach. Provided a clear integration map for Qui and Rebecca before execution.

*Completed: March 22, 2026*

---

### Code Review — Migration Scripts
**Jira:** SB2-23 (pre-work) — *(Security Hardening)*

Reviewed the draft email encryption migration script (`draft_email_encryption_migration.py`) and rollback script (`draft_email_encryption_rollback.py`). Identified that the non-deterministic GCM approach in the current draft breaks login and duplicate-detection queries, and specified required revisions before the scripts are safe to execute in staging. Verdict: not ready to execute; revisions required.

*Completed: March 22, 2026*

---

### Tech Stack Reference (Security Lens)
**Jira:** SB2-03 — *(Security Hardening)*

Identified and documented a discrepancy between the Tech Stack Reference (which listed SHA-256 as the password hashing algorithm) and the actual codebase (which correctly uses bcrypt). Flagged the inaccuracy in the Codebase Audit Report and assigned a correction task to ensure documentation reflects the live implementation.

*Completed: March 22, 2026*

---

### User Communication Draft
**Jira:** SB2-23 (pre-work) · SB2-08 — *(Security Hardening / User Trust)*

Drafted two user-facing communications for the upcoming email encryption migration: a pre-migration notice (informing users of the upcoming upgrade and what to expect) and a post-migration confirmation (confirming the upgrade is complete and providing support contact). Designed for in-app banner, push notification, and email channels.

*Completed: March 22, 2026*

---

## Sprint 3
*Jira Task: SB2-23 | March 23 – April 13, 2026*

---

### User Security Plan
**Jira:** SB2-23 — *Implement User Email and Password Encryption* (High Priority · In-Progress · Rebecca / Noah / Qui)

Wrote the full phased security roadmap for encrypting user emails and hardening password storage in RiskRadar.

- **Phase 1 — Analysis & Preparation** *(Complete as of March 30, 2026)*: Documented codebase audit findings, designed schema changes, drafted migration and rollback scripts, authored migration logging plan, authored monitoring/logging setup plan, authored staging environment setup plan.

- **Phase 2 — Staging & Validation** *(Complete as of March 30, 2026)*: All migration/rollback scripts tested and validated in staging environment; no production-impacting changes made; all actions documented.

- **Phase 3 — Migration Logging & Monitoring** *(In Progress)*: Implementing and verifying migration logging (table/file), setting up monitoring and alerting for migration events, documenting process for team review before any production deployment.

---

*Document generated April 13, 2026 — cross-referenced against Sprint Backlog 1 (SCRUM tasks), Sprint Backlog 2 (SB2-01 through SB2-22), and Sprint Backlog 3 (SB2-01 through SB2-37).*
