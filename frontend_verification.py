
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

    page.goto("http://localhost:3000/login")

    # Wait for inputs
    page.fill("input[type='email']", email)
    page.fill("input[type='password']", password)

    # Click login
    page.click("button[type='submit']")

    # Wait for navigation to dashboard.
    try:
        page.wait_for_url("**/dashboard", timeout=5000)
    except:
        print("Login might have failed or timeout. Checking for error message.")
        if page.locator(".text-red-300").is_visible():
            print(f"Login error: {page.locator('.text-red-300').inner_text()}")
            raise Exception("Login failed")

    # Now navigate to profile
    page.goto("http://localhost:3000/perfil")

    # Wait for profile data to load
    expect(page.get_by_text("Cargando perfil...")).not_to_be_visible(timeout=10000)

    # 2. Verify that removed fields are NOT present
    content = page.content()

    assert "Horas de Estudio" not in content, "Found 'Horas de Estudio'"
    assert "Colegio Secundario" not in content, "Found 'Colegio Secundario'"
    assert "Método Preferido" not in content, "Found 'Método Preferido'"
    assert "Facilidad de Aprendizaje" not in content, "Found 'Facilidad de Aprendizaje'"
    assert "Entorno de Estudio" not in content, "Found 'Entorno de Estudio'"
    assert "Realizas Actividad Física" not in content, "Found 'Realizas Actividad Física'"

    # We kept 'Equipamiento Informático' and 'Condición Laboral'
    expect(page.get_by_text("Equipamiento Informático")).to_be_visible()
    expect(page.get_by_text("Condición Laboral")).to_be_visible()

    # 3. Verify Subject Selection Logic (Basic check)
    expect(page.get_by_text("Cursando Ahora")).to_be_visible()

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
