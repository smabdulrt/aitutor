import re
from playwright.sync_api import sync_playwright, Page, expect

def verify_next_question_functionality(page: Page):
    """
    This test verifies that clicking the 'Next Question' button
    loads a new question.
    """
    # 1. Arrange: Go to the application's homepage.
    # The application is running on localhost:3000.
    page.goto("http://localhost:3000/")

    # 2. Wait for the initial question to load.
    # We expect the question container to be visible and contain text.
    question_locator = page.locator(".question-text")
    expect(question_locator).to_be_visible(timeout=10000)
    expect(question_locator).not_to_be_empty()

    # Capture the text of the first question.
    initial_question_text = question_locator.inner_text()
    print(f"Initial question: {initial_question_text}")

    # Take a screenshot of the initial state.
    page.screenshot(path="jules-scratch/verification/initial-question.png")

    # 3. Act: Find the "Next Question" button and click it.
    next_button_locator = page.get_by_role("button", name="Next Question")
    expect(next_button_locator).to_be_enabled()
    next_button_locator.click()

    # 4. Assert: Wait for the question to change.
    # We expect the text content of the question element to be different
    # from the initial question's text.
    expect(question_locator).not_to_have_text(initial_question_text, timeout=10000)

    new_question_text = question_locator.inner_text()
    print(f"New question: {new_question_text}")

    # 5. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/verification.png")
    print("Screenshot of the new question taken.")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_next_question_functionality(page)
        finally:
            browser.close()

if __name__ == "__main__":
    main()