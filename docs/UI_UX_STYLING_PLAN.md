# RiskRadar Mobile UI/UX Styling Plan

## Purpose

This document is the implementation checklist for restyling the Expo React Native mobile app to match `RiskRadar_MobileApp_Wireframe.png` using the existing `/wireframe_icons` assets.

## Primary Goal

Replace the Expo starter UI with a branded, wireframe-accurate RiskRadar mobile interface that is simple to maintain and safe to extend.

## Success Criteria

- Main mobile screens visibly match the structure and branding direction of the wireframe.
- Colors, typography, spacing, and iconography are centralized in reusable theme tokens.
- Navigation elements use RiskRadar-branded visuals instead of Expo starter defaults.
- Screens render cleanly on both Android and iOS-sized layouts without overflow or broken alignment.
- The app starts, navigates, and lints without introducing runtime or TypeScript issues.

## Current Frontend Baseline

The current mobile frontend is located in `frontend/RiskRadar` and is still close to the Expo starter template.

Key current entry points:

- `frontend/RiskRadar/app/_layout.tsx`
- `frontend/RiskRadar/app/(tabs)/_layout.tsx`
- `frontend/RiskRadar/app/(tabs)/index.tsx`
- `frontend/RiskRadar/app/(tabs)/explore.tsx`
- `frontend/RiskRadar/app/modal.tsx`
- `frontend/RiskRadar/constants/theme.ts`
- `frontend/RiskRadar/components/themed-text.tsx`
- `frontend/RiskRadar/components/themed-view.tsx`

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
- Primary visual mode: light mode only for phase 1
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

Typography defaults:

- Base family: existing platform sans stack
- Screen title: `32/36`, bold
- Section title: `20/24`, semibold
- Card title: `16/20`, semibold
- Body: `15/22`, regular
- Meta: `12/16`, medium

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
- [x] Set light mode as the only required branded mode for phase 1.
- [x] Remove Expo starter comments.

### 3. `frontend/RiskRadar/app/_layout.tsx`

Purpose:

- Apply the branded navigation theme and ensure app-wide visual consistency.

Checklist:

- [ ] Replace the default React Navigation theme with a custom RiskRadar navigation theme.
- [ ] Align background colors with the new token system.
- [ ] Set status bar styling to match the new screen header treatment.
- [ ] Keep layout minimal and push colors into `theme.ts`.

### 4. `frontend/RiskRadar/app/(tabs)/_layout.tsx`

Purpose:

- Replace default tab visuals with branded mobile navigation that resembles the wireframe.

Checklist:

- [ ] Restyle the tab bar background, height, padding, and active state.
- [ ] Replace generic icons with `RiskRadar_STND_HomeBttn.png` and `RiskRadar_ALERT_HomeBttn.png` for the Home tab.
- [ ] Rename `Explore` to `Alerts` unless the team rejects that information model.
- [ ] Use a temporary vector icon only for the non-home tab if no wireframe asset fits.
- [ ] Ensure the selected tab is visually obvious and consistent with the wireframe.

### 5. `frontend/RiskRadar/app/(tabs)/index.tsx`

Purpose:

- Rebuild the home screen to match the wireframe’s main dashboard layout.

Checklist:

- [ ] Remove Expo starter content completely.
- [ ] Add a branded header with RiskRadar logo treatment.
- [ ] Add a top summary area for location/context and high-priority risk information.
- [ ] Add wireframe-style data cards for weather, air quality, pollen, and hazard alerts.
- [ ] Use hazard icons from the wireframe asset set instead of placeholder illustrations.
- [ ] Ensure card spacing and hierarchy visually match the mobile wireframe.
- [ ] Use a standard `ScrollView` layout, not `ParallaxScrollView`.
- [ ] Structure placeholder data to match eventual API-backed cards.

### 6. `frontend/RiskRadar/app/(tabs)/explore.tsx`

Purpose:

- Convert the current example page into a branded secondary screen aligned with the app’s content model.

Checklist:

- [ ] Remove all starter educational content and collapsible docs sections.
- [ ] Convert the screen into an alerts-focused list view.
- [ ] Use iconography and card patterns shared with the home screen.
- [ ] Maintain visual consistency with home while allowing a distinct secondary purpose.
- [ ] Remove all leftover Expo starter UI.

### 7. `frontend/RiskRadar/app/modal.tsx`

Purpose:

- Bring the modal styling in line with the rest of the app, or repurpose it if the wireframe suggests a detail panel or notification sheet.

Checklist:

- [ ] Replace generic modal text with a notification details surface.
- [ ] Apply branded spacing, type, and link/button treatment.
- [ ] Ensure modal visuals match the home and tab screens.

### 8. `frontend/RiskRadar/components/themed-text.tsx`

Purpose:

- Make text styling reusable and consistent across all screens.

Checklist:

- [ ] Expand `type` variants to `hero`, `sectionTitle`, `cardTitle`, `eyebrow`, and `meta`.
- [ ] Connect text styles directly to the typography tokens in `theme.ts`.
- [ ] Remove hard-coded starter link colors and swap them for branded link/action colors.
- [ ] Keep the component simple enough to avoid text-style duplication across screens.

### 9. `frontend/RiskRadar/components/themed-view.tsx`

Purpose:

- Keep surface styling consistent for cards, sections, and full-screen backgrounds.

Checklist:

- [ ] Ensure background token usage supports screen, card, and muted surface layers.
- [ ] Keep it lightweight and reusable for containers and content blocks.
- [ ] Avoid pushing card-specific styling into this file if a separate card component would be cleaner.

### 10. `frontend/RiskRadar/components/parallax-scroll-view.tsx`

Purpose:

- Decide whether this starter component should be retained, simplified, or removed.

Checklist:

- [ ] Do not use this component for phase 1 screen rebuilds.
- [ ] Replace current usage in `app/(tabs)/index.tsx` and `app/(tabs)/explore.tsx` with `ScrollView`.
- [ ] Leave the file in place only if removing it would create unnecessary churn.

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

- [ ] Create these components before final screen styling.
- [ ] Keep props tied to display intent rather than temporary placeholder copy.
- [ ] Match spacing and composition to the wireframe first, then simplify if needed.

### 13. `frontend/RiskRadar/app.json`

Purpose:

- Align app shell branding with the styled UI.

Checklist:

- [ ] Update splash/background colors to match the new brand palette.
- [ ] Confirm icon and splash assets are consistent with the wireframe branding direction.
- [ ] Ensure metadata still reflects the RiskRadar app correctly.

## Suggested Implementation Order

### Phase 1: Foundation

- [x] Copy assets into the mobile app.
- [x] Rebuild `constants/theme.ts` with real brand tokens.
- [ ] Update `themed-text.tsx` and `themed-view.tsx`.
- [ ] Decide whether `parallax-scroll-view.tsx` stays or is replaced.

### Phase 2: Shell

- [ ] Restyle `app/_layout.tsx`.
- [ ] Restyle `app/(tabs)/_layout.tsx`.
- [ ] Update `app.json` shell branding.

### Phase 3: Screens

- [ ] Rebuild `app/(tabs)/index.tsx`.
- [ ] Rebuild `app/(tabs)/explore.tsx`.
- [ ] Update `app/modal.tsx`.

### Phase 4: Polish

- [ ] Extract reusable branded components.
- [ ] Normalize spacing, icon sizing, and card hierarchy.
- [ ] Compare side-by-side against the wireframe and adjust for closer fidelity.

## Efficiency and Clean Runtime Guidelines

To keep the app efficient and stable while making it wireframe-accurate:

- Prefer static local image assets for branded icons rather than remote image fetching.
- Keep theme constants centralized so color changes do not require screen-by-screen edits.
- Avoid deeply nested layout wrappers when one styled container will do.
- Use reusable components for repeated card patterns.
- Avoid unnecessary animation unless it supports comprehension or navigation.
- Keep placeholder data shapes close to eventual API response structure.

## Verification Checklist

After implementation, run the following checks:

- [ ] `npm install` in `frontend/RiskRadar` if dependencies are not already present.
- [ ] `npm run lint`
- [ ] `npm run start`
- [ ] Verify the app loads without runtime errors.
- [ ] Verify the home and secondary tab screens render cleanly.
- [ ] Verify the tab bar is branded and readable on small screens.
- [ ] Verify icon assets load correctly on device and simulator.
- [ ] Verify text remains legible across screen sizes.
- [ ] Verify no leftover Expo starter copy remains.

## Definition of Done

This styling task should be considered complete when all of the following are true:

- The mobile frontend no longer looks like the Expo starter template.
- The main screens visibly resemble the RiskRadar wireframe structure.
- Colors, type, spacing, and iconography are consistent throughout the app.
- Navigation and cards look intentional and branded.
- The implementation runs cleanly and is easy for teammates to continue building on.

## Recommended Next Action

Implement in this order:

1. `frontend/RiskRadar/constants/theme.ts`
2. `frontend/RiskRadar/components/themed-text.tsx`
3. `frontend/RiskRadar/components/brand-header.tsx`
4. `frontend/RiskRadar/components/risk-card.tsx`
5. `frontend/RiskRadar/app/(tabs)/_layout.tsx`
6. `frontend/RiskRadar/app/(tabs)/index.tsx`
7. `frontend/RiskRadar/app/(tabs)/explore.tsx`
8. `frontend/RiskRadar/app/modal.tsx`

This order minimizes rework and front-loads the highest-visibility branding changes.