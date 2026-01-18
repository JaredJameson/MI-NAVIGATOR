/**
 * Test Feature #3 - User login with invalid credentials
 *
 * Steps:
 * 1. Navigate to http://localhost:3000/login
 * 2. Enter invalid credentials (email: "wrong@test.com", password: "wrongpassword")
 * 3. Click login button
 * 4. Verify error message is GENERIC (does NOT reveal which field is wrong)
 * 5. Verify no session created (no redirect, still on /login)
 * 6. Take screenshot
 */

const { chromium } = require('playwright');

async function testFeature3() {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    // Listen to console messages
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

    try {
        console.log("Step 1: Navigate to http://localhost:3000/auth/login");
        await page.goto("http://localhost:3000/auth/login", { waitUntil: "load", timeout: 30000 });

        // Debug: Check what's on the page
        console.log("  - Page loaded, checking content...");
        await page.waitForTimeout(5000); // Wait for React to hydrate

        const bodyText = await page.locator('body').textContent();
        console.log("  - Body text preview:", bodyText.substring(0, 200));

        // Wait for the email input to be visible (React needs time to hydrate)
        console.log("  - Waiting for login form to load...");
        await page.waitForSelector('input#email', { timeout: 20000 });

        // Take initial screenshot
        await page.screenshot({ path: ".playwright-mcp/feature3_step1_login_page.png", fullPage: true });
        console.log("✓ Login page loaded");

        console.log("\nStep 2: Enter invalid credentials");

        // Find and fill email field using ID (from the login page source)
        await page.fill('input#email', "wrong@test.com");
        console.log("  - Email: wrong@test.com");

        // Find and fill password field using ID
        await page.fill('input#password', "wrongpassword");
        console.log("  - Password: wrongpassword");

        await page.screenshot({ path: ".playwright-mcp/feature3_step2_credentials_filled.png" });

        console.log("\nStep 3: Click login button");
        // Find and click login button
        const loginButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first();
        await loginButton.click();

        // Wait for response
        await page.waitForTimeout(2000);
        await page.screenshot({ path: ".playwright-mcp/feature3_step3_after_login_attempt.png" });

        console.log("\nStep 4: Verify error message is GENERIC");
        // Check for error message
        let errorMessage = null;

        // Wait a bit for the error to appear
        await page.waitForTimeout(1000);

        // Try various selectors for error messages
        const errorSelectors = [
            '.bg-red-50',
            '[role="alert"]',
            '.text-red-700',
            '.text-red-600',
            'div:has-text("Incorrect")',
            'div:has-text("Invalid")',
            'div:has-text("error")',
            '[class*="red"]'
        ];

        for (const selector of errorSelectors) {
            try {
                const errorEl = page.locator(selector).first();
                if (await errorEl.isVisible({ timeout: 1000 })) {
                    errorMessage = await errorEl.textContent();
                    if (errorMessage && errorMessage.trim().length > 0) {
                        break;
                    }
                }
            } catch (e) {
                continue;
            }
        }

        let isGeneric = false;
        let stayedOnLogin = false;

        if (errorMessage) {
            errorMessage = errorMessage.trim();
            console.log(`  - Error message found: '${errorMessage}'`);

            // Check if message is generic (good)
            const badMessages = [
                "email not found",
                "user not found",
                "wrong password",
                "incorrect password",
                "password incorrect",
                "email does not exist",
                "user does not exist"
            ];

            isGeneric = true;
            for (const bad of badMessages) {
                if (errorMessage.toLowerCase().includes(bad.toLowerCase())) {
                    console.log(`  ✗ FAIL: Error message reveals which field is wrong!`);
                    console.log(`    Message contains: '${bad}'`);
                    isGeneric = false;
                    break;
                }
            }

            if (isGeneric) {
                // Check for generic messages (good)
                const genericMessages = [
                    "invalid credentials",
                    "invalid email or password",
                    "login failed",
                    "authentication failed",
                    "incorrect credentials"
                ];

                let foundGeneric = false;
                for (const generic of genericMessages) {
                    if (errorMessage.toLowerCase().includes(generic.toLowerCase())) {
                        console.log(`  ✓ PASS: Error message is generic and secure`);
                        foundGeneric = true;
                        break;
                    }
                }

                if (!foundGeneric) {
                    console.log(`  ? WARNING: Error message is not specific, but may not be clear enough`);
                    console.log(`    Consider using: 'Invalid credentials' or 'Invalid email or password'`);
                }
            }
        } else {
            console.log("  ✗ FAIL: No error message found!");
            isGeneric = false;
        }

        console.log("\nStep 5: Verify no session created (no redirect, still on /auth/login)");
        const currentUrl = page.url();
        console.log(`  - Current URL: ${currentUrl}`);

        if (currentUrl.includes("/auth/login")) {
            console.log("  ✓ PASS: Still on login page (no session created)");
            stayedOnLogin = true;
        } else {
            console.log(`  ✗ FAIL: Redirected to ${currentUrl} (session may have been created!)`);
            stayedOnLogin = false;
        }

        console.log("\nStep 6: Take screenshot");
        await page.screenshot({ path: ".playwright-mcp/feature3_step6_final_verification.png", fullPage: true });
        console.log("  ✓ Screenshot saved");

        // Final verdict
        console.log("\n" + "=".repeat(60));
        if (errorMessage && isGeneric && stayedOnLogin) {
            console.log("RESULT: PASSED ✓");
            console.log("  - Generic error message shown");
            console.log("  - No session created");
            console.log("  - User remains on login page");
            await browser.close();
            return true;
        } else {
            console.log("RESULT: FAILED ✗");
            if (!errorMessage) {
                console.log("  - No error message displayed");
            } else if (!isGeneric) {
                console.log("  - Error message reveals which field is wrong (security issue)");
            }
            if (!stayedOnLogin) {
                console.log("  - User was redirected (possible session creation)");
            }
            await browser.close();
            return false;
        }

    } catch (error) {
        console.log(`\n✗ ERROR: ${error.message}`);
        await page.screenshot({ path: ".playwright-mcp/feature3_error.png" });
        await browser.close();
        return false;
    }
}

testFeature3().then(result => {
    process.exit(result ? 0 : 1);
}).catch(error => {
    console.error("Fatal error:", error);
    process.exit(1);
});
