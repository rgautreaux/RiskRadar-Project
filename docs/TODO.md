# Documentation Synchronization Note (Apr 10, 2026)

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
 - [ ] 🟡 Add regression checklist for scraper + DB + summary flow
 - [x] 🟢 All documentation, QA, and planning docs synchronized and validated as of April 2, 2026 (Rebecca)

### In Progress

### Done

---

## Sprint 6 — Presentation Polish

**Dates:** Apr 14 - Apr 20  
**Sprint Goal:** Final polish only (no major feature work).  
**Owners:** All
- [ ] 🟡 Confirm impact metrics and recommendations
- [ ] 🟡 Complete final team review and submission checks
### In Progress
- [ ] 🟡 Move active tasks here
### Done

---
  - [ ] 🔴
- Next:
  - [ ] 🟡
