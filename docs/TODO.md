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

- [ ] 🟡 **Mar 15:** MVP scope locked
- [ ] 🟡 **Mar 22:** Data pipeline + DB reliability checkpoint complete
- [ ] 🟡 **Mar 29:** API + AI summary quality checkpoint complete
- [ ] 🟡 **Apr 5:** Security + frontend integration checkpoint complete
- [ ] 🟡 **Apr 10:** End-to-end dry run completed
- [ ] 🟡 **Apr 13:** Core implementation + docs freeze complete
- [ ] 🟡 **Apr 20:** Final presentation polish complete

## Current Verification Snapshot (Mar 12, 2026)

- Backend pytest run (local venv): **78 collected, 52 passed, 26 errors**
- Current blocker for full green test run: missing `passlib` module in active environment
- Newly documented in `README.md` this week:
  - full backend test suite explanation and run guide
  - scheduled data cleanup (retention) architecture + operations notes

---

## Sprint 1 — Scope Lock

**Dates:** Mar 9 - Mar 15  
**Sprint Goal:** Lock MVP scope, user stories, and ownership.  
**Owners:** Rebecca, Qui, Ben, Celeste

### To Do
- [ ] 🟡 Finalize MVP audience focus (Travelers + Truckers)
- [ ] 🟡 Freeze MVP feature list (alerts, preferences, summaries, digest notifications)
- [ ] 🟡 Define explicit out-of-scope items for this term
- [ ] 🟡 Convert MVP scope into 5–8 user stories with acceptance criteria
- [ ] 🟡 Confirm owner per user story

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [ ] 🟢 Move completed tasks here

---

## Sprint 2 — Data + DB Reliability

**Dates:** Mar 16 - Mar 22  
**Sprint Goal:** Ensure scraper outputs and database schema are stable and aligned.  
**Owners:** Qui, Max, Rebecca

### To Do
- [ ] 🟡 Audit sources in `backend/config/sources.yaml`
- [x] 🟢 Verify scraper normalization for required `alerts` fields (covered by `backend/tests/test_scrapers.py` and `backend/tests/test_scraper_db_integration.py`)
- [x] 🟢 Validate dedup behavior on (`source`, `source_id`) (covered by `backend/tests/test_models.py` + scraper integration tests)
- [x] 🟢 Confirm MariaDB schema alignment with ORM models (`backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql` + migration notes)
- [ ] 🟡 Run and verify SQL migrations in `backend/db/migrations/`
- [x] 🟢 Add a repeatable local DB setup/verification checklist (documented in `README.md` MariaDB setup + quick verify section)

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [ ] 🟢 Move completed tasks here

---

## Sprint 3 — API + AI Quality

**Dates:** Mar 23 - Mar 29  
**Sprint Goal:** Complete core API behavior and improve summary quality/reliability.  
**Owners:** Qui, Max

### To Do
- [x] 🟢 Validate required Alerts, Summaries, and Users endpoints (`backend/api/alerts.py`, `backend/api/summaries.py`, `backend/api/users.py`, `backend/api/router.py`)
- [x] 🟢 Ensure request/response schemas are accurate and documented (`backend/schemas/*.py` + `backend/tests/test_api_alerts.py`, `backend/tests/test_api_summaries.py`, `backend/tests/test_api_users.py`)
- [ ] 🟡 Add/verify input validation and edge-case error handling
- [x] 🟢 Confirm pagination/filter defaults and behavior (implemented in `backend/api/alerts.py` query parameters)
- [ ] 🟡 Define summary quality rubric (clarity, actionability, factual consistency)
- [ ] 🟡 Review and tune prompts in `backend/llm/prompts.py`
- [ ] 🟡 Add fallback behavior for LLM/API failures
- [ ] 🟡 Measure token usage/cost for MVP workload

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [ ] 🟢 Move completed tasks here

---

## Sprint 4 — Security + Frontend Integration

**Dates:** Mar 30 - Apr 5  
**Sprint Goal:** Complete security checklist items and end-to-end frontend integration paths.  
**Owners:** Noah, Ben, Celeste, Qui, Max, Rebecca

### To Do
- [ ] 🟡 Finalize minimum personal data policy (zip-only where possible)
- [ ] 🟡 Confirm secrets handling (`.env`, no secrets in repo)
- [x] 🟢 Review authentication/password storage flow (`backend/auth/security.py` + user API tests)
- [ ] 🟡 Validate least-privilege DB/user access assumptions
- [ ] 🟡 Confirm API contract compatibility with frontend screens
- [x] 🟢 Validate user preference update flow end-to-end (`backend/tests/test_api_users.py` preference update coverage)
- [ ] 🟡 Verify push/device token handling lifecycle
- [ ] 🟡 Define MVP UI states (loading, empty, error, success)

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [ ] 🟢 Move completed tasks here

---

## Sprint 5 — QA + Docs + Demo Readiness

**Dates:** Apr 6 - Apr 13  
**Sprint Goal:** Stabilize system, complete documentation, and lock demo-ready MVP.  
**Owners:** All

### To Do
- [ ] 🟡 Keep backend tests green in `backend/tests/` (Mar 12 status: 52 passed, 26 errors due to missing `passlib` in local environment)
- [ ] 🟡 Add tests for uncovered critical paths
- [ ] 🟡 Add regression checklist for scraper + DB + summary flow
- [x] 🟢 Validate scheduler startup/shutdown behavior baseline (`backend/tests/test_retention.py` verifies retention job registration and scheduler start)
- [ ] 🟡 Track known issues with severity and owner
- [x] 🟢 Update `README.md` architecture and quick-start accuracy (tests and retention cleanup sections updated Mar 12)
- [ ] 🟡 Reconcile docs (`ARCHITECTURE.md`, `DATA_MODEL.md`, `PROJECT_DESCRIPTION.md`)
- [ ] 🟡 Prepare executive-level narrative + final demo script
- [ ] 🟡 Run end-to-end dry run by Apr 10
- [ ] 🟡 Complete documentation freeze and repo cleanup by Apr 13

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [ ] 🟢 Move completed tasks here

---

## Sprint 6 — Presentation Polish

**Dates:** Apr 14 - Apr 20  
**Sprint Goal:** Final polish only (no major feature work).  
**Owners:** All

### To Do
- [ ] 🟡 Finalize presentation deck and speaking flow
- [ ] 🟡 Prepare backup demo path and screenshots
- [ ] 🟡 Confirm impact metrics and recommendations
- [ ] 🟡 Complete final team review and submission checks

### In Progress
- [ ] 🟡 Move active tasks here

### Done
- [ ] 🟢 Move completed tasks here

---

## Standup Template (copy each week)

### Standup — Week of __________
- Completed yesterday:
  - [ ] 🟢
- In progress today:
  - [ ] 🟡
- Blockers:
  - [ ] 🔴
- Next:
  - [ ] 🟡
