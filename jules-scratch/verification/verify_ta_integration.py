from playwright.sync_api import sync_playwright, expect
import time

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:3000", timeout=60000, wait_until="networkidle")

            # Open the side panel if it's not already open
            side_panel = page.locator(".side-panel")

            # Give it a moment to make sure it's not in the middle of opening
            time.sleep(1)

            is_open = "open" in (side_panel.get_attribute("class") or "")
            if not is_open:
                 page.locator(".opener").click()

            # Wait for the panel to be open
            expect(side_panel).to_have_class("side-panel open", timeout=10000)

            # Wait for the TA's greeting message to appear in the log.
            greeting_locator = page.get_by_text("Welcome back, Jules!")

            # Increase timeout because it might take a while for websockets to connect and TA to respond
            expect(greeting_locator).to_be_visible(timeout=30000)

            # Take a screenshot of the side panel which contains the console.
            side_panel.screenshot(path="jules-scratch/verification/ta_integration_verification.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()