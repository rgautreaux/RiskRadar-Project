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

---

_Last updated: March 23, 2026_
