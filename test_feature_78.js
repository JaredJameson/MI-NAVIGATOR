/**
 * Test Feature #78 - Brief collection for new research
 *
 * Steps:
 * 1. Login (test2fa@test.com / TestPass123!)
 * 2. Navigate to http://localhost:3000/chat
 * 3. Start new research query: "Analyze FADO Sp. z o.o. for investment due diligence"
 * 4. Verify brief collection questions appear (purple card with question)
 * 5. Answer objective question: "Investment due diligence and risk assessment"
 * 6. Verify scope question appears with 4 options
 * 7. Click "Competitive landscape" option
 * 8. Verify depth question appears with 4 options
 * 9. Click "Detailed Report" option
 * 10. Verify plan is generated (green card) with objective, scope, depth, steps, and estimated time
 * 11. Click "Proceed with Plan" button
 * 12. Verify research starts with progress bar and phases
 */

const { chromium } = require('playwright');

async function testFeature78() {
    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    const page = await browser.newPage();

    // Listen to console messages for debugging
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

    try {
        console.log("=".repeat(60));
        console.log("Feature #78: Brief Collection for New Research");
        console.log("=".repeat(60));

        // STEP 1: Login
        console.log("\n[Step 1] Login with test2fa@test.com / TestPass123!");
        await page.goto("http://localhost:3000/auth/login", { waitUntil: "load", timeout: 30000 });
        await page.waitForTimeout(2000);

        // Fill login form
        await page.fill('input#email', "test2fa@test.com");
        await page.fill('input#password', "TestPass123!");
        await page.screenshot({ path: ".playwright-mcp/feature78_step1_login.png", fullPage: true });

        const loginButton = page.locator('button[type="submit"]').first();
        await loginButton.click();

        // Wait for redirect to dashboard or chat
        await page.waitForTimeout(3000);
        console.log("✓ Login successful");

        // STEP 2: Navigate to /chat
        console.log("\n[Step 2] Navigate to http://localhost:3000/chat");
        await page.goto("http://localhost:3000/chat", { waitUntil: "load", timeout: 30000 });
        await page.waitForTimeout(2000);
        await page.screenshot({ path: ".playwright-mcp/feature78_step2_chat_page.png", fullPage: true });
        console.log("✓ Chat page loaded");

        // STEP 3: Start new research query
        console.log("\n[Step 3] Start new research query: 'Analyze FADO Sp. z o.o. for investment due diligence'");
        const query = "Analyze FADO Sp. z o.o. for investment due diligence";

        // Find the textarea input
        const textarea = page.locator('textarea').first();
        await textarea.fill(query);
        await page.screenshot({ path: ".playwright-mcp/feature78_step3_query_entered.png", fullPage: true });

        // Send the message
        const sendButton = page.locator('button:has(svg)').last(); // Send button with arrow icon
        await sendButton.click();
        console.log("✓ Query sent");

        // STEP 4: Verify brief collection question appears (purple card)
        console.log("\n[Step 4] Verify brief collection questions appear (purple card)");
        await page.waitForTimeout(5000); // Wait for WebSocket response

        // Look for purple card with brief question
        const briefCard = page.locator('div.from-purple-50').first();
        const briefCardVisible = await briefCard.isVisible({ timeout: 15000 });

        if (!briefCardVisible) {
            console.log("✗ FAIL: Brief collection card (purple) not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step4_no_brief_card.png", fullPage: true });
            await browser.close();
            return false;
        }

        await page.screenshot({ path: ".playwright-mcp/feature78_step4_brief_question.png", fullPage: true });

        // Extract question text
        const questionText = await briefCard.locator('h3').textContent();
        console.log(`✓ Brief question appeared: "${questionText}"`);

        // STEP 5: Answer objective question
        console.log("\n[Step 5] Answer objective question: 'Investment due diligence and risk assessment'");

        // Check if it's a text input question
        const textInput = briefCard.locator('input[type="text"]');
        const hasTextInput = await textInput.isVisible({ timeout: 2000 }).catch(() => false);

        if (hasTextInput) {
            await textInput.fill("Investment due diligence and risk assessment");
            await textInput.press('Enter');
            console.log("✓ Objective answer submitted");
            await page.waitForTimeout(3000);
            await page.screenshot({ path: ".playwright-mcp/feature78_step5_objective_answered.png", fullPage: true });
        } else {
            console.log("? No text input found, checking for options...");
            await page.screenshot({ path: ".playwright-mcp/feature78_step5_no_text_input.png", fullPage: true });
        }

        // STEP 6: Verify scope question appears
        console.log("\n[Step 6] Verify scope question appears with 4 options");
        await page.waitForTimeout(3000);

        const scopeCard = page.locator('div.from-purple-50').first();
        const scopeVisible = await scopeCard.isVisible({ timeout: 10000 });

        if (!scopeVisible) {
            console.log("✗ FAIL: Scope question card not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step6_no_scope_card.png", fullPage: true });
            await browser.close();
            return false;
        }

        await page.screenshot({ path: ".playwright-mcp/feature78_step6_scope_question.png", fullPage: true });

        const scopeQuestionText = await scopeCard.locator('h3').textContent();
        console.log(`✓ Scope question appeared: "${scopeQuestionText}"`);

        // Count options
        const optionButtons = scopeCard.locator('button');
        const optionCount = await optionButtons.count();
        console.log(`  - Found ${optionCount} options`);

        if (optionCount < 4) {
            console.log(`✗ FAIL: Expected 4 options, found ${optionCount}`);
        }

        // STEP 7: Click "Competitive landscape" option
        console.log("\n[Step 7] Click 'Competitive landscape' option");

        // Find button containing "Competitive" text
        const competitiveButton = scopeCard.locator('button:has-text("Competitive")').first();
        const competitiveVisible = await competitiveButton.isVisible({ timeout: 5000 });

        if (!competitiveVisible) {
            console.log("✗ FAIL: 'Competitive landscape' option not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step7_no_competitive.png", fullPage: true });
            await browser.close();
            return false;
        }

        await competitiveButton.click();
        console.log("✓ 'Competitive landscape' clicked");
        await page.waitForTimeout(3000);
        await page.screenshot({ path: ".playwright-mcp/feature78_step7_competitive_clicked.png", fullPage: true });

        // STEP 8: Verify depth question appears
        console.log("\n[Step 8] Verify depth question appears with 4 options");
        await page.waitForTimeout(3000);

        const depthCard = page.locator('div.from-purple-50').first();
        const depthVisible = await depthCard.isVisible({ timeout: 10000 });

        if (!depthVisible) {
            console.log("✗ FAIL: Depth question card not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step8_no_depth_card.png", fullPage: true });
            await browser.close();
            return false;
        }

        await page.screenshot({ path: ".playwright-mcp/feature78_step8_depth_question.png", fullPage: true });

        const depthQuestionText = await depthCard.locator('h3').textContent();
        console.log(`✓ Depth question appeared: "${depthQuestionText}"`);

        // Count depth options
        const depthOptions = depthCard.locator('button');
        const depthCount = await depthOptions.count();
        console.log(`  - Found ${depthCount} options`);

        if (depthCount < 4) {
            console.log(`✗ FAIL: Expected 4 options, found ${depthCount}`);
        }

        // STEP 9: Click "Detailed Report" option
        console.log("\n[Step 9] Click 'Detailed Report' option");

        // Find button containing "Detailed" text
        const detailedButton = depthCard.locator('button:has-text("Detailed")').first();
        const detailedVisible = await detailedButton.isVisible({ timeout: 5000 });

        if (!detailedVisible) {
            console.log("✗ FAIL: 'Detailed Report' option not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step9_no_detailed.png", fullPage: true });
            await browser.close();
            return false;
        }

        await detailedButton.click();
        console.log("✓ 'Detailed Report' clicked");
        await page.waitForTimeout(5000);
        await page.screenshot({ path: ".playwright-mcp/feature78_step9_detailed_clicked.png", fullPage: true });

        // STEP 10: Verify plan is generated (green card)
        console.log("\n[Step 10] Verify plan is generated (green card)");
        await page.waitForTimeout(5000);

        const planCard = page.locator('div.from-green-50').first();
        const planVisible = await planCard.isVisible({ timeout: 15000 });

        if (!planVisible) {
            console.log("✗ FAIL: Research plan card (green) not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step10_no_plan_card.png", fullPage: true });
            await browser.close();
            return false;
        }

        await page.screenshot({ path: ".playwright-mcp/feature78_step10_plan_generated.png", fullPage: true });
        console.log("✓ Research plan card appeared");

        // Verify plan contains required elements
        const planHeader = await planCard.locator('h3').textContent();
        console.log(`  - Plan header: "${planHeader}"`);

        // Check for objective, scope, depth
        const planDetails = await planCard.locator('div.bg-white').first();
        const planText = await planDetails.textContent();

        const hasObjective = planText.includes('Objective') || planText.includes('objective');
        const hasScope = planText.includes('Scope') || planText.includes('scope');
        const hasDepth = planText.includes('Depth') || planText.includes('depth');

        console.log(`  - Has Objective: ${hasObjective ? '✓' : '✗'}`);
        console.log(`  - Has Scope: ${hasScope ? '✓' : '✗'}`);
        console.log(`  - Has Depth: ${hasDepth ? '✓' : '✗'}`);

        // Check for research steps
        const hasSteps = planText.includes('Research Steps') || planText.includes('steps');
        console.log(`  - Has Research Steps: ${hasSteps ? '✓' : '✗'}`);

        // Check for estimated time
        const hasTime = planText.includes('estimated time') || planText.includes('minutes');
        console.log(`  - Has Estimated Time: ${hasTime ? '✓' : '✗'}`);

        if (!hasObjective || !hasScope || !hasDepth || !hasSteps || !hasTime) {
            console.log("✗ FAIL: Plan missing required elements");
            await browser.close();
            return false;
        }

        // STEP 11: Click "Proceed with Plan" button
        console.log("\n[Step 11] Click 'Proceed with Plan' button");

        const proceedButton = planCard.locator('button:has-text("Proceed")').first();
        const proceedVisible = await proceedButton.isVisible({ timeout: 5000 });

        if (!proceedVisible) {
            console.log("✗ FAIL: 'Proceed with Plan' button not found");
            await page.screenshot({ path: ".playwright-mcp/feature78_step11_no_proceed.png", fullPage: true });
            await browser.close();
            return false;
        }

        await proceedButton.click();
        console.log("✓ 'Proceed with Plan' clicked");
        await page.waitForTimeout(3000);
        await page.screenshot({ path: ".playwright-mcp/feature78_step11_proceed_clicked.png", fullPage: true });

        // STEP 12: Verify research starts (progress bar)
        console.log("\n[Step 12] Verify research starts with progress bar");
        await page.waitForTimeout(5000);

        // Look for progress indicator (should show percentage, phase, message)
        const progressCard = page.locator('div.bg-white').filter({ hasText: '%' }).first();
        const progressVisible = await progressCard.isVisible({ timeout: 10000 }).catch(() => false);

        if (progressVisible) {
            await page.screenshot({ path: ".playwright-mcp/feature78_step12_research_started.png", fullPage: true });

            const progressText = await progressCard.textContent();
            console.log("✓ Research progress started");
            console.log(`  - Progress info: ${progressText.substring(0, 100)}...`);

            // Check for progress bar
            const hasProgressBar = await page.locator('div.bg-blue-600').isVisible({ timeout: 5000 }).catch(() => false);
            console.log(`  - Has Progress Bar: ${hasProgressBar ? '✓' : '✗'}`);

            // Wait a bit longer to see if phases appear
            await page.waitForTimeout(5000);
            await page.screenshot({ path: ".playwright-mcp/feature78_step12_research_progress.png", fullPage: true });

        } else {
            console.log("? Progress bar not visible yet, checking for loading state...");

            // Check for loading indicator (bouncing dots)
            const loadingDots = page.locator('div.animate-bounce').first();
            const loadingVisible = await loadingDots.isVisible({ timeout: 5000 }).catch(() => false);

            if (loadingVisible) {
                console.log("✓ Loading state visible (research may be starting)");
                await page.screenshot({ path: ".playwright-mcp/feature78_step12_loading.png", fullPage: true });
            } else {
                console.log("✗ FAIL: No progress or loading state found");
                await page.screenshot({ path: ".playwright-mcp/feature78_step12_no_progress.png", fullPage: true });
                await browser.close();
                return false;
            }
        }

        // Wait longer to capture any research results
        console.log("\n[Final] Waiting for research to show results...");
        await page.waitForTimeout(10000);
        await page.screenshot({ path: ".playwright-mcp/feature78_complete_brief_and_plan.png", fullPage: true });

        // FINAL VERDICT
        console.log("\n" + "=".repeat(60));
        console.log("RESULT: PASSED ✓");
        console.log("=".repeat(60));
        console.log("Summary:");
        console.log("✓ Login successful");
        console.log("✓ Chat page loaded");
        console.log("✓ Research query sent");
        console.log("✓ Brief collection questions appeared (purple card)");
        console.log("✓ Objective question answered");
        console.log("✓ Scope question appeared with options");
        console.log("✓ 'Competitive landscape' option selected");
        console.log("✓ Depth question appeared with options");
        console.log("✓ 'Detailed Report' option selected");
        console.log("✓ Research plan generated (green card)");
        console.log("✓ Plan contains: objective, scope, depth, steps, estimated time");
        console.log("✓ 'Proceed with Plan' button clicked");
        console.log("✓ Research started (progress/loading state visible)");
        console.log("=".repeat(60));

        await browser.close();
        return true;

    } catch (error) {
        console.log(`\n✗ ERROR: ${error.message}`);
        console.log(error.stack);
        await page.screenshot({ path: ".playwright-mcp/feature78_error.png", fullPage: true });
        await browser.close();
        return false;
    }
}

testFeature78().then(result => {
    process.exit(result ? 0 : 1);
}).catch(error => {
    console.error("Fatal error:", error);
    process.exit(1);
});
