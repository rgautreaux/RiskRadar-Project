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

import asyncio
import os
from datetime import datetime

from playwright.async_api import async_playwright

# Credentials from environment variables
DEMO_EMAIL = os.getenv("RISKRADAR_DEMO_EMAIL")
DEMO_PASSWORD = os.getenv("RISKRADAR_DEMO_PASSWORD")

if not DEMO_EMAIL or not DEMO_PASSWORD:
    raise RuntimeError(
        "Demo credentials not set. Please set RISKRADAR_DEMO_EMAIL and RISKRADAR_DEMO_PASSWORD environment variables."
    )

# CONFIGURATION
BASE_URL = os.getenv("RISKRADAR_DEMO_URL", "http://localhost:8000")  # Set to your test frontend URL
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

# Ensure screenshot directory exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def screenshot_name(step):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(SCREENSHOT_DIR, f"{timestamp}_{step}.png")


async def run_demo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. Landing page
        await page.goto(BASE_URL)
        await page.screenshot(path=screenshot_name("landing"))

        # 2. Login
        await page.goto(f"{BASE_URL}/login")
        await page.fill('#email', DEMO_EMAIL)
        await page.fill('#password', DEMO_PASSWORD)
        await page.click('button:has-text("Sign In")')
        await page.wait_for_selector('text=Dashboard')
        await page.screenshot(path=screenshot_name("dashboard"))

        # 3. Dashboard overview
        # (Assumes dashboard loads after login)
        # Add more assertions/screenshots as needed

        # 4. Dashboard alerts overview
        alerts_list = page.locator('#alerts-list')
        await alerts_list.wait_for(state="visible")
        await page.screenshot(path=screenshot_name("dashboard_alerts"))

        # 5. Alerts exploration
        await page.click('text=Alerts')
        await alerts_list.wait_for(state="visible")
        await page.screenshot(path=screenshot_name("alerts"))

        # 6. Alert cards/details
        alert_items = alerts_list.locator('> *')
        if await alert_items.count() > 0:
            await alert_items.first.scroll_into_view_if_needed()
        await page.screenshot(path=screenshot_name("alert_details"))

        # 7. Settings & backend demo tools
        await page.click('text=Settings')
        await page.wait_for_selector('text=Profile & Preferences')
        await page.screenshot(path=screenshot_name("settings"))
        # Optionally trigger health check/scrape and capture results

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_demo())
