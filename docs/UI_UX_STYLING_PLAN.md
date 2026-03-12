# RiskRadar Mobile UI/UX Styling Plan

## Purpose

This document defines the implementation plan for styling the Expo React Native mobile app so it matches the RiskRadar wireframe direction shown in `RiskRadar_MobileApp_Wireframe.png`, uses the existing icon assets in `/wireframe_icons`, and remains efficient, maintainable, and clean at runtime.

## Primary Goal

Make the current mobile app visually consistent with RiskRadar branding and wireframe intent while keeping the codebase simple enough to iterate on during the remaining project timeline.

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

## Asset Strategy

Expo static asset imports are most reliable when the files live inside the app project. Before UI implementation starts, copy the wireframe icons into a mobile-owned asset directory such as:

- `frontend/RiskRadar/assets/icons/`

Recommended organization:

- `frontend/RiskRadar/assets/icons/branding/`
- `frontend/RiskRadar/assets/icons/navigation/`
- `frontend/RiskRadar/assets/icons/hazards/`
- `frontend/RiskRadar/assets/images/wireframes/`

This avoids path issues and keeps the mobile app self-contained.

## Styling Direction

The wireframe should drive a visual system with these characteristics:

- Clear environmental-risk dashboard identity rather than generic app styling.
- Strong blue-led safety palette with high contrast text and soft data-card surfaces.
- Dense but readable information layout suitable for alerts, summaries, and at-a-glance hazard status.
- Rounded cards, intentional icon usage, and clean spacing between modules.
- Typography that feels operational and trustworthy rather than playful or default.

## Recommended Brand System

These values should be finalized during implementation, but the plan should assume a branded token set like the following:

- Primary: deep risk blue
- Secondary: light atmospheric blue
- Accent: alert orange or warning amber
- Surface: off-white or pale blue-gray
- Border: cool gray-blue
- Text primary: dark slate
- Text secondary: muted slate
- Success, warning, and danger semantic colors for alert states

Typography direction:

- Use a clean sans-serif stack that feels structured and readable.
- Keep titles bold and condensed in spacing.
- Use a smaller, restrained metadata size for timestamps, severity labels, and hazard summaries.

## File-by-File Implementation Checklist

### 1. `frontend/RiskRadar/assets/icons/`

Purpose:

- Store the copied wireframe icon assets inside the mobile app for direct import.

Checklist:

- [ ] Create `assets/icons/branding/`, `assets/icons/navigation/`, and `assets/icons/hazards/`.
- [ ] Copy the relevant files from `/wireframe_icons` into those folders.
- [ ] Keep file names consistent with the original asset names where practical.
- [ ] Add the wireframe image to `assets/images/wireframes/` for design reference if needed.

### 2. `frontend/RiskRadar/constants/theme.ts`

Purpose:

- Convert the current starter theme into the RiskRadar design token source of truth.

Checklist:

- [ ] Replace default Expo colors with a full RiskRadar brand palette.
- [ ] Add semantic tokens for `surface`, `surfaceMuted`, `border`, `danger`, `warning`, `success`, and `shadow`.
- [ ] Add spacing tokens such as `xs`, `sm`, `md`, `lg`, `xl`.
- [ ] Add radius tokens for cards, pills, and buttons.
- [ ] Expand typography tokens for title, subtitle, section label, card heading, body, and meta text.
- [ ] Keep light mode as the primary target unless the team specifically wants branded dark mode.
- [ ] Remove generic starter comments that no longer describe the project.

### 3. `frontend/RiskRadar/app/_layout.tsx`

Purpose:

- Apply the branded navigation theme and ensure app-wide visual consistency.

Checklist:

- [ ] Replace the default React Navigation theme with a custom RiskRadar navigation theme.
- [ ] Align background colors with the new token system.
- [ ] Set status bar styling to match the new screen header treatment.
- [ ] Keep layout minimal and push most styling decisions into shared constants.

### 4. `frontend/RiskRadar/app/(tabs)/_layout.tsx`

Purpose:

- Replace default tab visuals with branded mobile navigation that resembles the wireframe.

Checklist:

- [ ] Restyle the tab bar background, height, padding, and active state.
- [ ] Replace generic icons with RiskRadar navigation assets where appropriate.
- [ ] If image tabs are not practical, map icons to the closest branded visual treatment and label color system.
- [ ] Ensure the selected tab is visually obvious and consistent with the wireframe.
- [ ] Consider renaming tabs if the wireframe uses different information architecture than `Home` and `Explore`.

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
- [ ] Keep screen composition scrollable but visually segmented.
- [ ] Prepare components so real API data can replace placeholder content later without redesign.

### 6. `frontend/RiskRadar/app/(tabs)/explore.tsx`

Purpose:

- Convert the current example page into a branded secondary screen aligned with the app’s content model.

Checklist:

- [ ] Remove all starter educational content and collapsible docs sections.
- [ ] Convert the screen into a useful branded surface such as alerts feed, hazard explorer, or category browser.
- [ ] Use iconography and card patterns shared with the home screen.
- [ ] Maintain visual consistency with home while allowing a distinct secondary purpose.
- [ ] Ensure the screen works as a realistic extension of the wireframe rather than a leftover placeholder page.

### 7. `frontend/RiskRadar/app/modal.tsx`

Purpose:

- Bring the modal styling in line with the rest of the app, or repurpose it if the wireframe suggests a detail panel or notification sheet.

Checklist:

- [ ] Replace generic modal text with RiskRadar-relevant content.
- [ ] Apply branded spacing, type, and link/button treatment.
- [ ] Ensure modal visuals match the home and tab screens.

### 8. `frontend/RiskRadar/components/themed-text.tsx`

Purpose:

- Make text styling reusable and consistent across all screens.

Checklist:

- [ ] Expand `type` variants to include more UI-specific options like `hero`, `sectionTitle`, `cardTitle`, `eyebrow`, and `meta`.
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

- [ ] Evaluate whether parallax behavior matches the wireframe.
- [ ] If it does not match, replace it with a simpler `ScrollView`-based layout.
- [ ] If retained, restyle the header and remove all Expo-starter visual assumptions.
- [ ] Avoid decorative animation that conflicts with the wireframe’s more functional design.

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

Recommended new components:

- `section-header.tsx`
- `risk-card.tsx`
- `hazard-chip.tsx`
- `brand-header.tsx`
- `tab-bar-icon.tsx`

Checklist:

- [ ] Create reusable card and section components before building too many one-off styles into screen files.
- [ ] Keep props tied to display intent rather than temporary placeholder copy.
- [ ] Use the wireframe as the source for spacing and composition decisions.

### 13. `frontend/RiskRadar/app.json`

Purpose:

- Align app shell branding with the styled UI.

Checklist:

- [ ] Update splash/background colors to match the new brand palette.
- [ ] Confirm icon and splash assets are consistent with the wireframe branding direction.
- [ ] Ensure metadata still reflects the RiskRadar app correctly.

## Suggested Implementation Order

### Phase 1: Design System Foundation

- [ ] Copy assets into the mobile app.
- [ ] Rebuild `constants/theme.ts` with real brand tokens.
- [ ] Update `themed-text.tsx` and `themed-view.tsx`.
- [ ] Decide whether `parallax-scroll-view.tsx` stays or is replaced.

### Phase 2: Navigation and App Shell

- [ ] Restyle `app/_layout.tsx`.
- [ ] Restyle `app/(tabs)/_layout.tsx`.
- [ ] Update `app.json` shell branding.

### Phase 3: Core Screen Reconstruction

- [ ] Rebuild `app/(tabs)/index.tsx`.
- [ ] Rebuild `app/(tabs)/explore.tsx`.
- [ ] Update `app/modal.tsx`.

### Phase 4: Component Extraction and Polish

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

Start with `frontend/RiskRadar/constants/theme.ts`, `frontend/RiskRadar/app/(tabs)/_layout.tsx`, and `frontend/RiskRadar/app/(tabs)/index.tsx` first. Those three files will define most of the visible branding impact and make the rest of the screens easier to finish consistently.