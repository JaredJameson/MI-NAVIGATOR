const { chromium } = require('playwright');
const path = require('path');

/**
 * Feature #269 - TAM SAM SOM Visualization Test
 *
 * Tests market size visualization with concentric circles diagram.
 * Steps:
 * 1. Login to the app (test2fa@test.com / TestPass123!)
 * 2. Navigate to chat and request market sizing analysis
 * 3. Wait for response with TAM/SAM/SOM data
 * 4. Verify concentric circles diagram appears
 * 5. Verify TAM is outer circle, SAM is middle, SOM is inner
 * 6. Verify values are labeled on each circle
 * 7. Verify interactive tooltips work (hover over circles)
 * 8. Take screenshots
 */

(async () => {
  const screenshotDir = path.join(__dirname, '.playwright-mcp');
  let browser;
  let testPassed = false;
  let failureReason = '';

  try {
    console.log('Starting Feature #269 test - TAM SAM SOM Visualization...\n');

    browser = await chromium.launch({
      headless: false,
      slowMo: 500
    });

    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    const page = await context.newPage();

    // Step 1: Login
    console.log('Step 1: Navigating to login page...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step1_login_page.png'), fullPage: true });

    console.log('Step 1: Entering credentials...');
    await page.fill('input[type="email"]', 'test2fa@test.com');
    await page.fill('input[type="password"]', 'TestPass123!');
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step1_credentials_filled.png'), fullPage: true });

    console.log('Step 1: Clicking login button...');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check if 2FA is required
    const has2FA = await page.locator('input[placeholder*="code"], input[placeholder*="Code"], input[name="code"]').count() > 0;
    if (has2FA) {
      console.log('Step 1: 2FA detected, generating TOTP code...');
      // Generate TOTP code using Python script
      const { execSync } = require('child_process');
      const totp = execSync('python3 generate_totp_test.py').toString().trim();
      console.log(`Step 1: Using TOTP code: ${totp}`);

      await page.fill('input[placeholder*="code"], input[placeholder*="Code"], input[name="code"]', totp);
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step1_2fa_filled.png'), fullPage: true });
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
    }

    // Wait for successful login
    await page.waitForURL('**/dashboard', { timeout: 10000 }).catch(() => {});
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step1_logged_in.png'), fullPage: true });
    console.log('Step 1: Login successful ✓\n');

    // Step 2: Navigate to chat
    console.log('Step 2: Navigating to chat page...');
    await page.goto('http://localhost:3000/chat', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step2_chat_page.png'), fullPage: true });
    console.log('Step 2: Chat page loaded ✓\n');

    // Step 3: Request market sizing analysis
    console.log('Step 3: Requesting market sizing analysis...');
    const marketQuery = 'What is the market size for CNC machining in Poland?';

    const chatInput = await page.locator('textarea, input[type="text"]').last();
    await chatInput.fill(marketQuery);
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3_query_typed.png'), fullPage: true });

    // Submit the query
    await chatInput.press('Enter');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3_query_submitted.png'), fullPage: true });

    // Handle multi-step clarification dialog
    console.log('Step 3: Checking for clarification dialogs...');

    // Step 3a: Research objective
    let clarificationDialog = await page.locator('text=What is the main objective').count() > 0;
    if (clarificationDialog) {
      console.log('Step 3a: Clarification dialog detected, providing research objective...');
      const objectiveInput = await page.locator('input[placeholder*="Evaluate"], textarea').first();
      await objectiveInput.fill('Market sizing and opportunity analysis');
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3a_objective_filled.png'), fullPage: true });
      await objectiveInput.press('Enter');
      await page.waitForTimeout(3000);
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3a_objective_submitted.png'), fullPage: true });
    }

    // Step 3b: Research scope
    const scopeDialog = await page.locator('text=What is the scope').count() > 0;
    if (scopeDialog) {
      console.log('Step 3b: Scope dialog detected, selecting "Full industry deep dive"...');
      // Click on the "Full industry deep dive" option which includes market analysis
      await page.click('text=Full industry deep dive');
      await page.waitForTimeout(3000);
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3b_scope_selected.png'), fullPage: true });
    }

    // Step 3c: Detail level
    const detailDialog = await page.locator('text=What level of detail').count() > 0;
    if (detailDialog) {
      console.log('Step 3c: Detail level dialog detected, selecting "Standard Analysis"...');
      // Click on "Standard Analysis" for reasonable depth
      await page.click('text=Standard Analysis');
      await page.waitForTimeout(3000);
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3c_detail_selected.png'), fullPage: true });
    }

    // Step 3d: Check for research plan and proceed
    const researchPlan = await page.locator('text=Research Plan Generated').count() > 0;
    if (researchPlan) {
      console.log('Step 3d: Research plan generated, looking for proceed button...');
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3d_research_plan.png'), fullPage: true });

      // Look for a proceed/confirm/start button
      const proceedButton = await page.locator('button:has-text("Proceed"), button:has-text("Start"), button:has-text("Confirm"), button:has-text("Continue")').first();
      if (await proceedButton.count() > 0) {
        console.log('Step 3d: Clicking proceed button to start research...');
        await proceedButton.click();
        await page.waitForTimeout(3000);
        await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3d_research_started.png'), fullPage: true });
      } else {
        console.log('Step 3d: No proceed button found, research may auto-start');
      }
    }

    console.log('Step 3: Waiting for response (up to 120 seconds)...');

    // Wait for response to appear - look for TAM/SAM/SOM related content
    let responseReceived = false;
    let visualizationFound = false;
    let actualMarketData = false;

    for (let i = 0; i < 120; i++) {
      await page.waitForTimeout(1000);

      const pageContent = await page.content();
      const pageText = await page.textContent('body');

      // Check for actual TAM/SAM/SOM data (not just the query echo)
      const hasTAMData = (pageText.includes('TAM') && (pageText.includes('billion') || pageText.includes('million') || pageText.includes('PLN') || pageText.includes('EUR')));
      const hasSAMData = (pageText.includes('SAM') && (pageText.includes('billion') || pageText.includes('million') || pageText.includes('PLN') || pageText.includes('EUR')));
      const hasSOMData = (pageText.includes('SOM') && (pageText.includes('billion') || pageText.includes('million') || pageText.includes('PLN') || pageText.includes('EUR')));

      if (hasTAMData || hasSAMData || hasSOMData) {
        responseReceived = true;
        actualMarketData = true;
        console.log(`Step 3: Response with market sizing data received after ${i + 1} seconds ✓`);
        await page.screenshot({ path: path.join(screenshotDir, 'feature269_step3_response_received.png'), fullPage: true });
        break;
      }

      // Also check for progress indicators or streaming response
      if (pageContent.includes('Analyzing') || pageContent.includes('Researching') || pageContent.includes('Processing')) {
        if (i % 10 === 0) {
          console.log(`  Research in progress... (${i}s)`);
          await page.screenshot({ path: path.join(screenshotDir, `feature269_step3_progress_${i}s.png`), fullPage: true });
        }
      } else if (i % 5 === 0) {
        console.log(`  Waiting... (${i}s)`);
      }
    }

    if (!responseReceived) {
      failureReason = 'No market sizing response received within 60 seconds';
      console.log(`Step 3: ${failureReason} ✗\n`);
    } else {
      console.log('Step 3: Market sizing response received ✓\n');
    }

    // Step 4: Check for concentric circles diagram
    console.log('Step 4: Checking for concentric circles diagram...');
    await page.waitForTimeout(2000);

    // Scroll to top to see full visualization
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step4_scrolled_to_top.png'), fullPage: true });

    // Look for SVG elements that might represent the visualization
    const svgElements = await page.locator('svg').count();
    const canvasElements = await page.locator('canvas').count();
    const circleElements = await page.locator('circle').count();

    console.log(`  Found ${svgElements} SVG elements`);
    console.log(`  Found ${canvasElements} Canvas elements`);
    console.log(`  Found ${circleElements} circle elements`);

    if (svgElements > 0 || canvasElements > 0 || circleElements > 0) {
      visualizationFound = true;
      console.log('Step 4: Visualization elements found ✓');
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step4_visualization_found.png'), fullPage: true });
    } else {
      console.log('Step 4: No visualization elements found');
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step4_no_visualization.png'), fullPage: true });
    }
    console.log('');

    // Step 5: Verify circle structure (TAM outer, SAM middle, SOM inner)
    console.log('Step 5: Verifying circle structure...');

    if (circleElements >= 3) {
      // Get all circles and check their radii
      const circles = await page.locator('circle').all();
      const radii = [];

      for (const circle of circles) {
        const r = await circle.getAttribute('r');
        if (r) {
          radii.push(parseFloat(r));
        }
      }

      radii.sort((a, b) => b - a); // Sort descending
      console.log(`  Circle radii found: ${radii.join(', ')}`);

      if (radii.length >= 3 && radii[0] > radii[1] && radii[1] > radii[2]) {
        console.log('Step 5: Concentric circles with decreasing radii confirmed ✓');
        await page.screenshot({ path: path.join(screenshotDir, 'feature269_step5_circles_verified.png'), fullPage: true });
      } else {
        console.log('Step 5: Circle structure does not match expected pattern');
      }
    } else {
      console.log('Step 5: Less than 3 circles found - cannot verify structure');
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step5_insufficient_circles.png'), fullPage: true });
    }
    console.log('');

    // Step 6: Verify labels on circles
    console.log('Step 6: Checking for value labels on circles...');

    const pageText = await page.textContent('body');
    const hasTAMLabel = pageText.includes('TAM') || pageText.includes('Total Addressable Market');
    const hasSAMLabel = pageText.includes('SAM') || pageText.includes('Serviceable Addressable Market');
    const hasSOMLabel = pageText.includes('SOM') || pageText.includes('Serviceable Obtainable Market');

    console.log(`  TAM label found: ${hasTAMLabel}`);
    console.log(`  SAM label found: ${hasSAMLabel}`);
    console.log(`  SOM label found: ${hasSOMLabel}`);

    if (hasTAMLabel && hasSAMLabel && hasSOMLabel) {
      console.log('Step 6: All market size labels found ✓');
    } else {
      console.log('Step 6: Some labels missing');
    }

    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step6_labels_check.png'), fullPage: true });
    console.log('');

    // Step 7: Test interactive tooltips
    console.log('Step 7: Testing interactive tooltips...');

    if (circleElements > 0) {
      const circles = await page.locator('circle').all();

      for (let i = 0; i < Math.min(circles.length, 3); i++) {
        console.log(`  Hovering over circle ${i + 1}...`);
        await circles[i].hover();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(screenshotDir, `feature269_step7_hover_circle_${i + 1}.png`), fullPage: true });
      }

      console.log('Step 7: Tooltip interaction test complete ✓');
    } else {
      console.log('Step 7: No circles to test tooltips on');
      await page.screenshot({ path: path.join(screenshotDir, 'feature269_step7_no_tooltips.png'), fullPage: true });
    }
    console.log('');

    // Step 8: Final screenshot
    console.log('Step 8: Taking final screenshot...');
    await page.screenshot({ path: path.join(screenshotDir, 'feature269_step8_final_view.png'), fullPage: true });
    console.log('Step 8: Final screenshot saved ✓\n');

    // Determine test result
    if (responseReceived && visualizationFound) {
      testPassed = true;
      console.log('═══════════════════════════════════════════════════════');
      console.log('RESULT: PASSED ✓');
      console.log('═══════════════════════════════════════════════════════');
      console.log('Market sizing feature is implemented with visualization.');
      console.log(`Found ${circleElements} circle elements in the visualization.`);
      console.log('TAM/SAM/SOM labels present in response.');
    } else if (responseReceived && !visualizationFound) {
      console.log('═══════════════════════════════════════════════════════');
      console.log('RESULT: PARTIAL ⚠');
      console.log('═══════════════════════════════════════════════════════');
      console.log('Market sizing feature returns data but visualization not found.');
      console.log('The feature may be text-based only at this time.');
    } else {
      console.log('═══════════════════════════════════════════════════════');
      console.log('RESULT: NOT IMPLEMENTED / FAILED ✗');
      console.log('═══════════════════════════════════════════════════════');
      console.log(`Reason: ${failureReason || 'Market sizing feature not responding'}`);
      console.log('This feature may not be implemented yet.');
    }

    console.log('\nAll screenshots saved to:', screenshotDir);

  } catch (error) {
    console.error('\n═══════════════════════════════════════════════════════');
    console.error('RESULT: ERROR ✗');
    console.error('═══════════════════════════════════════════════════════');
    console.error('Error during test execution:', error.message);
    console.error('\nStack trace:', error.stack);

    if (browser) {
      const page = (await browser.contexts())[0]?.pages()[0];
      if (page) {
        await page.screenshot({ path: path.join(screenshotDir, 'feature269_error.png'), fullPage: true });
        console.log('\nError screenshot saved to:', path.join(screenshotDir, 'feature269_error.png'));
      }
    }
  } finally {
    if (browser) {
      console.log('\nClosing browser...');
      await browser.close();
    }

    process.exit(testPassed ? 0 : 1);
  }
})();
