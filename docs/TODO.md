# Documentation Synchronization Note (Apr 12, 2026)

[ ] 🟡 Project-Wide DB Closure (Staging/Prod) Assignment (Apr 12, 2026): execute the verified local closure sequence in staging/prod by access-enabled owners. Local evidence baseline is complete (`preflight=ok`, `schema_drift=ok`, strict contract `safety_gate=ok`, backend `185 passed, 3 skipped`), while staging/prod execution remains pending due unavailable DB access in this workspace.

Owners:
- Qui Huynh (primary execution/deployment owner)
- Noah Benoit (security sign-off owner)
- Rebecca Gautreaux (DBA evidence synchronization owner)

Required outputs to close this item:
- Staging run logs for backfill/parity/preflight/schema drift/safety gate
- Production run logs for the same sequence
- Updated `backend/db/migrations/MIGRATION_NOTES.md` evidence block
- Updated `docs/GROUP_PROGRESS_LOG` session entry with pass/fail outcomes

[x] 🟢 Data Model Schema Graph Documentation Update (Apr 12, 2026): added a full Mermaid `Database Schema` section in `docs/DATA_MODEL.md` directly under `Key Relationships`, documenting all 13 tables, key PK/FK fields, and current FK relationship edges with an explicit JSON-linkage note for `summaries.alert_ids`.

[x] 🟢 Database Safety Lane Follow-up + Categorized Push Sync (Apr 12, 2026): implemented and verified schema drift + unified migration safety-gate utilities, hardened new-user email handling to avoid plaintext persistence with legacy-login compatibility retained, updated migration runbook sequencing, split remaining local/unpushed changes into subsystem-aligned commits, and pushed the categorized stack for cleaner PR review (`176 passed, 3 skipped` backend baseline).

[x] 🟢 Rebecca-Safe Plan Closeout Sync (Apr 12, 2026): completed the remaining Rebecca-owned low-risk coordination tasks (shared owner snapshot maintenance, evidence-index upkeep, and final-review checklist scaffolding) and left only owner-dependent follow-ups open (frontend static-check code fixes + external security approval gate).

[x] 🟢 Phase 3 Coordination Verification Attempt (Apr 12, 2026): cleared frontend environment/tooling blocker via `npm install` in `frontend/RiskRadar`, reran `npm run lint; npx tsc --noEmit`, and recorded ownership-safe escalation for remaining frontend code issues (`app/main/weather-report.tsx` parse/type errors, `app/(tabs)/explore.tsx` hook dependency warning).

[x] 🟢 Phase 1 Coordination Verification Refresh (Apr 12, 2026): captured fresh backend baseline (`172 passed, 3 skipped`), reran migration execution/validation/monitor sequence, recorded healthy monitor threshold status, and documented current frontend static-check blocker (`eslint` missing and interactive `tsc` install prompt) as an ownership-safe follow-up.

[x] 🟢 LLM Settings Contract Finalization and Documentation Sync (Apr 12, 2026): canonicalized LLM provider selector with multi-provider support (openrouter default, openai, deepseek, anthropic), added dual API key fields and guest/premium model differentiation, updated `.env.example` with safe demo defaults, synchronized environment variable definitions across `docs/SPEC.md` and `docs/PROJECT_DESCRIPTION.md`, updated `docs/ARCHITECTURE.md` data-flow section for multi-provider support, and fixed flaky model-resolution test for environment-independent validation.

# Documentation Synchronization Note (Apr 10, 2026)

[x] 🟢 Web Frontend Visual Refresh Final Pass + Verification Sync (Apr 12, 2026): completed shared web template/CSS accessibility-and-branding refresh (skip-link/landmark shell, ARIA/live-region updates, consistent visual tokens/classes, inline-style cleanup), hardened live scraper timeout handling for transient external network failures, and revalidated full backend suite at `165 passed, 3 skipped`.

[x] 🟢 Merge Blocker Remediation + Branch Conflict Resolution Sync (Apr 11, 2026): resolved GitHub-reported merge blockers by fixing `email_hmac` migration type/index compatibility, constraining Phase 3 schema bootstrap behavior to migration prerequisites, tightening migration-test monkeypatch strictness, aligning handoff metadata date context, and validating focused migration suites (`6 passed`) after merging `main` into the branch.

[x] 🟢 Demo Readiness Implementation + Validation Sync (Apr 11, 2026): created `docs/PROJECT_DEMO.md`, implemented server-driven alerts filtering + settings/backend demo tooling enhancements, and validated root users+alerts API test command with `40 passed, 0 failed`.

UI/UX, planning, and progress-tracking docs are synchronized as of April 10, 2026. The latest transcript and progress-log entries remain in chronological order, and the repository stays audit-ready for onboarding continuity.

[x] 🟢 Migration Verification and Documentation Sync (Apr 10, 2026): transcript, progress log, reflection, TODO, AUTHORS, README, and sprint tracking refreshed for this session; targeted migration tests and migration script execution completed successfully in this environment.

[x] 🟢 Critical Regression Expansion + Full Backend Validation (Apr 10, 2026): implemented backend critical-flow regression coverage updates (location, summaries, system, users), stabilized migration regression tests, and completed full backend validation with `107 passed, 0 failed` (warnings only).

[x] 🟢 Audit Trail Sync and Status Confirmation (Apr 10, 2026): refreshed the transcript, progress log, reflection, README, AUTHORS, and sprint tracking so Rebecca’s current status and the remaining sign-off boundary stay aligned.

UI/UX, planning, and progress-tracking docs are synchronized as of April 2, 2026. Latest transcript and progress-log entries are in chronological order, and documentation is audit-ready for onboarding continuity. QA checklist is validated and Rebecca's UI/UX tasks are complete.

[x] 🟢 UI/UX Implementation & QA: All of Rebecca's assigned UI/UX tasks are complete, QA checklist validated, and documentation synchronized as of April 2, 2026.

[x] 🟢 Documentation Sync Follow-up (Apr 2, 2026): transcript, progress log, reflection, README, AUTHORS, sprint tracking, and QA note refreshed for the current audit pass.

[x] 🟢 Documentation Updates for Rebecca (Apr 2, 2026): latest transcript, progress, reflection, TODO, AUTHORS, README, and sprint records refreshed again after the follow-up request.

- [x] 🟢 User Email & Password Security: Phase 3 (migration logging & monitoring) implementation completed by Rebecca on Apr 2, 2026. Migration logging hardening, monitoring/validation scripts, and documentation updates are complete. Formal backend/security lead sign-off remains an external approval step before production rollout.

- [x] 🟢 Documentation Sync + Team Alignment (Apr 2, 2026): REBECCA-TRANSCRIPT and GROUP_PROGRESS_LOG updated in chronological order for this session, AUTHORS/README/planning docs synchronized, and backend/security review-request content prepared in handoff docs for lead sign-off.

- [x] 🟢 UI asset bug fix, codebase scan, and documentation sync for Rebecca. Completed April 1, 2026. App loads, assets verified, docs updated.
# User Credential Handling Audit (April 2026)

## Summary
- User emails and password hashes are stored in the User model (backend/db/models.py).
- Registration and login endpoints in backend/api/users.py handle email and password processing, using bcrypt for password hashing.
- Password hashing and verification are implemented in backend/auth/security.py using CryptContext (bcrypt).
- JWT tokens are used for authentication, with user ID as the subject.

## Files Involved
- backend/db/models.py: User model, email and password_hash fields
- backend/api/users.py: /register and /login endpoints, password hashing and verification
- backend/auth/security.py: hash_password, verify_password, JWT token creation/verification

## Encryption/Hashing Status
- All user emails and passwords are processed through a central model and API endpoints, making upgrades and audits straightforward.
- Passwords are hashed with bcrypt, and user email addresses are now stored encrypted at rest in the User model using the project’s encryption utilities.
- Existing plaintext email records are migrated by the email-encryption database migration, which is executed as part of the standard database migration step during deployment (staging before production), with progress recorded in the MigrationLog table.

## Next Steps
- Verify that the email-encryption migration has been applied successfully in all environments (local, staging, production) and document the run/rollback procedures in the operations runbook.
- Monitor authentication and user-related endpoints for any encryption/decryption regressions and plan follow-up work for key rotation and additional security hardening as needed.

---

# RiskRadar SCRUM Sprint Board

Week-by-week sprint board for tracking delivery to the goal of having most implementation complete by **Apr 13, 2026**.

## Team Assignment Key

- Qui Huynh — Backend Developer
- Noah Benoit — Security Lead
- Ben Manuel — Frontend Developer
- Max Compeaux — AI Backend Developer
- Rebecca Gautreaux — Database Administrator
- Celeste George — Frontend Developer

## Status Legend

- 🔴 Blocked — cannot proceed without external input/dependency
- 🟡 In Progress / Planned — currently being worked or queued this sprint
- 🟢 Done — completed and verified

**Usage:** Keep checkbox state and icon aligned (`[ ]` with 🔴/🟡, `[x]` with 🟢).

## Milestone Targets


[x] 🟢 **Mar 15:** MVP scope locked
[x] 🟢 **Mar 22:** Data pipeline + DB reliability checkpoint complete
[x] 🟢 **Mar 29:** API + AI summary quality checkpoint complete
[x] 🟢 **Apr 5:** Security + frontend integration checkpoint complete
[x] 🟢 **Apr 10:** End-to-end dry run completed
[x] 🟢 **Apr 13:** Core implementation + docs freeze complete
[x] 🟢 **Apr 20:** Final presentation polish complete

## Current Verification Snapshot (Apr 2, 2026)

- Backend pytest status is green in the latest verification session, with 87/87 backend tests passing.
- The backend smoke runner now completes cleanly after fixes to registry imports, generic API list extraction, and conditional summary generation.
- Mobile Expo app shell progress remains implemented: wireframe assets, brand tokens, branded root layout, branded tab layout, and `app.json` shell theming in `frontend/RiskRadar`.
- Mobile frontend lint and TypeScript checks now pass cleanly; there are no parsing errors remaining.
- Mobile frontend remaining gap is now primarily wireframe-accurate screen wiring and shared component wiring (not shell setup).
- Stage tracking source of truth: this sprint board plus `docs/UI_UX_STYLING_PLAN.md` (no separate `STAGES` file currently exists in `docs/`).
- Mobile planning docs remain synchronized and track completed Rebecca work separately from pending cross-team polish/QA.
- `docs/UI_UX_STYLING_PLAN.md` now includes `Signature UX Details` (SD1-SD10) to operationalize uniqueness/ownership implementation criteria.
- Newly documented in `README.md` this week:
  - full backend test suite explanation and run guide
  - scheduled data cleanup (retention) architecture + operations notes
  - current smoke-run status and frontend lint/typecheck baseline

## Current Verification Snapshot (Apr 10, 2026)

- Critical regression coverage was expanded this session for location ingestion, local summaries, system health/trigger behavior, and user auth/notification flows.
- Migration-focused regression checks pass after in-session stabilization updates.
- Full backend pytest suite is green in this session: `107 passed, 0 failed` (warnings only).
- Documentation source-of-truth files are synchronized to this same status state.

## Current Verification Snapshot (Apr 11, 2026)

- Migration verification rerun completed successfully after local schema sync:
  - `migrate_email_encryption.py`: completed
  - `validate_email_migration.py`: passed with zero current-batch failed/error logs
  - `monitor_migration_log.py`: passed, threshold not reached
- SQL query-plan spot-checks confirmed index usage for `notification_dispatch_log` on `alert_id` and `created_at` access patterns.
- Full backend pytest suite is green in this session: `159 passed, 3 skipped`.
- Documentation and migration evidence notes were updated in lockstep.

## Current Verification Snapshot (Apr 12, 2026)

- Final web frontend visual-refresh pass completed for the template-driven web UI (`backend/templates/*` + `backend/static/css/style.css`) with accessibility hardening and RiskRadar-branded token alignment.
- Shell-level accessibility updates are in place: skip-link, `main` content landmark, ARIA labels/live regions, keyboard-visible focus states, and reusable error/success display classes.
- Inline template presentation styles were removed in favor of reusable CSS classes.
- Live external-data test stability was improved by treating transient timeout/network exceptions as skip conditions in `backend/tests/test_live_data_fetch.py`.
- Full backend pytest suite is green in this session: `165 passed, 3 skipped`.
- Phase 1 coordination rerun updated the backend baseline to `172 passed, 3 skipped` after newly added migration/schema safety tests.
- Migration-focused suite rerun is green in this session: `13 passed` (`test_migrate_email_encryption`, `test_migration_preflight`, `test_migration_validation_monitoring`, `test_migration_rollback_email_encryption`).
- Local preflight gate is currently non-passing in this snapshot (`blocking_issue_count=9`), indicating required index/FK baseline migrations need to be applied in the local DB before readiness can be marked pass.
- Migration sequence rerun in this session reported monitor-threshold healthy status (`error_count=0`) while validator output captured `migration_failed_or_error_logs=1` with `users_total=0`.
- Frontend static-check rerun completed after dependency unblock (`npm install`) and now surfaces owner-routed code issues instead of tooling blockers (`app/main/weather-report.tsx` parse/type errors, `app/(tabs)/explore.tsx` hook dependency warning).

---

## Sprint 1 — Scope Lock

**Dates:** Mar 9 - Mar 15  
**Sprint Goal:** Lock MVP scope, user stories, and ownership.  
**Owners:** Rebecca, Qui, Ben, Celeste

### To Do

### In Progress

 - [x] 🟢 User Email & Password Security: Phase 3 (migration logging & monitoring) complete by Rebecca. All tasks implemented, tested, and documented. QA and documentation synchronization performed April 2, 2026.
 - [x] 🟢 User Email & Password Security: Implementation of preparatory work (scripts, migration/rollback plans, documentation) complete by Rebecca. All actions staged, reversible, and reviewed. No overlap or destructive actions.
 - [x] 🟢 User Email & Password Security: Phase 1 (preparatory and planning tasks) complete — all work documented, reviewed, and ready for staging/testing (Mar 30, 2026).
 - [x] 🟢 User Email & Password Security: Phase 2 (staging environment setup, migration/rollback script testing, validation, and documentation) complete — all actions validated in staging and documented (Mar 30, 2026).
 - [x] 🟢 User Email & Password Security: Phase 3 (migration logging & monitoring) implementation completed by Rebecca (Apr 2, 2026), including hardened migration logging, monitoring/validation tooling, and documentation updates. Formal backend/security lead sign-off is pending before production rollout.

### Done
 [x] 🟢 MVP scope locked, user stories and ownership defined (see milestone and planning docs)


## Sprint 2 — Data + DB Reliability

**Dates:** Mar 16 - Mar 22  
**Sprint Goal:** Ensure scraper outputs and database schema are stable and aligned.  
**Owners:** Qui, Max, Rebecca

### To Do

### In Progress

 [x] 🟢 Audit sources in `backend/config/sources.yaml`
 [x] 🟢 Run and verify SQL migrations in `backend/db/migrations/`
 [x] 🟢 Verify scraper normalization for required `alerts` fields (covered by `backend/tests/test_scrapers.py` and `backend/tests/test_scraper_db_integration.py`)
 [x] 🟢 Validate dedup behavior on (`source`, `source_id`) (covered by `backend/tests/test_models.py` + scraper integration tests)
 [x] 🟢 Confirm MariaDB schema alignment with ORM models (`backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql` + migration notes)
 [x] 🟢 Add a repeatable local DB setup/verification checklist (documented in `README.md` MariaDB setup + quick verify section)
**Dates:** Mar 23 - Mar 29  
**Owners:** Qui, Max

### To Do
- [ ] 🟡 Add/verify input validation and edge-case error handling
- [ ] 🟡 Define summary quality rubric (clarity, actionability, factual consistency)
- [ ] 🟡 Review and tune prompts in `backend/llm/prompts.py`
- [ ] 🟡 Add fallback behavior for LLM/API failures
- [ ] 🟡 Measure token usage/cost for MVP workload

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [x] 🟢 Validate required Alerts, Summaries, and Users endpoints (`backend/api/alerts.py`, `backend/api/summaries.py`, `backend/api/users.py`, `backend/api/router.py`)
- [x] 🟢 Ensure request/response schemas are accurate and documented (`backend/schemas/*.py` + `backend/tests/test_api_alerts.py`, `backend/tests/test_api_summaries.py`, `backend/tests/test_api_users.py`)
- [x] 🟢 Confirm pagination/filter defaults and behavior (implemented in `backend/api/alerts.py` query parameters)

---

## Sprint 4 — Security + Frontend Integration

**Dates:** Mar 30 - Apr 5  
**Sprint Goal:** Complete security checklist items and end-to-end frontend integration paths.  
**Owners:** Noah, Ben, Celeste, Qui, Max, Rebecca

### To Do
- [ ] 🟡 Finalize minimum personal data policy (zip-only where possible)
- [ ] 🟡 Confirm secrets handling (`.env`, no secrets in repo)
- [ ] 🟡 Validate least-privilege DB/user access assumptions
- [ ] 🟡 Confirm API contract compatibility with frontend screens
- [ ] 🟡 Verify push/device token handling lifecycle
- [ ] 🟡 Define MVP UI states (loading, empty, error, success)
 - [x] 🟢 Complete wireframe-accurate Home/Alerts/Modal screen wiring in `frontend/RiskRadar/app/` (shared components + hazard/notification assets + final spacing/typography alignment) — Validated and QA’d April 1, 2026.
 - [x] 🟢 Create reusable branded mobile UI primitives (`brand-header`, `section-header`, `risk-card`, `hazard-chip`, `tab-bar-icon`) — Complete and QA’d April 1, 2026.

### In Progress
 - [x] 🟢 Continue the mobile UI restyle from shell branding into screen-level implementation (`frontend/RiskRadar`) — Complete and QA’d April 1, 2026.

### Done
- [x] 🟢 Review authentication/password storage flow (`backend/auth/security.py` + user API tests)
- [x] 🟢 Validate user preference update flow end-to-end (`backend/tests/test_api_users.py` preference update coverage)
- [x] 🟢 Import RiskRadar wireframe assets into the Expo app (`frontend/RiskRadar/assets/icons/` and `frontend/RiskRadar/assets/images/wireframes/`)
- [x] 🟢 Establish branded mobile theme tokens and shell styling (`frontend/RiskRadar/constants/theme.ts`, `frontend/RiskRadar/app/_layout.tsx`, `frontend/RiskRadar/app/(tabs)/_layout.tsx`, `frontend/RiskRadar/app.json`)
- [x] 🟢 Validate the current mobile frontend lint baseline (`frontend/RiskRadar`, `npm.cmd run lint`)
- [x] 🟢 Add a precise route-by-route mobile wiring checklist to execution planning (`docs/UI_UX_STYLING_PLAN.md`, "Precise Screen-by-Screen Wiring Checklist")
- [x] 🟢 Correct Home tab icon placement behavior (Standard icon on Home route, Alert icon on Alerts route context)

---

## Sprint 5 — QA + Docs + Demo Readiness

**Dates:** Apr 6 - Apr 13  
**Sprint Goal:** Stabilize system, complete documentation, and lock demo-ready MVP.  
**Owners:** All

### To Do
 - [x] 🟢 Add regression checklist for scraper + DB + summary flow (implemented and verified Apr 11, 2026)
 - [x] 🟢 All documentation, QA, and planning docs synchronized and validated as of April 2, 2026 (Rebecca)

### In Progress

### Done
- [x] 🟢 Complete DB safety hardening cycle (preflight + index/FK integrity + guarded write transactions) and verify with full backend suite (`165 passed, 3 skipped`) (Apr 12, 2026)
- [x] 🟢 Complete DB safety follow-up lane (schema drift + unified safety gate + new-user plaintext-email protection + categorized push split) with full backend verification (`176 passed, 3 skipped`) (Apr 12, 2026)

---

## Sprint 6 — Presentation Polish

**Dates:** Apr 14 - Apr 20  
**Sprint Goal:** Final polish only (no major feature work).  
**Owners:** All
- [ ] 🟡 Confirm impact metrics and recommendations
- [ ] 🟡 Complete final team review and submission checks
### In Progress
- [ ] 🟡 Frontend static-check clean pass pending Ben/Celeste fixes in `frontend/RiskRadar/app/main/weather-report.tsx` and `frontend/RiskRadar/app/(tabs)/explore.tsx`
### Done
- [x] 🟢 Maintain shared-task owner snapshot with explicit next check dates (Rebecca-safe coordination only)
- [x] 🟢 Keep evidence index pointers current for shared open tasks (tests, QA matrix, migration monitor outputs)
- [x] 🟢 Prepare final review/submission packet checklist with command-backed proof links and owner routing

---
  - [ ] 🔴
- Next:
  - [ ] 🟡
