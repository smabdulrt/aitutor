from playwright.sync_api import sync_playwright, expect
import time
import sys

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Enable console logging for debugging
        page.on("console", lambda msg: print(f"Browser console [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser error: {err}"))

        try:
            print("Step 1: Loading page at http://localhost:3000...")
            page.goto("http://localhost:3000", timeout=60000, wait_until="networkidle")
            print("✓ Page loaded successfully")

            # Check if the side panel exists
            print("Step 2: Checking for side panel...")
            side_panel = page.locator(".side-panel")
            expect(side_panel).to_be_attached(timeout=5000)
            print("✓ Side panel found")

            # Give it a moment to make sure it's not in the middle of opening
            time.sleep(1)

            # Open the side panel if it's not already open
            print("Step 3: Opening side panel if needed...")
            is_open = "open" in (side_panel.get_attribute("class") or "")
            if not is_open:
                print("  → Clicking opener button...")
                page.locator(".opener").click()

            # Wait for the panel to be open
            expect(side_panel).to_have_class("side-panel open", timeout=10000)
            print("✓ Side panel is open")

            # Check if Logger component is present
            print("Step 4: Checking for Logger component...")
            logger = page.locator(".logger")
            expect(logger).to_be_attached(timeout=5000)
            print("✓ Logger component found")

            # Wait for WebSocket connections to establish (check for connection logs)
            print("Step 5: Waiting for WebSocket connections...")
            time.sleep(3)  # Give time for connections to establish

            # Check for any TA logs first (to verify TA messages are flowing)
            print("Step 6: Checking for TA log messages...")
            ta_logs = page.locator(".ta-log")
            try:
                expect(ta_logs.first).to_be_attached(timeout=15000)
                print("✓ TA log messages detected")
            except Exception as e:
                print(f"⚠ Warning: No TA log messages found yet: {e}")
                # Take a screenshot for debugging
                page.screenshot(path="jules-scratch/verification/debug_no_ta_logs.png")
                # Print all console logs
                print("\nDumping logger content for debugging:")
                logger_content = logger.inner_text()
                print(logger_content)

            # Wait for the TA's greeting message to appear in the log
            print("Step 7: Waiting for TA greeting message...")
            greeting_locator = page.get_by_text("Welcome back, Jules!")

            # Increase timeout because it might take a while for websockets to connect and TA to respond
            expect(greeting_locator).to_be_visible(timeout=30000)
            print("✓ TA greeting message found!")

            # Take a screenshot of the side panel which contains the console
            print("Step 8: Taking screenshot...")
            side_panel.screenshot(path="jules-scratch/verification/ta_integration_verification.png")
            print("✓ Screenshot saved to jules-scratch/verification/ta_integration_verification.png")

            print("\n✅ All verification steps passed!")

        except Exception as e:
            print(f"\n❌ Verification failed: {e}")
            # Take a debug screenshot
            page.screenshot(path="jules-scratch/verification/debug_failure.png")
            print("Debug screenshot saved to jules-scratch/verification/debug_failure.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)