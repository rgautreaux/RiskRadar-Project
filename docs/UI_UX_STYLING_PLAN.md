# Documentation Synchronization Note (Mar 31, 2026)

Phase 3 (Migration Logging & Monitoring) tasks and progress have been outlined and added to all relevant documentation. All planning and progress-tracking docs remain in sync.

This plan is in sync with README.md, GROUP_PROGRESS_LOG, AUTHORS.md, and TODO.md as of Mar 23, 2026. All UI/UX implementation, planning, and ownership details reflect the current project state and major developments.

# RiskRadar Mobile UI/UX Styling Plan

## Purpose

This document is the implementation checklist for restyling the Expo React Native mobile app to match `RiskRadar_MobileApp_Wireframe.png` using the existing `/wireframe_icons` assets.

## Primary Goal

Replace the Expo starter UI with a branded, wireframe-accurate RiskRadar mobile interface that is simple to maintain and safe to extend.

## Success Criteria

Main mobile screens visibly match the structure and branding direction of the wireframe.
Colors, typography, spacing, and iconography are centralized in reusable theme tokens.
App defaults to Light Mode on startup, with a visible toggle for users to switch between Light and Dark Mode. Remove hard lock in app.json; implement toggle in dashboard header or settings.
All theme tokens and styling logic support both modes, with no screen-level hard-coded color overrides.
Dashboard is the default landing page at app startup, not Login. Login is accessible from a card/tab/button on the Dashboard.
Remove the "Latest Summary" tab/page. Add a summary dropdown menu on the Dashboard for summary selection—no separate summary screen.
Add a Summary Search Bar to the Dashboard. Prompt users for topics of concern and display relevant summaries directly on the Dashboard (Quick Onboarding for info gathering).
Onboarding is quick and topic-driven via Dashboard search bar and dropdown.
Navigation elements use RiskRadar-branded visuals instead of Expo starter defaults.
Screens render cleanly on both Android and iOS-sized layouts without overflow or broken alignment.
The app starts, navigates, and lints without introducing runtime or TypeScript issues.

## Planning Sync Snapshot (Mar 18, 2026)

- All Rebecca-owned UI/UX tasks (token hygiene, contrast validation, asset wiring, notification art polish) are complete and verified.
- All color, typography, and spacing values are sourced from semantic tokens and palette roles in theme.ts.
- Asset wiring and notification art polish in explore.tsx and modal.tsx match wireframe fidelity.
- Documentation is current and synchronized with implementation state.

- Primary planning docs in active use are `docs/TODO.md` (sprint/stage board) and this plan (`docs/UI_UX_STYLING_PLAN.md`).
- There is currently no separate `STAGES` file under `docs/`; stage tracking is represented by sprint phases in `docs/TODO.md`.
- The "Precise Screen-by-Screen Wiring Checklist" section in this plan is the current source of truth for route-level implementation order and acceptance criteria.
- Mar 18 documentation sync pass: progress checkboxes were reconciled with completed Rebecca-track PR outcomes (R1/R2/R3), while pending cross-team polish and QA items remain explicitly open.

## Current Frontend Baseline

The current mobile frontend is located in `frontend/RiskRadar`.

As of Mar 17, 2026, a branch audit confirms two major UI/UX streams that must be merged intentionally:

- Branded shell and token system work (assets, `theme.ts`, `app/_layout.tsx`, `app/(tabs)/_layout.tsx`, and `app.json`) is present in Rebecca-aligned branches and is the strongest wireframe foundation.
- Ben's branch contains meaningful auth and onboarding UI prototypes (`app/auth/login.tsx`, `app/auth/registration.tsx`, and `app/main/home.tsx`) but uses an older route architecture and does not include the current branded shell/token files.

The current branch has a mixed completion state:

- Shell + branding foundations are implemented (`constants/theme.ts`, `app/_layout.tsx`, `app/(tabs)/_layout.tsx`, `app.json`, wireframe assets).
- `app/(tabs)/index.tsx` still needs full wireframe-accurate dashboard implementation.
- `app/(tabs)/explore.tsx` and `app/modal.tsx` are rebuilt from starter state but still require final asset wiring/polish for full wireframe fidelity.
- Shared reusable components created as contracts still need full production wiring on target screens.

Key current entry points:

- `frontend/RiskRadar/app/_layout.tsx`
- `frontend/RiskRadar/app/(tabs)/_layout.tsx`
- `frontend/RiskRadar/app/(tabs)/index.tsx`
- `frontend/RiskRadar/app/(tabs)/explore.tsx`
- `frontend/RiskRadar/app/modal.tsx`
- `frontend/RiskRadar/constants/theme.ts`
- `frontend/RiskRadar/components/themed-text.tsx`
- `frontend/RiskRadar/components/themed-view.tsx`

## Cross-Branch Reconciliation Baseline (Mar 16, 2026)

This plan now treats branch reconciliation as required implementation work, not optional cleanup.

Confirmed branch findings relevant to mobile UI/UX:

- `origin/Rebecca-Gautreaux-Work-Branch` and `origin/troubleshooting-and-testing-branch`: branded assets + shell + token improvements.
- `origin/Ben-Manuel-Work-Branch`: auth and onboarding-focused UI prototypes and alternate route flow.
- `origin/copilot/sub-pr-21`: asset and token alignment work that matches the branded shell direction.
- Other team branches currently inspected do not add distinct wireframe-ready mobile UI patterns beyond starter/existing shell content.

Branch integration rule set:

- Keep Rebecca-side shell and token architecture as base.
- Port Ben's UX intent and screen-level flow into the branded architecture, not vice versa.
- Do not merge older route structure directly if it regresses tab routing or theme integration.
- Resolve all route ownership explicitly before screen restyling.

## Branch Merge Checklist (Exact Keep/Port Decisions)

Use this checklist during merge work. Do not merge by directory-wide preference; merge by the decisions below.

### Merge Decision Table

| Target File/Area | Decision | Source of Truth | Required Action |
| --- | --- | --- | --- |
| `frontend/RiskRadar/constants/theme.ts` | Keep | Rebecca-side branches (`origin/Rebecca-Gautreaux-Work-Branch`, `origin/troubleshooting-and-testing-branch`) | Keep current token system and semantic naming. Do not import Ben branch color constants. |
| `frontend/RiskRadar/app/_layout.tsx` | Keep | Rebecca-side branches | Keep current root theme provider + stack setup. Only add route entries if needed for auth flow. |
| `frontend/RiskRadar/app/(tabs)/_layout.tsx` | Keep + small patch | Rebecca-side branches | Keep tab structure and branded tab bar. Patch home icon focused-state asset mapping after design validation. |
| `frontend/RiskRadar/app/(tabs)/index.tsx` | Port intent, rewrite implementation | Mixed: Rebecca architecture + Ben UX intent | Replace starter/parallax implementation. Port Ben flow concepts (welcome/guest/location risk context) into wireframe-accurate dashboard structure. |
| `frontend/RiskRadar/app/(tabs)/explore.tsx` | Keep path, new implementation | Rebecca-side architecture | Ben branch has no equivalent file. Fully rebuild as Alerts list screen using branded components. |
| `frontend/RiskRadar/app/modal.tsx` | Keep path, new implementation | Rebecca-side architecture | Ben branch has no equivalent file. Rework into branded notification details panel. |
| `frontend/RiskRadar/components/themed-text.tsx` | Keep path, rewrite variants | Rebecca-side architecture | Expand to hero/section/card/meta variants bound to `Typography` tokens. |
| `frontend/RiskRadar/components/themed-view.tsx` | Keep path, extend lightly | Rebecca-side architecture | Add token-driven surface support (`background`, `card`, `muted`) without adding card-specific logic. |
| `frontend/RiskRadar/components/parallax-scroll-view.tsx` | Keep temporarily, deprecate usage | Current branch | Remove usage from tab screens first. Delete later only if no remaining consumers. |
| `frontend/RiskRadar/assets/icons/**` and `assets/images/wireframes/**` | Keep | Rebecca-side and `origin/copilot/sub-pr-21` alignment | Keep existing mapped assets and file names unchanged. |
| `frontend/RiskRadar/app/auth/login.tsx` | Port + restyle | `origin/Ben-Manuel-Work-Branch` | Port Ben login UX structure, then restyle to RiskRadar tokens/components and current router flow. |
| `frontend/RiskRadar/app/auth/registration.tsx` | Port + restyle | `origin/Ben-Manuel-Work-Branch` | Port Ben registration UX structure, then restyle to RiskRadar tokens/components and current router flow. |
| `frontend/RiskRadar/app/main/home.tsx` | Do not port file directly | `origin/Ben-Manuel-Work-Branch` intent only | Port useful interaction patterns (zip entry, guest context, risk card placeholders) into final tab screens. Avoid reviving alternate route architecture. |
| `frontend/RiskRadar/app/(tabs)/index.tsx` from Ben branch | Do not keep | `origin/Ben-Manuel-Work-Branch` | Ben's `(tabs)/index.tsx` is onboarding-first and tied to older route assumptions; port only UX patterns, not direct file content. |
| Non-mobile branches and unrelated files | Ignore for mobile UI merge | N/A | Do not let unrelated backend/doc changes drive mobile merge decisions. |

### Step-by-Step Merge Execution Checklist

- [ ] Freeze base files before merge: `constants/theme.ts`, `app/_layout.tsx`, and `app/(tabs)/_layout.tsx`.
- [ ] Create or confirm auth route group ownership in current router before porting Ben auth screens.
- [ ] Port `app/auth/login.tsx` from Ben branch and restyle with branded tokens/components.
- [ ] Port `app/auth/registration.tsx` from Ben branch and restyle with branded tokens/components.
- [ ] Rebuild `app/(tabs)/index.tsx` using wireframe structure and Ben interaction intent (not Ben file body).
- [x] Rebuild `app/(tabs)/explore.tsx` as Alerts list screen (no Ben equivalent file).
- [x] Rebuild `app/modal.tsx` as branded notification/details surface (no Ben equivalent file).
- [x] Expand `components/themed-text.tsx` and `components/themed-view.tsx` before final screen pass.
- [x] Remove `ParallaxScrollView` usage from Home and Alerts screens.
- [x] Validate tab home icon focused-state mapping against wireframe active/inactive expectations.
- [ ] Run lint and app startup checks after each merge chunk to catch route regressions early.

### Conflict Resolution Rules (Required)

- If a conflict touches routing and styling simultaneously, resolve routing first and restyle second.
- If a conflict introduces hard-coded colors, keep tokenized styles and re-map values to `theme.ts`.
- If a Ben file conflicts with existing route groups, keep route groups from current branch and port only component-level UI logic.
- If uncertain during conflict resolution, prefer preserving compile-safe navigation flow over visual polish in that commit, then polish in next commit.

### PR-Ready Parallel Task List (Grouped by Owner)

Use the following PR split so work can proceed in parallel with minimal file overlap.

#### Shared (do first)

- [x] PR S1: Lock base architecture contract.
- Scope: `frontend/RiskRadar/constants/theme.ts`, `frontend/RiskRadar/app/_layout.tsx`, `frontend/RiskRadar/app/(tabs)/_layout.tsx`, and this plan file.
- Deliverable: Team agreement on keep/port decisions, route ownership, and icon focused-state expectation.
- Conflict guard: No feature code changes in this PR; documentation + tiny config-only updates.
- **Status (Mar 17, 2026):** Base files validated — all three frozen architecture files are correctly structured with branded theme tokens, tab routing, and root stack navigation. No changes were needed. `hooks/use-color-scheme.ts` created as missing dependency.

- [x] PR S2: Create new reusable component files and export contracts only.
- Scope: `frontend/RiskRadar/components/brand-header.tsx`, `frontend/RiskRadar/components/section-header.tsx`, `frontend/RiskRadar/components/risk-card.tsx`, `frontend/RiskRadar/components/hazard-chip.tsx`, `frontend/RiskRadar/components/tab-bar-icon.tsx`.
- Deliverable: Typed props, placeholder render bodies, and naming conventions agreed.
- Conflict guard: No screen wiring yet, so Ben, Rebecca, and Celeste can branch from this safely.
- **Status (Mar 17, 2026):** All 5 component skeleton files created with TypeScript props interfaces, JSDoc, and token-bound placeholder render bodies. 

#### Rebecca Owner Track

- [x] PR R1: Foundation primitives and tab-shell stabilization.
- Scope: `frontend/RiskRadar/components/themed-text.tsx`, `frontend/RiskRadar/components/themed-view.tsx`, `frontend/RiskRadar/app/(tabs)/_layout.tsx`.
- Deliverable: Token-driven text/view variants and validated home icon active/inactive mapping.
- Conflict guard: Do not edit `app/auth/*` in this PR.
- **Status (Mar 17, 2026):** COMPLETED. Created `themed-text.tsx` with 8 text variants (hero, title, subtitle, sectionTitle, cardTitle, eyebrow, body, meta) bound to typography tokens. Created `themed-view.tsx` with semantic surface modes (background, card, surfaceMuted) and optional elevation/padding. Fixed home tab icon mapping in `_layout.tsx` to show alert (red) for focused state and standard (green) for unfocused state.

- [x] PR R2: Alerts and modal rebuild on branded architecture.
- Scope: `frontend/RiskRadar/app/(tabs)/explore.tsx`, `frontend/RiskRadar/app/modal.tsx`.
- Deliverable: No Expo starter content, no parallax usage, shared branded component consumption.
- Conflict guard: Avoid edits to `app/(tabs)/index.tsx` while Ben track is active.
- **Status (Mar 17, 2026):** COMPLETED. Rebuilt `explore.tsx` as wireframe-accurate Alerts list screen with AlertCard components showing severity-based coloring (critical=red, warning=yellow, info=blue). Created `modal.tsx` as branded notification details panel with alert header, description, recommendations, and action button. Both use ThemedView and ThemedText for consistent styling.

- [x] PR R3: Parallax deprecation cleanup.
- Scope: `frontend/RiskRadar/components/parallax-scroll-view.tsx` and any remaining references.
- Deliverable: Either fully unused + retained temporarily, or removed after zero-consumer confirmation.
- Conflict guard: Merge only after R2 and B2 to avoid accidental reintroduction.
- **Status (Mar 17, 2026):** COMPLETED. Verified that `parallax-scroll-view.tsx` component does not exist in current codebase and no usage remains. All screens use standard ScrollView or View layouts.

#### Celeste Owner Track

- [ ] PR C1: Reusable branded component implementation (UI/UX styling pass).
- Scope: `frontend/RiskRadar/components/brand-header.tsx`, `frontend/RiskRadar/components/section-header.tsx`, `frontend/RiskRadar/components/risk-card.tsx`, `frontend/RiskRadar/components/hazard-chip.tsx`, `frontend/RiskRadar/components/tab-bar-icon.tsx`.
- Deliverable: Components move from placeholder contracts to branded implementations using locked token system (light + dark support, typography, spacing, iconography).
- Conflict guard: Do not modify `app/(tabs)/index.tsx`, `app/(tabs)/explore.tsx`, `app/modal.tsx`, or `app/auth/*` in this PR.

- [ ] PR C2: Component-level contrast and theming hardening.
- Scope: same component files as C1 plus any shared style helpers directly used by those components.
- Deliverable: Component-level Light Mode/Dark Mode contrast fixes and semantic surface consistency, with no screen-level logic changes.
- Conflict guard: Keep this PR focused on component internals only; avoid route or navigation file edits.

#### Ben Owner Track

- [ ] PR B1: Auth route integration (ported and restyled).
- Scope: `frontend/RiskRadar/app/auth/login.tsx`, `frontend/RiskRadar/app/auth/registration.tsx`, and minimal route registration changes in `frontend/RiskRadar/app/_layout.tsx` if required.
- Deliverable: Ben onboarding UX ported into branded tokens/components with current route groups.
- Conflict guard: No edits to themed primitives and no tab-screen rewrites in this PR.

- [ ] PR B2: Home screen flow integration from Ben intent.
- Scope: `frontend/RiskRadar/app/(tabs)/index.tsx`.
- Deliverable: Wireframe-aligned home dashboard that includes Ben's useful interaction patterns (guest context, zip input intent, risk placeholders) without older route architecture.
- Conflict guard: Do not modify `explore.tsx` or `modal.tsx` in this PR.

#### Shared Finalization Track

- [ ] PR S3: Cross-track integration and QA gate.
- Scope: merge fallout only across `app/(tabs)/index.tsx`, `app/(tabs)/explore.tsx`, `app/modal.tsx`, `app/auth/*`, `components/*`.
- Deliverable: Lint clean, startup verified, no dead-end routes, no starter copy, and no hard-coded off-brand color constants.
- Conflict guard: Only bugfix and integration edits; no new feature additions.

### Merge Queue (Recommended Order)

1. PR S1
2. PR S2
3. PR R1, PR C1, and PR B1 in parallel
4. PR R2, PR C2, and PR B2 in parallel
5. PR R3
6. PR S3

### File Ownership Guardrail (While Parallel Work Is Active)

- Ben owns changes in `frontend/RiskRadar/app/auth/*` and primary edits in `frontend/RiskRadar/app/(tabs)/index.tsx`.
- Rebecca owns changes in `frontend/RiskRadar/app/(tabs)/explore.tsx`, `frontend/RiskRadar/app/modal.tsx`, `frontend/RiskRadar/components/themed-text.tsx`, and `frontend/RiskRadar/components/themed-view.tsx`.
- Celeste owns changes in `frontend/RiskRadar/components/brand-header.tsx`, `frontend/RiskRadar/components/section-header.tsx`, `frontend/RiskRadar/components/risk-card.tsx`, `frontend/RiskRadar/components/hazard-chip.tsx`, and `frontend/RiskRadar/components/tab-bar-icon.tsx`.
- Shared-only files (`constants/theme.ts`, `app/_layout.tsx`, `app/(tabs)/_layout.tsx`) require a quick sync approval before merge if both tracks need edits.

## Available Branding Assets

The following asset directory already contains usable RiskRadar wireframe imagery and iconography:

- `/wireframe_icons/RiskRadar_MobileApp_Wireframe.png`
- `/wireframe_icons/RiskRadar_ALERT_Logo.png`
- `/wireframe_icons/RiskRadar_STND_Logo.png`
- `/wireframe_icons/RiskRadar_ALERT_HomeBttn.png`
- `/wireframe_icons/RiskRadar_STND_HomeBttn.png`
- `/wireframe_icons/RiskRadar_ALERT_NotifIcon.png`
- `/wireframe_icons/RiskRadar_STND_NotifIcon.png`
- `/wireframe_icons/RiskRadar_Weather_Icon.png`
- `/wireframe_icons/RiskRadar_AirQuality_Icon.png`
- `/wireframe_icons/RiskRadar_Pollen_Icon.png`
- `/wireframe_icons/RiskRadar_Pollution_Icon.png`
- `/wireframe_icons/RiskRadar_LocalEQ_Icon.png`
- `/wireframe_icons/RiskRadar_GlobalEQ_Icon.png`
- `/wireframe_icons/RiskRadar_LocalFlood_Icon.png`
- `/wireframe_icons/RiskRadar_GlobalFlood_Icon.png`
- `/wireframe_icons/RiskRadar_LocalWindEvent_Icon.png`
- `/wireframe_icons/RiskRadar_GlobalWindEvent_Icon.png`
- `/wireframe_icons/RiskRadar_LocalFIre_Icon.png`
- `/wireframe_icons/RiskRadar_GlobalFire_Icon.png`

## Locked Implementation Defaults

Use these defaults during implementation unless the team explicitly decides otherwise:

- Asset root: `frontend/RiskRadar/assets/icons/`
- Branding assets: `frontend/RiskRadar/assets/icons/branding/`
- Navigation assets: `frontend/RiskRadar/assets/icons/navigation/`
- Hazard assets: `frontend/RiskRadar/assets/icons/hazards/`
- Wireframe reference image: `frontend/RiskRadar/assets/images/wireframes/`
- Primary tab names: `Home` and `Alerts`
- Primary screen pattern: standard `ScrollView`, not parallax
- Primary visual mode: both Light Mode and Dark Mode
- Icon strategy: static local PNG assets for branded icons; vector icons only for utility actions
- Header component owner: `components/brand-header.tsx`
- Card component owner: `components/risk-card.tsx`
- Hazard badge/chip owner: `components/hazard-chip.tsx`

These defaults reduce implementation drift and keep the mobile app self-contained.

## Asset Mapping Table

Use this table as the exact default mapping for asset placement and first consumer location.

| Wireframe Asset File | Target Asset Path | First Consumer File | UI Purpose |
| --- | --- | --- | --- |
| `RiskRadar_MobileApp_Wireframe.png` | `assets/images/wireframes/RiskRadar_MobileApp_Wireframe.png` | None | Design reference only. |
| `RiskRadar_ALERT_Logo.png` | `assets/icons/branding/RiskRadar_ALERT_Logo.png` | `components/brand-header.tsx` | Alert-state header logo. |
| `RiskRadar_STND_Logo.png` | `assets/icons/branding/RiskRadar_STND_Logo.png` | `components/brand-header.tsx` | Default header logo. |
| `RiskRadar_ALERT_HomeBttn.png` | `assets/icons/navigation/RiskRadar_ALERT_HomeBttn.png` | `app/(tabs)/_layout.tsx` | Active home tab icon. |
| `RiskRadar_STND_HomeBttn.png` | `assets/icons/navigation/RiskRadar_STND_HomeBttn.png` | `app/(tabs)/_layout.tsx` | Inactive home tab icon. |
| `RiskRadar_ALERT_NotifIcon.png` | `assets/icons/navigation/RiskRadar_ALERT_NotifIcon.png` | `components/brand-header.tsx` | Alert-state notification button. |
| `RiskRadar_STND_NotifIcon.png` | `assets/icons/navigation/RiskRadar_STND_NotifIcon.png` | `components/brand-header.tsx` | Default notification button. |
| `RiskRadar_ALERT_NotifWindow.png` | `assets/icons/navigation/RiskRadar_ALERT_NotifWindow.png` | `app/modal.tsx` | Alert-state notification panel art. |
| `RiskRadar_STND_NotifWIndow.png` | `assets/icons/navigation/RiskRadar_STND_NotifWIndow.png` | `app/modal.tsx` | Default notification panel art. |
| `RiskRadar_ALERT_Text.png` | `assets/icons/branding/RiskRadar_ALERT_Text.png` | `components/brand-header.tsx` | Alert-state branded text. |
| `RiskRadar_STND_Text.png` | `assets/icons/branding/RiskRadar_STND_Text.png` | `components/brand-header.tsx` | Default branded text. |
| `RiskRadar_DataHeader_Format.png` | `assets/icons/branding/RiskRadar_DataHeader_Format.png` | `components/section-header.tsx` | Reference for section header structure. |
| `RiskRadar_Weather_Icon.png` | `assets/icons/hazards/RiskRadar_Weather_Icon.png` | `components/risk-card.tsx` | Weather card icon. |
| `RiskRadar_AirQuality_Icon.png` | `assets/icons/hazards/RiskRadar_AirQuality_Icon.png` | `components/risk-card.tsx` | Air quality card icon. |
| `RiskRadar_Pollen_Icon.png` | `assets/icons/hazards/RiskRadar_Pollen_Icon.png` | `components/risk-card.tsx` | Pollen card icon. |
| `RiskRadar_Pollution_Icon.png` | `assets/icons/hazards/RiskRadar_Pollution_Icon.png` | `components/risk-card.tsx` | Pollution card icon. |
| `RiskRadar_Local_Icon.png` | `assets/icons/navigation/RiskRadar_Local_Icon.png` | `components/brand-header.tsx` | Local scope indicator. |
| `RiskRadar_DEST_Global_Icon.png` | `assets/icons/navigation/RiskRadar_DEST_Global_Icon.png` | `app/(tabs)/explore.tsx` | Global destination/scope indicator. |
| `RiskRadar_GEN_Global_Icon.png` | `assets/icons/navigation/RiskRadar_GEN_Global_Icon.png` | `app/(tabs)/explore.tsx` | Generic global scope indicator. |
| `RiskRadar_LocalEQ_Icon.png` | `assets/icons/hazards/RiskRadar_LocalEQ_Icon.png` | `components/hazard-chip.tsx` | Local earthquake icon. |
| `RiskRadar_GlobalEQ_Icon.png` | `assets/icons/hazards/RiskRadar_GlobalEQ_Icon.png` | `components/hazard-chip.tsx` | Global earthquake icon. |
| `RiskRadar_LocalFlood_Icon.png` | `assets/icons/hazards/RiskRadar_LocalFlood_Icon.png` | `components/hazard-chip.tsx` | Local flood icon. |
| `RiskRadar_GlobalFlood_Icon.png` | `assets/icons/hazards/RiskRadar_GlobalFlood_Icon.png` | `components/hazard-chip.tsx` | Global flood icon. |
| `RiskRadar_LocalWindEvent_Icon.png` | `assets/icons/hazards/RiskRadar_LocalWindEvent_Icon.png` | `components/hazard-chip.tsx` | Local wind event icon. |
| `RiskRadar_GlobalWindEvent_Icon.png` | `assets/icons/hazards/RiskRadar_GlobalWindEvent_Icon.png` | `components/hazard-chip.tsx` | Global wind event icon. |
| `RiskRadar_LocalFIre_Icon.png` | `assets/icons/hazards/RiskRadar_LocalFIre_Icon.png` | `components/hazard-chip.tsx` | Local fire icon. |
| `RiskRadar_GlobalFire_Icon.png` | `assets/icons/hazards/RiskRadar_GlobalFire_Icon.png` | `components/hazard-chip.tsx` | Global fire icon. |

## Styling Direction

The wireframe should drive a visual system with these characteristics:

- Clear environmental-risk dashboard identity rather than generic app styling.
- Strong blue-led safety palette with high contrast text and soft data-card surfaces.
- Dense but readable information layout suitable for alerts, summaries, and at-a-glance hazard status.
- Rounded cards, intentional icon usage, and clean spacing between modules.
- Typography that feels operational and trustworthy rather than playful or default.

## Locked Brand System

Use these values as the first-pass token set in `frontend/RiskRadar/constants/theme.ts`.

### Light Mode Tokens

- Primary: `#0B5FA5`
- Primary dark: `#083B73`
- Secondary: `#D9ECFB`
- Accent warning: `#F59E0B`
- Accent danger: `#D64545`
- Surface: `#F6FAFD`
- Surface muted: `#EAF2F8`
- Border: `#C7D8E6`
- Text primary: `#16324A`
- Text secondary: `#5B748A`
- Success: `#2E8B57`
- White: `#FFFFFF`

### Dark Mode Tokens

- Primary: `#5FA8E6`
- Primary dark: `#1B4F8A`
- Secondary: `#1C2E40`
- Accent warning: `#F8B84E`
- Accent danger: `#FF6B6B`
- Surface: `#0E1B2A`
- Surface muted: `#16293B`
- Border: `#2F4A63`
- Text primary: `#E6F2FF`
- Text secondary: `#A9C0D6`
- Success: `#4FBF8A`
- White: `#FFFFFF`

Typography defaults:

- Base family: existing platform sans stack
- Screen title: `32/36`, bold
- Section title: `20/24`, semibold
- Card title: `16/20`, semibold
- Body: `15/22`, regular
- Meta: `12/16`, medium

## Current Status Snapshot

- Done in current baseline: wireframe assets copied into `frontend/RiskRadar/assets/`, branded tokens implemented in `frontend/RiskRadar/constants/theme.ts`, app shell theming updated in `frontend/RiskRadar/app/_layout.tsx`, branded tab bar applied in `frontend/RiskRadar/app/(tabs)/_layout.tsx`, and Expo app metadata updated in `frontend/RiskRadar/app.json`.
- Done in Ben branch (to be integrated): `app/auth/login.tsx`, `app/auth/registration.tsx`, and `app/main/home.tsx` provide usable UX flow and content structure for onboarding and location-risk search.
- Verified: lint/startup and backend test validations have been run in recent sessions; maintain re-validation after each wiring chunk.
- Still pending: full wireframe-accurate Home route rebuild, final Alerts/Modal icon-asset wiring, shared component production wiring (C1/C2), and Ben auth/main flow reconciliation into current shell.
- Resolved risk: Home tab icon state mapping was corrected so standard icon appears on Home and alert variant appears in Alerts-route context.

## File-by-File Implementation Checklist

### 1. `frontend/RiskRadar/assets/icons/`

Purpose:

- Store the copied wireframe icon assets inside the mobile app for direct import.

Checklist:

- [x] Create `assets/icons/branding/`, `assets/icons/navigation/`, and `assets/icons/hazards/`.
- [x] Copy each file according to the Asset Mapping Table above.
- [x] Keep the original file names unchanged.
- [x] Add the wireframe image to `assets/images/wireframes/`.

### 2. `frontend/RiskRadar/constants/theme.ts`

Purpose:

- Convert the current starter theme into the RiskRadar design token source of truth.

Checklist:

- [x] Replace default Expo colors with a full RiskRadar brand palette.
- [x] Add semantic tokens for `surface`, `surfaceMuted`, `border`, `danger`, `warning`, `success`, and `shadow`.
- [x] Add spacing tokens such as `xs`, `sm`, `md`, `lg`, `xl`.
- [x] Add radius tokens for cards, pills, and buttons.
- [x] Expand typography tokens for title, subtitle, section label, card heading, body, and meta text.
- [x] Add a dedicated dark palette (do not mirror `light` values) using the locked Dark Mode token set.
- [x] Ensure `Colors.dark` contains semantic keys matching `Colors.light` one-to-one.
- [x] Ensure navigation, card, border, and status colors are readable in dark mode.
- [x] Remove Expo starter comments.

### 3. `frontend/RiskRadar/app/_layout.tsx`

Purpose:

- Apply the branded navigation theme and ensure app-wide visual consistency.

Checklist:

- [x] Replace the default React Navigation theme with a custom RiskRadar navigation theme.
- [x] Align background colors with the new token system.
- [x] Set status bar styling dynamically for Light Mode and Dark Mode.
- [x] Keep layout minimal and push colors into `theme.ts`.

### 4. `frontend/RiskRadar/app/(tabs)/_layout.tsx`

Purpose:

- Replace default tab visuals with branded mobile navigation that resembles the wireframe.

Checklist:

- [x] Restyle the tab bar background, height, padding, and active state.
- [x] Replace generic icons with `RiskRadar_STND_HomeBttn.png` and `RiskRadar_ALERT_HomeBttn.png` for the Home tab.
- [x] Rename `Explore` to `Alerts` unless the team rejects that information model.
- [x] Use a temporary vector icon only for the non-home tab if no wireframe asset fits.
- [x] Ensure the selected tab is visually obvious and consistent with the wireframe.
- [x] Validate `RiskRadar_ALERT_HomeBttn.png` and `RiskRadar_STND_HomeBttn.png` focused-state mapping matches wireframe intent.
- [x] Ensure tab bar surfaces, labels, and icon contrast pass readability in both light and dark modes.

### 5. `frontend/RiskRadar/app/(tabs)/index.tsx`

Purpose:

Rebuild the home screen to match the wireframe’s main dashboard layout.

Checklist:

- [ ] Remove Expo starter content completely.
- [ ] Add a branded header with RiskRadar logo treatment.
- [ ] Add a top summary area for location/context and high-priority risk information.
- [ ] Add wireframe-style data cards for weather, air quality, pollen, and hazard alerts.
	- [ ] Weather card must display both the exact temperature and the "feels like" temperature (factoring in wind chill and other environmental conditions).
	- [ ] Weather card should provide advice on how to dress and what to pack for travelers, based on current and forecasted conditions.
	- [ ] Prompt users for their expected length of stay in the location and offer a packing guide tailored to the weather in the region.
- [ ] Use hazard icons from the wireframe asset set instead of placeholder illustrations.
- [ ] Ensure card spacing and hierarchy visually match the mobile wireframe.
- [ ] Use a standard `ScrollView` layout, not `ParallaxScrollView`.
- [ ] Structure placeholder data to match eventual API-backed cards.

### 6. `frontend/RiskRadar/app/(tabs)/explore.tsx`

Purpose:

- Convert the current example page into a branded secondary screen aligned with the app’s content model.

Progress note:

- Core rebuild completed in PR R2. Remaining icon-asset and composition refinements are tracked in the Precise Screen-by-Screen section (Route D).

Checklist:

- [x] Remove all starter educational content and collapsible docs sections.
- [x] Convert the screen into an alerts-focused list view.
- [x] Use iconography and card patterns shared with the home screen.
- [x] Maintain visual consistency with home while allowing a distinct secondary purpose.
- [x] Remove all leftover Expo starter UI.

### 7. `frontend/RiskRadar/app/modal.tsx`

Purpose:

- Bring the modal styling in line with the rest of the app, or repurpose it if the wireframe suggests a detail panel or notification sheet.

Progress note:

- Core rebuild completed in PR R2. Remaining notification art/state wiring refinements are tracked in the Precise Screen-by-Screen section (Route E).

Checklist:

- [x] Replace generic modal text with a notification details surface.
- [x] Apply branded spacing, type, and link/button treatment.
- [x] Ensure modal visuals match the home and tab screens.

### 8. `frontend/RiskRadar/components/themed-text.tsx`

Purpose:

- Make text styling reusable and consistent across all screens.

Checklist:

- [x] Expand `type` variants to `hero`, `sectionTitle`, `cardTitle`, `eyebrow`, and `meta`.
- [x] Connect text styles directly to the typography tokens in `theme.ts`.
- [ ] Remove hard-coded starter link colors and swap them for branded link/action colors.
- [ ] Keep the component simple enough to avoid text-style duplication across screens.
- [ ] Validate all text variants for contrast in both light and dark surfaces.

### 9. `frontend/RiskRadar/components/themed-view.tsx`

Purpose:

- Keep surface styling consistent for cards, sections, and full-screen backgrounds.

Checklist:

- [x] Ensure background token usage supports screen, card, and muted surface layers.
- [x] Keep it lightweight and reusable for containers and content blocks.
- [x] Avoid pushing card-specific styling into this file if a separate card component would be cleaner.
- [x] Support explicit semantic surface modes (`background`, `card`, `surfaceMuted`) across light and dark themes.

### 9.5 `frontend/RiskRadar/hooks/use-color-scheme.ts` and `frontend/RiskRadar/hooks/use-theme-color.ts`

Purpose:

- Ensure runtime theme selection and color lookup are stable and predictable in both modes.

Checklist:

- [ ] Confirm `use-color-scheme.ts` returns the active scheme consistently on device and emulator.
- [ ] Confirm `use-theme-color.ts` resolves semantic keys from `Colors.light`/`Colors.dark` without fallback drift.
- [ ] Remove any behavior that silently forces light values when dark values exist.

### 10. `frontend/RiskRadar/components/parallax-scroll-view.tsx`

Purpose:

- Decide whether this starter component should be retained, simplified, or removed.

Checklist:

- [x] Do not use this component for phase 1 screen rebuilds.
- [x] Replace current usage in `app/(tabs)/index.tsx` and `app/(tabs)/explore.tsx` with `ScrollView`.
- [x] Confirmed no `parallax-scroll-view.tsx` file/consumers remain in current codebase (R3 cleanup).

### 11. `frontend/RiskRadar/components/ui/icon-symbol.tsx`

Purpose:

- Support any remaining vector-based icons when a static image asset is not the right fit.

Checklist:

- [ ] Keep this component only for fallback/system icons.
- [ ] Do not rely on generic Material icons for the app’s primary branded hazard visuals.
- [ ] Update mappings only if needed for secondary actions like chevrons or utility navigation.

### 12. `frontend/RiskRadar/components/`

Purpose:

- Introduce reusable branded UI primitives instead of repeating layout and styling screen by screen.

Required new components:

- `section-header.tsx`
- `risk-card.tsx`
- `hazard-chip.tsx`
- `brand-header.tsx`
- `tab-bar-icon.tsx`

Checklist:

- [x] Create these components before final screen styling.
- [ ] Keep props tied to display intent rather than temporary placeholder copy.
- [ ] Match spacing and composition to the wireframe first, then simplify if needed.

### 13. `frontend/RiskRadar/app.json`

Purpose:

- Align app shell branding with the styled UI.

Checklist:

- [x] Update splash/background colors to match the new brand palette.
- [x] Confirm icon and splash assets are consistent with the wireframe branding direction.
- [x] Ensure metadata still reflects the RiskRadar app correctly.

### 14. `frontend/RiskRadar/app/auth/` and `frontend/RiskRadar/app/main/`

Purpose:

- Integrate Ben branch onboarding and guest-entry UX into the branded route architecture.

Checklist:

- [ ] Port and restyle `app/auth/login.tsx` using RiskRadar token/color/typography primitives.
- [ ] Port and restyle `app/auth/registration.tsx` using shared input/button styles from branded components.
- [ ] Merge `app/main/home.tsx` user flow concepts into the final wireframe-aligned Home/Alerts information model.
- [ ] Ensure auth and guest navigation target current route groups without breaking `(tabs)` behavior.
- [ ] Remove hard-coded non-brand purple values (`#4F46E5` family) during integration.

## Precise Screen-by-Screen Wiring Checklist

Use this section as the exact route wiring sequence for wireframe fidelity. Complete each screen block fully before moving to the next.

### A. Root Navigation Shell (`frontend/RiskRadar/app/_layout.tsx`)

- [ ] Confirm stack order and route groups include `(tabs)`, `auth/*`, `main/*`, and `modal` without broken back navigation.
- [ ] Keep `ThemeProvider` bound to semantic tokens from `constants/theme.ts` only.
- [ ] Ensure status bar style flips correctly for light and dark schemes.
- [ ] Verify no screen-level hard-coded hex colors are introduced in this file.

Exit criteria:

- [ ] App launches to tab shell with no navigation warnings.
- [ ] Auth screens and modal can be reached and dismissed cleanly.

### B. Tab Shell (`frontend/RiskRadar/app/(tabs)/_layout.tsx`)

- [x] Keep Home tab icon wired to local assets: `assets/icons/navigation/RiskRadar_STND_HomeBttn.png` and `assets/icons/navigation/RiskRadar_ALERT_HomeBttn.png`.
- [x] Keep Alerts tab label and ensure icon strategy is finalized: branded PNG via `components/tab-bar-icon.tsx` or temporary vector fallback.
- [x] Set tab bar dimensions, paddings, and label styles to match wireframe proportions.
- [x] Confirm focused/unfocused Home icon mapping against design intent and document the final mapping in code comments.

Exit criteria:

- [x] Tab bar looks branded on both iOS and Android sizes.
- [x] Home and Alerts tabs are visually distinct in active/inactive states.

### C. Home Dashboard Route (`frontend/RiskRadar/app/(tabs)/index.tsx`)

Header wiring:

- [ ] Render `components/brand-header.tsx` at the top of the screen.
- [ ] Wire `isAlert` state from placeholder risk status (temporary boolean until API integration).
- [ ] Wire notification tap to `router.push('/modal')`.

Summary/context wiring:

- [ ] Add location/scope summary row under header (local vs global scope placeholder).
- [ ] Add high-priority risk banner/card using semantic `danger`/`warning` tokens only.

Primary card stack wiring:

- [ ] Render reusable `components/risk-card.tsx` instances for Weather, Air Quality, Pollen, and Pollution.
- [ ] Use hazard assets, not vector placeholders:
	- [ ] `assets/icons/hazards/RiskRadar_Weather_Icon.png`
	- [ ] `assets/icons/hazards/RiskRadar_AirQuality_Icon.png`
	- [ ] `assets/icons/hazards/RiskRadar_Pollen_Icon.png`
	- [ ] `assets/icons/hazards/RiskRadar_Pollution_Icon.png`
- [ ] Use `ScrollView` (no parallax component).
- [ ] Keep placeholder data shape aligned with expected API fields (title, value, severity, timestamp, trend).

Exit criteria:

- [ ] No Expo starter content remains on Home.
- [ ] Home visually matches wireframe hierarchy: branded header -> context -> risk cards.

### D. Alerts Route (`frontend/RiskRadar/app/(tabs)/explore.tsx`)

Progress note:

- Core route rebuild was completed in PR R2; remaining items in this subsection are final wiring/polish tasks.

Header and scope wiring:

- [ ] Replace plain text header with `components/section-header.tsx` using Alerts title and count.
- [ ] Add scope indicator assets near header as required:
	- [ ] `assets/icons/navigation/RiskRadar_GEN_Global_Icon.png`
	- [ ] `assets/icons/navigation/RiskRadar_DEST_Global_Icon.png`

List wiring:

- [ ] Render alert rows/cards using reusable `risk-card` or dedicated alert-card pattern (single shared component style system).
- [ ] Replace icon placeholders with real hazard icons based on alert type/severity mapping.
- [ ] Add optional `components/hazard-chip.tsx` row for affected hazard categories.
- [ ] Keep severity color usage strictly tokenized (`danger`, `warning`, `primary`).

Exit criteria:

- [ ] Alerts list contains no placeholder geometry-only icons.
- [ ] Header, card spacing, and typography align with Home screen system.

### E. Modal Route (`frontend/RiskRadar/app/modal.tsx`)

Progress note:

- Core route rebuild was completed in PR R2; remaining items in this subsection are final asset wiring/polish tasks.

- [ ] Replace placeholder notification panel visuals with real notification panel art:
	- [ ] `assets/icons/navigation/RiskRadar_ALERT_NotifWindow.png`
	- [ ] `assets/icons/navigation/RiskRadar_STND_NotifWIndow.png`
- [ ] Use branded heading/body/meta text variants from `components/themed-text.tsx`.
- [ ] Keep CTA button style consistent with primary action buttons used on Home.
- [ ] Ensure close, dismiss, and Android back behaviors all return to previous route.

Exit criteria:

- [ ] Modal reads as a branded RiskRadar detail sheet, not a starter modal.
- [ ] No generic placeholder icon blocks remain.

### F. Login Route (`frontend/RiskRadar/app/auth/login.tsx`)

- [ ] Port Ben flow structure while preserving current route shell.
- [ ] Replace hard-coded color values with `Colors[scheme]` semantic tokens.
- [ ] Reuse branded button/input spacing conventions from Home and shared components.
- [ ] Add brand header treatment (full `brand-header` or compact variant).
- [ ] Ensure successful login routes to `(tabs)` target without dead-end intermediate routes.

Exit criteria:

- [ ] Login styling matches app brand and wireframe tone.
- [ ] No purple legacy palette remains.

### G. Registration Route (`frontend/RiskRadar/app/auth/registration.tsx`)

- [ ] Port Ben registration UX content and validation layout.
- [ ] Reuse the same tokenized input/button styles as Login.
- [ ] Keep typography and spacing aligned with Home + Login.
- [ ] Ensure submit/back navigation respects auth route group and returns correctly.

Exit criteria:

- [ ] Registration looks consistent with the branded shell.
- [ ] Route transitions to/from Login and Tabs are stable.

### H. Shared Component Wiring Prerequisites (`frontend/RiskRadar/components/`)

- [ ] `brand-header.tsx`: finish production implementation and wire logo/text/notification assets.
- [ ] `section-header.tsx`: support title + subtitle/count + optional right-side icon/action.
- [ ] `risk-card.tsx`: support icon, title, value/description, severity badge, timestamp.
- [ ] `hazard-chip.tsx`: support icon + label + local/global variant style.
- [ ] `tab-bar-icon.tsx`: centralize PNG tab icon logic where feasible to avoid per-screen drift.

Exit criteria:

- [ ] All screen routes consume shared components instead of duplicating card/header markup.

### I. Screen-by-Screen QA Gate (Run After A-H)

- [ ] Home route: all four primary hazard cards use wireframe PNG icons.
- [ ] Alerts route: list icons and chips use wireframe PNG assets; no square placeholders.
- [ ] Modal route: notification window art appears in correct state (alert/standard).
- [ ] Login/Registration: tokenized colors only; no off-brand hard-coded values.
- [ ] Tab bar: active/inactive states are obvious and match documented mapping.
- [ ] Light and dark modes both render legible text and surface contrast.
- [ ] `npm run lint` and `npm run start` both pass after wiring completion.

## Suggested Implementation Order

### Phase 0: Branch Reconciliation

- [ ] Freeze `frontend/RiskRadar/constants/theme.ts` and shell layouts as base architecture.
- [ ] Port Ben branch UX flows (auth + guest entry + zip search intent) into the base architecture.
- [ ] Resolve route ownership for `(tabs)`, `auth/*`, and any `main/*` successors before visual polish.

### Phase 1: Foundation

- [x] Copy assets into the mobile app.
- [ ] Rebuild `constants/theme.ts` with complete light and dark brand tokens.
- [x] Update `themed-text.tsx` and `themed-view.tsx`.
- [ ] Validate `use-color-scheme.ts` and `use-theme-color.ts` behavior for both modes.
- [x] Decide whether `parallax-scroll-view.tsx` stays or is replaced.

### Phase 2: Shell

- [x] Restyle `app/_layout.tsx`.
- [x] Restyle `app/(tabs)/_layout.tsx`.
- [x] Update `app.json` shell branding.

### Phase 3: Screens

- [ ] Rebuild `app/(tabs)/index.tsx`.
- [x] Rebuild `app/(tabs)/explore.tsx` (core rebuild complete; final polish/wiring tracked below).
- [x] Update `app/modal.tsx` (core rebuild complete; final polish/wiring tracked below).

### Phase 4: Polish

- [ ] Extract reusable branded components.
- [ ] Normalize spacing, icon sizing, and card hierarchy.
- [ ] Compare side-by-side against the wireframe and adjust for closer fidelity.

### Phase 4.5: Signature UX Details Pass

- [ ] Complete all items in the `Signature UX Details` section below.
- [ ] Capture before/after screenshots for Home, Alerts, Modal, Login, and Registration to confirm visible non-starter identity.
- [ ] Validate that each signature detail is token-driven or component-driven (no screen-local one-off styling).

### Phase 5: Branch-Integrated QA

- [ ] Validate both guest and authenticated entry paths.
- [ ] Confirm no old-route regressions from Ben branch integration.
- [ ] Confirm all screens consume shared tokens instead of screen-local color/style constants.
- [ ] Validate complete Light Mode and Dark Mode parity across Home, Alerts, Modal, and Auth flows.

## Efficiency and Clean Runtime Guidelines

To keep the app efficient and stable while making it wireframe-accurate:

- Prefer static local image assets for branded icons rather than remote image fetching.
- Keep theme constants centralized so color changes do not require screen-by-screen edits.
- Avoid deeply nested layout wrappers when one styled container will do.
- Use reusable components for repeated card patterns.
- Avoid unnecessary animation unless it supports comprehension or navigation.
- Keep placeholder data shapes close to eventual API response structure.

## Signature UX Details


#### Dashboard Summary Drop-down UX (Assigned to Ben)

- [ ] Add a drop-down or scrollable list UI element at the top or in a prominent dashboard section for summary selection.
- [ ] Populate the drop-down/list with available summary titles or brief descriptions (fetched from API or placeholder data).
- [ ] When a user selects a summary, display the full summary content below the drop-down/list, updating dynamically.
- [ ] Ensure the user can scroll through available summaries, select one, and read its full content without navigating away from the dashboard.
- [ ] Style the drop-down/list and summary display to match RiskRadar branding and maintain accessibility/contrast standards.
- [ ] Test the summary selection and display flow for both mobile platforms.

**Responsibility:** Ben (Home Dashboard route: `frontend/RiskRadar/app/(tabs)/index.tsx`)
Purpose:

- Operationalize small but intentional UI details so the app feels distinctly RiskRadar-owned rather than library-default.

Implementation checklist (complete all):

- [ ] **SD1 - Branded Header Identity:** `components/brand-header.tsx` must render logo + branded text treatment + notification icon state (`standard` and `alert`) using local PNG assets only. No fallback to generic icon for primary brand marks.
- [ ] **SD2 - Scope Identity Chip:** Add a reusable local/global scope indicator pattern (icon + label + surface treatment) used consistently on Home and Alerts headers.
- [ ] **SD3 - Severity Visual Language:** Standardize severity styling across `risk-card.tsx`, `hazard-chip.tsx`, and Alerts rows using one shared severity map (`danger`, `warning`, `primary`, `success`) and one badge shape family.
- [ ] **SD4 - Data Freshness Meta Pattern:** Every primary risk card and alert row includes a consistent freshness/timestamp line style (icon optional, text required) using `meta` typography tokens.
- [ ] **SD5 - Card Personality System:** Risk cards include one distinctive RiskRadar treatment beyond base container styles (for example: severity rail, icon plate, or status corner marker) implemented once in shared component logic.
- [ ] **SD6 - Signature CTA Treatment:** Primary action buttons on Home, Modal, Login, and Registration use one shared visual recipe (radius, padding, text weight, pressed-state feedback) tied to theme tokens.
- [ ] **SD7 - Stateful Empty/Error/Loading Surfaces:** Home and Alerts each define branded empty/loading/error states with RiskRadar copy tone and icon treatment; no default spinner-only or plain text-only fallback.
- [ ] **SD8 - Auth Personality Alignment:** Login and Registration include compact brand-header treatment and shared input styling (label, helper/error text, focus ring) with no purple legacy values.
- [ ] **SD9 - Motion Micro-Details:** Add subtle, purposeful motion in at least two places (for example card entrance stagger and notification panel reveal) with durations between 120ms and 280ms and no decorative-only animation loops.
- [ ] **SD10 - Tab Bar Ownership Detail:** `tab-bar-icon.tsx` centralizes branded tab icon state behavior and includes one explicit code comment documenting active/inactive mapping rationale against wireframe intent.

Acceptance gate:

- [ ] Run a quick visual QA pass where all SD1-SD10 items are demonstrably visible in the app and can be traced to shared components/tokens.
- [ ] Confirm there are no remaining primary UI regions that look like Expo starter defaults.

## Verification Checklist

After implementation, run the following checks:

- [x] `npm install` in `frontend/RiskRadar` if dependencies are not already present.
- [x] `npm run lint`
- [ ] `npm run start`
- [ ] Verify the app loads without runtime errors.
- [ ] Verify the home and secondary tab screens render cleanly.
- [ ] Verify the tab bar is branded and readable on small screens.
- [ ] Verify icon assets load correctly on device and simulator.
- [ ] Verify text remains legible across screen sizes.
- [ ] Verify no leftover Expo starter copy remains.
- [ ] Verify auth entry (`login` and `registration`) works with current router groups.
- [ ] Verify guest flow reaches wireframe-aligned Home experience without dead-end routes.
- [ ] Verify all core screens in Light Mode have correct brand colors and contrast.
- [ ] Verify all core screens in Dark Mode have correct brand colors and contrast.
- [ ] Verify toggling system theme updates surfaces and text without requiring app restart.
- [ ] Verify all `Signature UX Details` items (SD1-SD10) are complete and visually evident on target routes.
- [ ] Verify before/after screenshots are captured for Home, Alerts, Modal, Login, and Registration.

## Definition of Done

This styling task should be considered complete when all of the following are true:

- The mobile frontend no longer looks like the Expo starter template.
- The main screens visibly resemble the RiskRadar wireframe structure.
- Colors, type, spacing, and iconography are consistent throughout the app in both Light Mode and Dark Mode.
- Navigation and cards look intentional and branded.
- Signature details (SD1-SD10) are implemented and consistently visible across core routes.
- The implementation runs cleanly and is easy for teammates to continue building on.

## Recommended Next Action

Implement in this order:

1. Route reconciliation pass: map Ben's `auth/*` and `main/home` flows into the current route shell.
2. `frontend/RiskRadar/components/themed-text.tsx` and `frontend/RiskRadar/components/themed-view.tsx`
3. `frontend/RiskRadar/components/brand-header.tsx` and `frontend/RiskRadar/components/section-header.tsx`
4. `frontend/RiskRadar/components/risk-card.tsx`, `frontend/RiskRadar/components/hazard-chip.tsx`, and `frontend/RiskRadar/components/tab-bar-icon.tsx`
5. `frontend/RiskRadar/app/(tabs)/index.tsx` and Ben flow integration points
6. `frontend/RiskRadar/app/(tabs)/explore.tsx` and `frontend/RiskRadar/app/modal.tsx`
7. `frontend/RiskRadar/components/parallax-scroll-view.tsx` (retain or deprecate after replacement)

This order minimizes rework by reconciling branch architecture first, then finishing shared primitives before replacing remaining starter screens.
