# RiskRadar Demo Script

This script provides a step-by-step guide for presenters to demonstrate all major features of the RiskRadar app, ensuring a smooth and repeatable demo experience.

---

## Pre-Demo Setup
- Ensure the backend server is running and reachable from the demo device.
- (Optional) Prepare demo user credentials, or be ready to use guest mode.
- (Optional) Have API keys configured for live LLM summaries if desired.

---

## Step-by-Step Demo Flow

### 1. Launch the App
- Open the RiskRadar app on your device.

### 2. Landing, Login, or Guest Entry
- Show the branded landing screen.
- Demonstrate both login (with prepared credentials) and guest entry as fallback.
- Explain the difference: authenticated users get personalized features; guest mode is for quick access or presentations.

### 3. Registration (Optional)
- Click 'Register' and fill in the form (name, email, password, optional home zip code).
- Submit and show successful registration flow.

### 4. Dashboard Overview
- After login/guest entry, highlight the dashboard:
  - Latest summary card
  - Risk assessment card
  - Zip-code search bar
- Explain this is the main entry point for users.

### 5. Location Drill-Down
- Use the zip-code search to look up a location.
- Show the weather report screen:
  - Location info
  - Recent alerts
  - AI-generated summary (if available)
- Emphasize how raw data is turned into readable, actionable insights.

### 6. Alerts Exploration
- Navigate to the 'Alerts' tab/view.
- Show active alerts, hazard category chips, and demo prioritization filters.
- Click on an alert to open the modal with detailed info and recommendations.
- Explain how users can quickly assess severity and context.

### 7. Settings & Backend Demo Tools
- Go to the 'Settings' page from the dashboard menu.
- Demonstrate customization:
  - Notification preferences
  - Tracked locations
  - Data sources
- Use the in-app backend demo tools:
  - Run a backend health check and show the result.
  - Trigger a scrape run and review the source-level outcomes.
- Mention that these tools are presentation-safe and useful for technical audiences.

### 8. (Optional) API/Swagger Docs
- If the audience is technical, show the Swagger docs or API endpoints for backend credibility.

---

## Fallbacks & Troubleshooting
- If login fails, use guest mode.
- If live data is slow/unavailable, focus on dashboard summaries and alert browsing.
- If backend is unreachable, show Swagger docs or health endpoint.

---

## Presenter Tips
- Keep the story focused on user value: early warning, readable summaries, and faster decisions.
- Use the modal and weather report screens as visual highlights.
- Only dive into technical/API details if prompted by the audience.
- Be ready to explain fallback paths and reliability improvements.

---

## End of Demo
- Recap the end-to-end flow: entry, location insight, alert review, and backend trust.
- Invite questions or deeper dives as appropriate.
