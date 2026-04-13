# RiskRadar Automated Demo Runner

This directory contains scripts and resources for automated demonstration and evidence collection of the RiskRadar web application.

## Getting Started

### 1. Install Playwright (Python)

```
pip install playwright
playwright install
```

### 2. Usage
- Run the demo script(s) in this directory to execute the automated demo flow and collect screenshots/artifacts.
- By default, scripts target a test/staging environment. **Never run against production.**

- `demo_script.py` — Main Playwright script that automates the demo flow: launches the app, logs in, navigates the dashboard, performs a zip-code search, explores alerts, opens an alert modal, visits settings, and collects screenshots at each step.
- `screenshots/` — Collected screenshots and artifacts

### 4. Safety
- Only use test accounts and data.
- Ensure the backend and frontend are running in a test environment.

### 5. Maintenance
- Update selectors and flows as the UI evolves.
- Keep this README and scripts up to date with demo requirements.

---

For questions, see the main project README or contact the RiskRadar team.
