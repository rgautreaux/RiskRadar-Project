# QA_CHECKLIST.md

## RiskRadar UI/UX QA Checklist

This checklist is for use during the S3 QA/integration phase and for manual validation after each major merge. It covers navigation, theming, accessibility, and device layout checks.

---

### 1. Navigation & Routing
- [ ] App launches to Dashboard (Home) by default
- [ ] Login and Registration accessible from Dashboard
- [ ] Alerts screen accessible from tab bar
- [ ] Modal/notification panel opens and closes as expected
- [ ] No dead-end or broken routes

### 2. Theming & Visuals
- [ ] All screens use tokenized colors (no hard-coded values)
- [ ] Light Mode and Dark Mode toggle works and persists
- [ ] Tab bar icons match wireframe (active/inactive states)
- [ ] Card, surface, and background colors match design system
- [ ] Typography variants render as specified

### 3. Layout & Responsiveness
- [ ] No overflow or broken alignment on iOS and Android
- [ ] Cards, chips, and headers have correct spacing and radius
- [ ] All icons/images render at correct size and aspect

### 4. Accessibility
- [ ] All text passes color contrast (WCAG AA)
- [ ] Text scales with system font size
- [ ] Touch targets are at least 44x44px
- [ ] All interactive elements are accessible by screen reader

### 5. Alerts & Modal
- [ ] Alerts list shows all severity colors (critical, warning, info)
- [ ] Modal displays alert details, recommendations, and action button
- [ ] Modal art matches alert state (default/alert)

### 6. Regression/Smoke Tests
- [ ] Login, registration, and logout flows work
- [ ] Dashboard summary dropdown and search bar (when implemented) work
- [ ] No runtime or TypeScript errors on startup
- [ ] Lint passes with no warnings

---

_Last updated: March 23, 2026_
