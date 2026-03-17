# Rough/Unorganized Notes
## Project Questions
**1. User Privacy**: How will we handle user's privacy?
- Only ask users for zip/area code. 
- Does not use cookies to track users and  gather data without their consent. 
- No user accounts.

**2. Self-Sustainability**: How could this project stay afloat financially?
- One-Time Payment Methods?
    - Information deleted after payment is made. 
    - User needs to keep paying for the service (could be problematic)
- Subscription?
    - Need some way to store user payment method, which needs some way to keep track of users.

**3. Target Audience**: Who are we targeting?
- Travelers? 
    - Need weather information to plan trips
- Truckers?
    - Need weather information for traveling conditions. 
- Industry Owners?
    - Need weather information for project construction. 
- General Public?
    - Everyone needs weather information for different reasons (*LARGE SCOPE!!*)

## Action Items
1. Narrowing scope, writing user stories

2. How we make it work (system architecture)
    - Best practices
    
3. Security Questionnaire

4. Research AI tools
    - Work trees

5. Security considerations
    - Best practices

## Major Developments Since Initial Notes (Mar 2026)

### Backend and Database
- Implemented MariaDB schema alignment migration for scraper compatibility (`backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql`).
- Added environment-driven DB switching (`DATABASE_URL`) while preserving SQLite fallback.
- Validated scraper-to-database end-to-end write path (alerts + scrape_log) and added integration tests.
- Implemented retention cleanup framework with scheduler integration, archive tables, and retention tests.
- Added and verified additional backend regression coverage (including system scrape trigger path).

### Testing and Verification
- Repeated full backend verification sessions documented with green pytest runs in the active branch timeline.
- Added targeted integration/regression tests for scraper DB flow and retention behavior.
- Expanded README troubleshooting/testing guidance for repeatable validation.

### Frontend Mobile UI/UX
- Copied wireframe icon/image assets into Expo app asset directories.
- Rebuilt mobile theme token system and branded shell (`theme.ts`, root layout, tabs layout, app.json).
- Corrected Home tab icon placement behavior (standard vs alert state mapping).
- Audited wireframe fidelity and added a precise route-by-route wiring checklist in `docs/UI_UX_STYLING_PLAN.md`.

### Planning and Documentation
- Created and evolved `docs/TODO.md` into a sprint/stage tracking board with owners, dates, and status legend.
- Added reusable progress log templates and expanded `docs/GROUP_PROGRESS_LOG` with detailed session evidence.
- Maintained `docs/REBECCA-TRANSCRIPT.md` with cleanup, formatting normalization, and session-by-session updates.
- Synced planning docs (`TODO` + `UI_UX_STYLING_PLAN`) as the current stage-tracking source set.

### Remaining High-Priority Work
- Complete wireframe-accurate screen wiring for Home/Alerts/Modal with shared component production wiring.
- Reconcile Ben auth/main UX flow into current branded route shell.
- Continue end-to-end validation after each major frontend integration chunk.