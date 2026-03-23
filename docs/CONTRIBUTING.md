# CONTRIBUTING.md

## RiskRadar Frontend Contribution Guidelines

Thank you for contributing to RiskRadar! Please follow these guidelines to ensure a smooth and collaborative workflow.

---

### 1. Code Style & Linting
- Use the existing code style and formatting (see .eslintrc, .prettierrc if present)
- Run lint and TypeScript checks before submitting a PR

### 2. File & Feature Ownership
- Only edit files/components you own (see UI/UX Styling Plan for ownership)
- Do not edit Celeste- or Ben-owned files/features without explicit coordination
- All shared primitives (ThemedText, ThemedView, theme.ts) are open for documentation, onboarding, and test data improvements

### 3. Pull Request Process
- Branch from the latest main/develop branch
- Write clear PR titles and descriptions
- Reference related docs (DESIGN_SYSTEM.md, QA_CHECKLIST.md, etc.)
- Tag reviewers as appropriate

### 4. Documentation & Onboarding
- Update DESIGN_SYSTEM.md, ONBOARDING.md, and ASSET_MAP.md as needed
- Add usage examples and prop tables for new/updated primitives
- Cross-link docs for easy navigation

### 5. Test Data & QA
- Add or update mock data in mock/ for new primitives or edge cases
- Expand QA_CHECKLIST.md with new test cases as needed

### 6. Communication
- If unsure about file boundaries or ownership, clarify in this file and notify the team
- Propose new shared primitives or onboarding content in docs/ before implementation

---

_Last updated: March 23, 2026_
