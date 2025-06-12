import os
import json
from playwright.sync_api import sync_playwright

# Discourse base URL
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_JSON_URL = f"{BASE_URL}/c/courses/tds-kb/34.json"
AUTH_STATE_FILE = "auth.json"

def login_and_save_auth(playwright):
    print("🔐 Opening browser for login...")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Open login page
    page.goto(f"{BASE_URL}/login")
    print("👉 Please log in with Google. Then come back and press Enter here.")
    input("⏸️ Waiting... Press Enter after logging in.")

    # Save login session
    context.storage_state(path=AUTH_STATE_FILE)
    print("✅ Login session saved!")
    browser.close()

def fetch_and_save_data(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=AUTH_STATE_FILE)
    page = context.new_page()

    print("📡 Fetching posts with saved login session...")
    page.goto(CATEGORY_JSON_URL)
    text = page.inner_text("pre")

    data = json.loads(text)
    with open("discourse_posts.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Saved data to discourse_posts.json")
    browser.close()

def main():
    with sync_playwright() as playwright:
        if not os.path.exists(AUTH_STATE_FILE):
            login_and_save_auth(playwright)
        fetch_and_save_data(playwright)

if __name__ == "__main__":
    main()
