# ONBOARDING.md

## RiskRadar Frontend Onboarding Guide

Welcome to the RiskRadar mobile frontend! This guide will help new contributors get started, understand the design system, and follow best practices for UI/UX consistency.

---

### 1. Project Structure
- All mobile code is in `frontend/RiskRadar/`
- Shared primitives: `components/themed-text.tsx`, `components/themed-view.tsx`
- Design tokens: `constants/theme.ts`
- Assets: `assets/icons/`, `assets/images/`
- Docs: `docs/`

### 2. Design System
- All colors, typography, and spacing are sourced from theme tokens (see DESIGN_SYSTEM.md)
- Use ThemedText and ThemedView for all new UI
- Never hard-code colors or font sizes in screens/components

### 3. Adding New Screens/Components
- Use existing primitives and tokens
- Document new props and usage with JSDoc
- Add usage examples to DESIGN_SYSTEM.md if introducing new patterns

### 4. Testing & QA
- Run lint and TypeScript checks before PRs
- Use QA_CHECKLIST.md for manual validation
- Add test cases or mock data for new primitives/components

### 5. Asset Management
- Place new icons/images in the correct subfolder under assets/
- Update ASSET_MAP.md if adding new assets

### 6. Who Owns What?
- See UI/UX Styling Plan for file/component ownership
- Avoid editing teammate-owned files/routes/features without coordination

### 7. Further Reading
- DESIGN_SYSTEM.md (tokens, typography, asset usage)
- QA_CHECKLIST.md (manual QA)
- ASSET_MAP.md (asset mapping)
- UI_UX_STYLING_PLAN.md (implementation plan)

---

## Quick Start

1. Clone the repo and install dependencies
2. Run lint and TypeScript checks: `npm run lint` / `npm run tsc`
3. Review DESIGN_SYSTEM.md and ONBOARDING.md
4. Use ThemedText and ThemedView for all new UI
5. Add or update mock data in mock/ for manual testing
6. Submit a PR following CONTRIBUTING.md

---

## Common Pitfalls

- Do NOT hard-code colors, font sizes, or spacing—always use theme tokens
- Do NOT edit teammate-owned files/routes/features without coordination (see UI/UX Styling Plan)
- Always update docs and mock data when adding new primitives
- Run lint/tsc before every PR to avoid CI failures

---

## Cross-Links

- [Design System](./DESIGN_SYSTEM.md)
- [QA Checklist](./QA_CHECKLIST.md)
- [Asset Map](./ASSET_MAP.md)
- [Contribution Guidelines](./CONTRIBUTING.md)

---

## Usage with Mock Data

- To manually test ThemedText, ThemedView, or token usage, import mock data from mock/alerts.json, mock/summaries.json, or mock/risk_cards.json.
- Example: Use mock/alerts.json to render a list of alert cards in a test screen or Storybook story.
- Always update mock data to cover new variants or edge cases for primitives.

---

## Storybook Proposal (if not set up)

- Storybook can be used to visualize all primitives and variants in isolation.
- If the team agrees, set up Storybook and add stories for ThemedText, ThemedView, and token usage.
- Document Storybook usage and story structure in ONBOARDING.md.

---

_Last updated: March 23, 2026_
