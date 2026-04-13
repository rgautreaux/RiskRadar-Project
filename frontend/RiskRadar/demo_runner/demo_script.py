# RiskRadar Automated Demo Script (Playwright, Python)

"""
This script automates the RiskRadar demo flow using Playwright for Python.
It follows the steps in docs/Demo/DEMO_SCRIPT.md and collects screenshots for evidence.

Requirements:
- pip install playwright
- playwright install

Usage:
- python demo_script.py
"""


# Credentials from environment variables
DEMO_EMAIL = os.getenv("RISKRADAR_DEMO_EMAIL")
DEMO_PASSWORD = os.getenv("RISKRADAR_DEMO_PASSWORD")

if not DEMO_EMAIL or not DEMO_PASSWORD:
    raise RuntimeError(
        "Demo credentials not set. Please set RISKRADAR_DEMO_EMAIL and RISKRADAR_DEMO_PASSWORD environment variables."
    )

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

# CONFIGURATION
BASE_URL = os.getenv("RISKRADAR_DEMO_URL", "http://localhost:8000")  # Set to your test frontend URL
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

# Ensure screenshot directory exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def screenshot_name(step):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.click('text=Login')
        await page.fill('input[name="email"]', DEMO_EMAIL)
        await page.fill('input[name="password"]', DEMO_PASSWORD)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. Landing page
        await page.goto(BASE_URL)
        await page.screenshot(path=screenshot_name("landing"))

        # 2. Login (adjust selectors as needed)
        await page.click('text=Login')
        await page.fill('input[name="email"]', 'demo_user@example.com')
        await page.fill('input[name="password"]', 'demopassword')
        await page.click('button[type="submit"]')
        await page.wait_for_selector('text=Dashboard')
        await page.screenshot(path=screenshot_name("dashboard"))

        # 3. Dashboard overview
        # (Assumes dashboard loads after login)
        # Add more assertions/screenshots as needed

        # 4. Zip-code search
        await page.fill('input[name="zipcode"]', '12345')
        await page.click('button:has-text("Search")')
        await page.wait_for_selector('text=Weather Report')
        await page.screenshot(path=screenshot_name("weather_report"))

        # 5. Alerts exploration
        await page.click('text=Alerts')
        await page.wait_for_selector('text=Active Alerts')
        await page.screenshot(path=screenshot_name("alerts"))

        # 6. Alert modal
        await page.click('.alert-row')  # Adjust selector for an alert row
        await page.wait_for_selector('.alert-modal')  # Adjust selector for modal
        await page.screenshot(path=screenshot_name("alert_modal"))
        await page.click('.alert-modal button:has-text("Close")')

        # 7. Settings & backend demo tools
        await page.click('text=Settings')
        await page.wait_for_selector('text=Notification Preferences')
        await page.screenshot(path=screenshot_name("settings"))
        # Optionally trigger health check/scrape and capture results

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_demo())
