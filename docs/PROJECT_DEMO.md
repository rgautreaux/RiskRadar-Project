# RiskRadar Project Demo Guide

This file is the presentation-facing demo reference for RiskRadar. It lists what can already be demonstrated live, what still needs to be implemented for a stronger demo, and the key operating notes the presenter should know before showing the app.

## Demo Goals

- Show RiskRadar as a complete environmental risk monitoring product, not just a collection of screens.
- Keep the presentation anchored on one clear user story: access the app, check a location, read a summary, inspect alerts, and understand next actions.
- Use live functionality wherever possible, but always have a fallback path if a data source is slow or unavailable.

## Implemented Demos

### 1. Landing, login, and guest entry

- The app opens to a branded landing screen with login, registration, and guest entry.
- Authenticated users can proceed to the dashboard immediately.
- Guest mode exists as a presentation-safe fallback if auth setup is not desirable during the demo.

### 2. Registration and authentication

- Users can register with name, email, password, and optional home zip code.
- Users can log in with email and password and receive a JWT-backed session.
- The backend exposes public login and registration endpoints and a current-user profile endpoint.

### 3. Dashboard overview

- The home screen shows the latest summary card and a risk assessment card.
- The dashboard supports zip-code search as the main entry into the location-based workflow.
- This is the best screen to use for the opening “product value” explanation.

### 4. Location drill-down

- The weather report screen fetches location information, recent alerts, and an AI-generated summary for a zip code.
- This screen demonstrates the core value proposition: raw environmental data becomes a readable, location-specific summary.

### 5. Alerts exploration

- The alerts view shows active alerts and hazard category chips.
- The alerts view now includes demo prioritization filters so critical alerts and major hazards can be surfaced first.
- The modal view provides a polished alert detail presentation with recommendations.
- These screens are useful for showing severity and alert context without leaving the app flow.

### 6. Backend credibility proof

- The backend exposes a health check endpoint for a simple system-status demo.
- The backend also exposes a manual scrape trigger for showing the live ingestion pipeline.
- The settings screen now includes in-app buttons for backend health checks and scrape-trigger demos.
- Swagger docs are available for a technical audience that wants the API layer, not only the app UI.

## Demos To Be Implemented or Strengthened

### 1. Persistent settings and preferences

- The settings screen currently includes demo controls that should persist reliably across app restarts.
- The home zip code should survive refreshes and be synchronized with the backend for logged-in users.
- Notification preferences should be clarified so the demo distinguishes between presentation-only toggles and real saved user settings.

### 2. Stronger state handling on the main flow

- Loading, empty, and error states should be visibly polished across home, weather report, alerts, and settings.
- If a live source fails, the presenter should see a graceful message rather than a stalled screen.

### 3. Alert prioritization demo

- Add clearer severity- or source-based prioritization so the audience can immediately see what matters most.
- If full filtering is too large for the current scope, use the existing alerts list and modal as the presentation path, then explain planned filtering.
- This is now partially implemented with demo filters, but it can still be expanded into richer backend-driven sorting or source-specific views.

### 4. Operations and trust demo

- Make the health check and scrape trigger easier to show during the presentation.
- This is now partially implemented through the settings screen, which offers both health checks and a scrape trigger action.
- If possible, add a more presenter-friendly summary view for the scrape result so the backend story is even faster to explain.

### 5. Repeatable demo rehearsal path

- Add a scripted or checklist-driven runbook for startup, login, search, weather report, alerts, and fallback handling.
- The demo should be repeatable from a clean boot without needing ad hoc exploration.

## Important Need-To-Know Information

### Dependencies

- Backend must be running before the app can fetch alerts, summaries, or user data.
- The mobile app reads the backend base URL from the local network setup, so the backend and device must be reachable on the same network.
- LLM summaries depend on configured API keys if live generation is part of the presentation.

### Recommended Presentation Order

1. Landing or login screen.
2. Home dashboard.
3. Zip-code search.
4. Weather report with AI summary and recent alerts.
5. Alerts view or alert modal.
6. Settings or personalization.
7. Backend health or Swagger docs only if the audience wants technical detail.

### Demo Fallback Rules

- If login is inconvenient, use guest mode.
- If the live weather report fails, show the alerts view and explain the on-demand location workflow.
- If the backend is unavailable, switch to Swagger docs or the health endpoint instead of waiting on a broken request.
- If external data is slow, keep the story moving by showing the dashboard summary and alert browsing path.

### Presenter Notes

- Keep the narrative focused on user value: early warning, readable summaries, and faster decisions.
- Do not over-explain every API call unless the audience asks for technical depth.
- Use the modal and weather report screens as the best visual moments in the demo.
- Call out reliability improvements only when they support the story of a stable, demo-ready system.

## Current Demo Status Summary

- Already demoable: landing/login, dashboard, zip search, weather report, alerts list, alert modal, health check, Swagger docs.
- Already demoable: landing/login, dashboard, zip search, weather report, alerts list, alert modal, health check, scrape trigger, Swagger docs.
- In progress or still to be strengthened: persistent settings, polished fallback states, richer alert prioritization, and a cleaner operations summary.
- Best live story today: show the product end to end from entry screen to location-based insight, then close with a brief backend trust proof.
