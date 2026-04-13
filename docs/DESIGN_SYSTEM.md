
# DESIGN_SYSTEM.md
## RiskRadar Design System Reference

This document summarizes the design tokens, palette roles, typography scales, and asset usage for the RiskRadar mobile app. It is intended as a reference for all contributors to ensure consistency and ease of onboarding.

---

## April 2026 Synchronization Note
All design tokens, asset usage, and UI/UX documentation are fully synchronized as of April 1, 2026. All planning and QA documentation is up to date and audit-ready.

---

## 1. Color Tokens (Light & Dark)

| Token            | Light Value  | Dark Value   | Usage                        |
|------------------|--------------|--------------|------------------------------|
| primary          | #0B5FA5      | #5FA8E6      | Main brand blue              |
| primaryDark      | #083B73      | #1B4F8A      | Darker blue, nav backgrounds |
| secondary        | #D9ECFB      | #1C2E40      | Accent, tab backgrounds      |
| warning          | #F59E0B      | #F8B84E      | Alert/warning                |
| danger           | #D64545      | #FF6B6B      | Critical/alert state         |
| surface          | #F6FAFD      | #0E1B2A      | Main background              |
| surfaceMuted     | #EAF2F8      | #16293B      | Card backgrounds, muted      |
| border           | #C7D8E6      | #2F4A63      | Card/border lines            |
| textPrimary      | #16324A      | #E6F2FF      | Main text                    |
| textSecondary    | #5B748A      | #A9C0D6      | Secondary text               |
| success          | #2E8B57      | #4FBF8A      | Success/positive             |
| white            | #FFFFFF      | #FFFFFF      | White surfaces               |
| shadow           | rgba(8,59,115,0.14) | rgba(8,59,115,0.14) | Card shadow                |

---

## 2. Typography

| Variant      | Size/Line | Weight   | Usage                        |
|--------------|-----------|----------|------------------------------|
| hero         | 32/36     | bold     | Screen hero titles           |
| title        | 20/24     | semibold | Section titles               |
| subtitle     | 16/20     | semibold | Section subtitles            |
| sectionTitle | 16/20     | semibold | Section headers              |
| cardTitle    | 16/20     | semibold | Card headings                |
| eyebrow      | 12/16     | semibold | Overline/metadata            |
| body         | 15/22     | regular  | Body text                    |
| meta         | 12/16     | medium   | Metadata/caption             |

---

## 3. Spacing & Radius

| Token | Value (px) |
|-------|------------|
| xs    | 4          |
| sm    | 8          |
| md    | 16         |
| lg    | 24         |
| xl    | 32         |
| card  | 16         |
| pill  | 24         |
| button| 8          |

---

## 4. Asset Usage Map

See UI/UX Plan Asset Mapping Table for full details. All assets are located in `frontend/RiskRadar/assets/` under branding, navigation, or hazards.

---

## 5. Themed Primitives

- `ThemedText`: Use for all text, supports variants and semantic color roles.
- `ThemedView`: Use for all containers, supports surface/background roles and elevation.

---

## 6. References
- [UI/UX Styling Plan](../docs/UI_UX_STYLING_PLAN.md)
- [Theme Tokens](../frontend/RiskRadar/constants/theme.ts)
- [Asset Mapping Table](../docs/UI_UX_STYLING_PLAN.md#asset-mapping-table)

---

_Last updated: March 23, 2026_
