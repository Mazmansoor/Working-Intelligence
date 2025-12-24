from playwright.sync_api import sync_playwright
import os

def verify_site():
    # Get absolute path to the current directory
    cwd = os.getcwd()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Check Homepage
        page.goto(f"file://{cwd}/index.html")
        page.screenshot(path="/home/jules/verification/home_depth.png")
        print("Captured home_depth.png")

        # 2. Check Setup Page (Markdown generated)
        page.goto(f"file://{cwd}/setup.html")
        page.screenshot(path="/home/jules/verification/setup_depth.png")
        print("Captured setup_depth.png")

        # 3. Check Module 1 (Markdown generated, depth check)
        page.goto(f"file://{cwd}/beginner/module-01.html")
        page.screenshot(path="/home/jules/verification/mod1_depth.png")
        print("Captured mod1_depth.png")

        # 4. Verify Navigation on a "Deep" page
        # Check if 'Setup' link exists
        setup_link = page.get_by_role("link", name="Setup")
        if setup_link.is_visible():
            print("Setup link is visible on Module 1")
        else:
            print("Setup link MISSING on Module 1")

        browser.close()

if __name__ == "__main__":
    verify_site()
