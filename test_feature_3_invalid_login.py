"""
Test Feature #3 - User login with invalid credentials

Steps:
1. Navigate to http://localhost:3000/login
2. Enter invalid credentials (email: "wrong@test.com", password: "wrongpassword")
3. Click login button
4. Verify error message is GENERIC (does NOT reveal which field is wrong)
5. Verify no session created (no redirect, still on /login)
6. Take screenshot
"""

import asyncio
from playwright.async_api import async_playwright
import sys
import os

async def test_feature_3():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("Step 1: Navigate to http://localhost:3000/login")
            await page.goto("http://localhost:3000/login", wait_until="networkidle", timeout=10000)
            await page.wait_for_timeout(1000)

            # Take initial screenshot
            await page.screenshot(path=".playwright-mcp/feature3_step1_login_page.png")
            print("✓ Login page loaded")

            print("\nStep 2: Enter invalid credentials")
            # Find and fill email field
            email_field = page.locator('input[type="email"], input[name="email"], input[id*="email"]').first
            await email_field.fill("wrong@test.com")
            print("  - Email: wrong@test.com")

            # Find and fill password field
            password_field = page.locator('input[type="password"], input[name="password"], input[id*="password"]').first
            await password_field.fill("wrongpassword")
            print("  - Password: wrongpassword")

            await page.screenshot(path=".playwright-mcp/feature3_step2_credentials_filled.png")

            print("\nStep 3: Click login button")
            # Find and click login button
            login_button = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first
            await login_button.click()

            # Wait for response
            await page.wait_for_timeout(2000)
            await page.screenshot(path=".playwright-mcp/feature3_step3_after_login_attempt.png")

            print("\nStep 4: Verify error message is GENERIC")
            # Check for error message
            error_message = None

            # Try various selectors for error messages
            error_selectors = [
                '.error',
                '[role="alert"]',
                '.alert-error',
                '.text-red-500',
                '.text-red-600',
                '[class*="error"]',
                'p:has-text("Invalid")',
                'div:has-text("Invalid")',
                'span:has-text("Invalid")'
            ]

            for selector in error_selectors:
                try:
                    error_el = page.locator(selector).first
                    if await error_el.is_visible(timeout=1000):
                        error_message = await error_el.text_content()
                        break
                except:
                    continue

            if error_message:
                error_message = error_message.strip()
                print(f"  - Error message found: '{error_message}'")

                # Check if message is generic (good)
                bad_messages = [
                    "email not found",
                    "user not found",
                    "wrong password",
                    "incorrect password",
                    "password incorrect",
                    "email does not exist",
                    "user does not exist"
                ]

                is_generic = True
                for bad in bad_messages:
                    if bad.lower() in error_message.lower():
                        print(f"  ✗ FAIL: Error message reveals which field is wrong!")
                        print(f"    Message contains: '{bad}'")
                        is_generic = False
                        break

                if is_generic:
                    # Check for generic messages (good)
                    generic_messages = [
                        "invalid credentials",
                        "invalid email or password",
                        "login failed",
                        "authentication failed",
                        "incorrect credentials"
                    ]

                    found_generic = False
                    for generic in generic_messages:
                        if generic.lower() in error_message.lower():
                            print(f"  ✓ PASS: Error message is generic and secure")
                            found_generic = True
                            break

                    if not found_generic:
                        print(f"  ? WARNING: Error message is not specific, but may not be clear enough")
                        print(f"    Consider using: 'Invalid credentials' or 'Invalid email or password'")
            else:
                print("  ✗ FAIL: No error message found!")
                is_generic = False

            print("\nStep 5: Verify no session created (no redirect, still on /login)")
            current_url = page.url
            print(f"  - Current URL: {current_url}")

            if "/login" in current_url:
                print("  ✓ PASS: Still on login page (no session created)")
                stayed_on_login = True
            else:
                print(f"  ✗ FAIL: Redirected to {current_url} (session may have been created!)")
                stayed_on_login = False

            print("\nStep 6: Take screenshot")
            await page.screenshot(path=".playwright-mcp/feature3_step6_final_verification.png", full_page=True)
            print("  ✓ Screenshot saved")

            # Final verdict
            print("\n" + "="*60)
            if error_message and is_generic and stayed_on_login:
                print("RESULT: PASSED ✓")
                print("  - Generic error message shown")
                print("  - No session created")
                print("  - User remains on login page")
                await browser.close()
                return True
            else:
                print("RESULT: FAILED ✗")
                if not error_message:
                    print("  - No error message displayed")
                elif not is_generic:
                    print("  - Error message reveals which field is wrong (security issue)")
                if not stayed_on_login:
                    print("  - User was redirected (possible session creation)")
                await browser.close()
                return False

        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            await page.screenshot(path=".playwright-mcp/feature3_error.png")
            await browser.close()
            return False

if __name__ == "__main__":
    result = asyncio.run(test_feature_3())
    sys.exit(0 if result else 1)
