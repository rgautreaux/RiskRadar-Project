# INTEGRATION_NOTES.md

## RiskRadar S3 Integration & Merge Guidance

This document provides guidance for the S3 cross-track integration phase, including known risks, edge cases, and best practices for maintainers.

---

### 1. Merge Order & Ownership
- Follow the merge queue in UI_UX_STYLING_PLAN.md strictly
- Never merge Celeste or Ben tracks before their dependencies are ready
- Shared files (`theme.ts`, `_layout.tsx`) require sync approval if both tracks need edits

### 2. Known Integration Risks
- Route conflicts: Always resolve routing before styling
- Hard-coded colors: Remap to tokens in theme.ts
- Asset naming: Ensure all asset references match ASSET_MAP.md
- TypeScript errors: Run lint/tsc after each merge chunk

### 3. Edge Cases
- If a teammate's PR introduces a new primitive, update DESIGN_SYSTEM.md and onboarding docs
- If a merge introduces a regression, document it in QA_CHECKLIST.md and notify the team

### 4. Best Practices
- Communicate before merging any shared or teammate-owned file
- Document all integration decisions in this file
- After each merge, re-run manual QA and update docs as needed

### 5. April 2026 Route/Auth Contract Checklist
- Route ownership contract:
	`frontend/RiskRadar/app/(tabs)/index.tsx` is the launcher screen, while `frontend/RiskRadar/app/main/home.tsx` is the operational dashboard destination after auth or guest continuation.
- Auth hydration contract:
	`frontend/RiskRadar/app/_layout.tsx` must wait for `isLoading` in `AuthProvider` before rendering route stacks to avoid startup flicker and stale-token route races.
- Post-auth navigation contract:
	Login and registration should land on `frontend/RiskRadar/app/main/home.tsx` using replace-style navigation, not a push to launcher.
- Guest navigation contract:
	Guest continuation from `frontend/RiskRadar/app/(tabs)/index.tsx` should also use replace-style navigation into `/main/home` so back-stack loops do not trap users on launcher/auth screens.
- API/auth boundary contract:
	Frontend auth calls in `frontend/RiskRadar/contexts/auth-context.tsx` and `frontend/RiskRadar/utils/api.ts` must remain consistent with `backend/api/users.py` for register/login/me payload shape and error handling semantics.
- Protected path assumptions to verify with Ben and Celeste:
	`frontend/RiskRadar/app/auth/*` stays public; `frontend/RiskRadar/app/main/*` is primary post-auth flow; tab routes should not reintroduce duplicate Home logic that conflicts with `/main/home`.
- Shared UI consistency contract:
	Auth/home/nav screens should rely on existing primitives (`PrimaryButton`, `BrandHeader`, `ThemedText`, `ThemedView`) and token values from `frontend/RiskRadar/constants/theme.ts`.
- Required QA checks before merge:
	Register -> Home, Login -> Home, Guest -> Home, Logout -> launcher/auth recovery, invalid credentials, backend unavailable state, and back navigation from Home.
- Docs sync after each route/auth change:
	Update `docs/SPRINT_GOAL_TRACKING.md`, `docs/TODO.md`, and `docs/QA_CHECKLIST.md` whenever route ownership or auth-flow behavior changes.

---

_Last updated: April 10, 2026_
