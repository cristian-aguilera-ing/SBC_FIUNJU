
from playwright.sync_api import Page, expect, sync_playwright
import time
import random
import string

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

email = f"{get_random_string()}@example.com"
password = "password123"

def verify_profile_page(page: Page):
    print(f"Navigating to login page...")
    page.goto("http://localhost:3000/login")

    print(f"Filling credentials for {email}...")
    page.fill("input[type='email']", email)
    page.fill("input[type='password']", password)

    print("Clicking login...")
    page.click("button[type='submit']")

    print("Waiting for navigation to dashboard...")
    try:
        page.wait_for_url("**/dashboard", timeout=15000)
        print("Navigation successful!")
    except:
        print("Navigation timeout. Checking for errors...")
        if page.locator(".text-red-300").is_visible():
            print(f"Login error displayed: {page.locator('.text-red-300').inner_text()}")
        else:
            print("No error displayed, but navigation failed.")
        raise Exception("Login failed")

    print("Navigating to /perfil...")
    page.goto("http://localhost:3000/perfil")

    print("Waiting for profile to load...")
    expect(page.get_by_text("Cargando perfil...")).not_to_be_visible(timeout=15000)

    # Verify new section title
    expect(page.get_by_text("Finales para rendir ahora")).to_be_visible()

    # Verify Accordion R/A buttons exist (checking generally in the page)
    # We can check inside the first accordion (1° Año)
    page.click("text=1° Año")
    page.wait_for_timeout(1000)

    # Check for "R" and "A" buttons
    # Using get_by_title because we added titles to buttons
    expect(page.locator("button[title='Regularizar Materia']").first).to_be_visible()
    expect(page.locator("button[title='Aprobar Final']").first).to_be_visible()

    # Take screenshot
    page.screenshot(path="/home/jules/verification/verification.png", full_page=True)
    print("Verification passed!")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        import requests
        try:
            print(f"Registering user: {email}")
            requests.post("http://localhost:8000/users/register", json={
                "email": email,
                "password": password,
                "full_name": "Test User"
            })
        except Exception as e:
            print(f"Registration error: {e}")

        try:
            verify_profile_page(page)
        except Exception as e:
            print(f"Test failed: {e}")
            page.screenshot(path="/home/jules/verification/error.png")
        finally:
            browser.close()
