# Feature #122 Regression Test - PARTIAL FAILURE

**Session:** 375
**Date:** 2026-01-21
**Feature:** Direct URL access to entity requires auth
**Status:** ❌ PARTIAL FAILURE (4/5 steps passing, 1/5 critical functionality missing)

## Test Steps & Results

### ✅ Step 1: Log out
**Status:** PASSING
- Clicked "Logout" button from dashboard
- Successfully redirected to `/auth/login`
- Screenshot: `regression_session375_feature122_step3_after_logout.png`

### ✅ Step 2: Access report URL directly
**Status:** PASSING
- Navigated to `http://localhost:3000/reports/pagination_test_c75aa4be_0001` while logged out
- Application detected unauthorized access
- Screenshot: `regression_session375_feature122_step4_direct_access.png`

### ✅ Step 3: Verify redirect to login
**Status:** PASSING
- Application correctly redirected from `/reports/pagination_test_c75aa4be_0001` to `/auth/login`
- Redirect happened automatically without showing protected content
- Screenshot: `regression_session375_feature122_step5_final_page.png`

### ✅ Step 4: Login
**Status:** PASSING
- Created new test account: `test_feature122@example.com` / `Test1234`
- Registration successful
- Login successful
- Screenshots:
  - `regression_session375_feature122_step7_register_page.png`
  - `regression_session375_feature122_step8_after_register.png`

### ❌ Step 5: Verify redirect to intended page
**Status:** FAILING - CRITICAL ISSUE
- **Expected:** After login, redirect to original URL `/reports/pagination_test_c75aa4be_0001`
- **Actual:** After login, redirected to `/dashboard`
- **Evidence:**
  - Final URL: `http://localhost:3000/dashboard` (confirmed via `window.location.href`)
  - Screenshots:
    - `regression_session375_feature122_step9_after_login_redirect.png`
    - `regression_session375_feature122_step10_final_url_check.png`

## Problem Analysis

### Issue
The application does NOT preserve the originally requested URL when redirecting unauthorized users to login.

### Expected Flow
1. User visits `/reports/pagination_test_c75aa4be_0001` (not logged in)
2. App redirects to `/auth/login?redirect=/reports/pagination_test_c75aa4be_0001`
3. User logs in
4. App redirects back to `/reports/pagination_test_c75aa4be_0001`

### Actual Flow
1. User visits `/reports/pagination_test_c75aa4be_0001` (not logged in)
2. App redirects to `/auth/login` (NO redirect parameter)
3. User logs in
4. App redirects to `/dashboard` (DEFAULT, not original URL)

## Impact

**Severity:** HIGH

### User Experience Impact
- Poor UX: Users must manually navigate back to the page they wanted
- Frustration: Extra clicks required after authentication
- Confusing: Users may forget what they were trying to access

### Business Impact
- Direct links shared via email/slack won't work as expected
- Bookmarked report URLs require extra navigation after login
- External integrations expecting deep linking will fail

## Recommended Fix

### Frontend (Login Page)
1. Read `redirect` URL parameter from query string
2. After successful login, redirect to `redirect` URL if present
3. Fallback to `/dashboard` if no redirect parameter

### Frontend (Auth Middleware)
1. When detecting unauthorized access, preserve current URL
2. Redirect to `/auth/login?redirect=${encodeURIComponent(currentUrl)}`
3. Handle edge cases (logout redirect, already on login page)

### Backend (Auth API)
1. Return `redirect_url` in login response if stored in session
2. Validate redirect URL is internal (prevent open redirect vulnerability)

## Test Evidence

All screenshots saved in `.playwright-mcp/` directory:
- `regression_session375_step1_homepage.png`
- `regression_session375_feature122_step1_reports.png`
- `regression_session375_feature122_step2_logout_button.png`
- `regression_session375_feature122_step3_after_logout.png`
- `regression_session375_feature122_step4_direct_access.png`
- `regression_session375_feature122_step5_final_page.png`
- `regression_session375_feature122_step6_after_login.png`
- `regression_session375_feature122_step7_register_page.png`
- `regression_session375_feature122_step8_after_register.png`
- `regression_session375_feature122_step9_after_login_redirect.png`
- `regression_session375_feature122_step10_final_url_check.png`

## Conclusion

Feature #122 provides basic authentication protection (redirects unauthorized users to login), but **lacks the critical "redirect back to intended page" functionality** that makes the feature truly useful.

**Score:** 4/5 steps passing (80%)
**Verdict:** PARTIAL FAILURE - Basic auth works, but missing post-login redirect
**Action Required:** Implement post-login redirect to originally requested URL
