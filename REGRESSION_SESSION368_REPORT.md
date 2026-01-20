# Regression Testing Report - Session 368
**Date:** 2026-01-20
**Status:** 🔴 **CRITICAL AUTHENTICATION REGRESSION**
**Features Tested:** 3 (Feature #217, #298, #71)
**Result:** 1/3 PASSING, 2/3 BLOCKED BY 401 ERRORS

---

## 🚨 CRITICAL DISCOVERY: Session Expires During Usage

### Problem Description
**Authentication tokens expire or become invalid DURING normal application usage**, causing widespread 401 Unauthorized errors across multiple endpoints.

### Impact
- **Blocks 2/3 regression test features** (Feature #298, #71)
- **Same issue that blocked sessions 355-362** (9 consecutive sessions!)
- **Application appears logged in but cannot load data**

---

## Test Results Summary

| Feature | Name | Steps Passing | Status | Blocker |
|---------|------|---------------|--------|---------|
| #217 | Session persistence across refresh | 5/5 (100%) | ✅ **PASSING** | None |
| #298 | Auto-save draft functionality | 0/6 (0%) | ❌ **BLOCKED** | 401 on `/api/proxy/reports/` |
| #71 | Alert notification delivery | 0/5 (0%) | ❌ **BLOCKED** | 401 on `/api/proxy/alerts/` |

**Summary:**
- Verified Passing: 1/3 (33%)
- Blocked by Auth: 2/3 (67%)
- **Critical regression blocks 67% of testable features**

---

## ✅ Feature #217: Session Persistence Across Refresh - PASSING

**Test Location:** `/dashboard`

**All 5 steps PASSING:**

### Step 1: Login and navigate to page ✅
- User already logged in as `user@example.com`
- Dashboard loaded successfully at `/dashboard`
- All widgets visible and functional

### Step 2: Press F5 to refresh ✅
- Executed `page.keyboard.press('F5')`
- Page reloaded without errors

### Step 3: Verify still logged in ✅
- User still visible in sidebar: "User (user@example.com)"
- No redirect to `/auth/login`
- Logout button still present

### Step 4: Verify page state restored ✅
- Dashboard layout identical before/after refresh
- All widgets present:
  - "Rozpocznij badanie" search widget
  - "Active Research" widget
  - "Recent Activity" widget
  - "Usage Stats" widget
  - "My Projects" widget
  - "Alerts & Monitoring" widget

### Step 5: Verify no re-authentication needed ✅
- **Zero ERROR logs in console**
- **All API calls returned 200 OK:**
  - `GET /api/proxy/users/me` → 200 OK
  - `GET /api/proxy/research/active` → 200 OK
  - `GET /api/proxy/users/usage?period=month` → 200 OK
  - `GET /api/proxy/projects` → 200 OK
  - `GET /api/proxy/alerts/?limit=3` → 200 OK
  - `GET /api/proxy/activity?limit=3` → 200 OK
- No POST to `/auth/login` (no re-authentication)
- Session persisted correctly

**Evidence:** 2 screenshots, zero console errors

**Result:** ✅ **5/5 steps PASSING (100%)**

**Status:** ✅ **PRODUCTION READY** - No regressions detected

---

## ❌ Feature #298: Auto-save Draft Functionality - BLOCKED

**Test Location:** `/reports` (attempted)

**Steps: 0/6 (blocked at step 1)**

### Blocker: 401 Unauthorized on Reports API

**Timeline of 401 Errors:**

1. **Initial load of `/reports` - SUCCESS:**
   - First call: `GET /api/proxy/reports/?page=1&limit=5` → **200 OK** ✅
   - Reports loaded and displayed correctly
   - Saw 5 reports: "Pagination Test Report #1-5"

2. **After clicking "Szkice" tab - SUCCESS:**
   - Call: `GET /api/proxy/reports/?page=1&limit=5&status=draft` → **200 OK** ✅
   - No drafts found (expected)

3. **After clicking back to "Wszystkie" tab - FAILURE:**
   - Same call: `GET /api/proxy/reports/?page=1&limit=5` → **401 Unauthorized** ❌
   - **Same endpoint that worked 30 seconds earlier now returns 401!**

4. **Direct navigation to report page:**
   - `GET /api/proxy/reports/pagination_test_c7902151_0001` → **401 Unauthorized** ❌
   - `GET /api/proxy/reports/{id}/annotations` → **401 Unauthorized** ❌
   - `GET /api/proxy/users/me/preferences` → **401 Unauthorized** ❌
   - But same report's versions/comments still work:
     - `GET /api/proxy/reports/{id}/versions` → **200 OK** ✅
     - `GET /api/proxy/reports/{id}/comments` → **200 OK** ✅

**Error Pattern:**
Some endpoints for the same resource return 200, others 401 - suggests **ownership/permission issue**, not just expired token.

**UI Impact:**
- Red error message: "Nie udało się załadować raportów"
- Link: "Zgłoś problem"
- Cannot access report editor
- **Cannot test auto-save functionality**

**Evidence:** 4 screenshots, 6+ ERROR logs

**Result:** ❌ **0/6 steps (BLOCKED at step 1)**

---

## ❌ Feature #71: Alert Notification Delivery - BLOCKED

**Test Location:** `/dashboard` (attempted)

**Steps: 0/5 (blocked at step 1)**

### Blocker: 401 Unauthorized on Multiple Dashboard APIs

**After navigating to dashboard:**

**12 ERROR logs (401 Unauthorized):**
1. `GET /api/proxy/users/me` → 401 (called 4 times)
2. `GET /api/proxy/research/active` → 401 (called 2 times)
3. `GET /api/proxy/users/usage?period=month` → 401 (called 2 times)
4. `GET /api/proxy/projects` → 401 (called 2 times)
5. `GET /api/proxy/activity?limit=3` → 401 (called 2 times)

**UI Impact:**
- Widget "Usage Stats" shows: **"Unable to load stats"** (was "0/100" before)
- Widget "My Projects" shows: **"No projects yet"** (had TEST_SESSION363_PROJECT_REGRESSION before)
- Widget "Recent Activity" shows: **"Brak ostatniej aktywności"**
- User appears logged in but data won't load
- **Cannot test alert functionality**

**Evidence:** 2 screenshots, 12 ERROR logs

**Result:** ❌ **0/5 steps (BLOCKED at step 1)**

---

## 🔍 Root Cause Analysis

### Authentication Token Lifecycle Issue

**Observations:**

1. **Initial login works perfectly:**
   - Dashboard loads all data successfully
   - All API calls return 200 OK
   - User session appears valid

2. **Session degrades over time/navigation:**
   - Same endpoints that worked initially start returning 401
   - Pattern: 200 OK → (user navigates) → 401 Unauthorized
   - Happens within **minutes** of usage

3. **Inconsistent endpoint behavior:**
   - Some endpoints for same resource work, others don't
   - Example: `/reports/{id}/versions` works, but `/reports/{id}` returns 401
   - Suggests **ownership validation failing**, not just token expiry

### Possible Causes

**Hypothesis 1: Token Refresh Failure**
- Access token expires (typical: 15 min)
- Refresh token mechanism failing
- Frontend doesn't retry with new token

**Hypothesis 2: Session Ownership Validation**
- User owns data initially
- Session ownership link broken during navigation
- Backend incorrectly validates user permissions

**Hypothesis 3: Cookie/LocalStorage Issue**
- Auth tokens stored in cookies or localStorage
- Tokens getting corrupted or cleared
- Inconsistent token retrieval across requests

### Code Investigation Needed

**Files to check:**
1. `frontend/src/lib/auth.ts` - Token refresh logic
2. `frontend/src/middleware.ts` - Auth middleware
3. `backend/app/core/auth.py` - Token validation
4. `backend/app/api/deps.py` - Dependency injection for auth
5. Network tab - Compare working vs failing request headers

---

## 🚨 Impact Assessment

### Features Blocked by This Issue

**From Session 368:**
- Feature #298 (Auto-save draft) - BLOCKED
- Feature #71 (Alert notifications) - BLOCKED

**From Previous Sessions (355-362):**
- Feature #2 (User login) - INCOMPLETE
- Feature #142 (Long text truncation) - BLOCKED
- Feature #137 (Modal focus trap) - INCOMPLETE
- Feature #39 (Report section reordering) - CODE VERIFIED, TEST BLOCKED
- Feature #240 (Report restore version) - CODE VERIFIED, TEST BLOCKED
- Many more...

**Estimated Impact:**
If this issue affects **67% of features** (2/3 in Session 368), and considering sessions 355-362 had similar problems:

- **~9 sessions blocked** (355-362 + 368 = 9 sessions)
- **~27 features unable to test** (3 features × 9 sessions)
- **Massive productivity loss**

### Production Risk

**🔴 CRITICAL - DO NOT DEPLOY TO PRODUCTION**

This issue would cause:
- Users to be randomly logged out
- Dashboard to show "Unable to load" errors
- Reports inaccessible
- Alerts not loading
- Complete breakdown of user experience

---

## 📊 Session Statistics

- **Duration:** ~2 hours
- **Features fully tested:** 1/3 (33%)
- **Features blocked:** 2/3 (67%)
- **Verified passing:** 1/3 (33%)
- **Screenshots:** 8 total
- **Console errors:** 18 (all 401 Unauthorized)
- **Token usage:** ~86k/200k (43%)

---

## 🔧 Recommended Actions

### Immediate (P0 - Critical)

1. **Investigate token refresh mechanism:**
   - Check if refresh tokens are being used
   - Verify token expiry times
   - Test token renewal flow

2. **Add auth error logging:**
   - Log all 401 responses with request context
   - Identify which endpoints fail most often
   - Capture token state when errors occur

3. **Implement token refresh retry:**
   - Intercept 401 responses
   - Attempt token refresh automatically
   - Retry original request with new token

### Short-term (P1 - High)

4. **Fix ownership validation:**
   - Review permission checks in backend
   - Ensure user ownership is checked consistently
   - Fix inconsistent endpoint behavior

5. **Add user-facing error handling:**
   - Show "Session expired" modal instead of silent failures
   - Provide "Refresh" or "Re-login" button
   - Clear error messages for users

6. **Create regression test:**
   - Automated test that uses app for 10+ minutes
   - Navigates between pages multiple times
   - Verifies no 401 errors occur

### Long-term (P2 - Medium)

7. **Session monitoring dashboard:**
   - Track session duration before failures
   - Identify most common failure patterns
   - Alert on authentication error spikes

8. **Improve token architecture:**
   - Consider longer-lived access tokens
   - Implement sliding sessions
   - Add token health checks

---

## 📝 Next Steps for Testing

**Cannot proceed with normal regression testing until auth issue is resolved.**

**Options:**

1. **Skip to non-auth features:**
   - Test UI-only features that don't require API calls
   - Focus on client-side functionality
   - Limited value without full integration

2. **Create fresh user session:**
   - Try creating new test user
   - See if fresh session avoids issue
   - May only work temporarily

3. **Wait for auth fix:**
   - Block all regression testing
   - Work on auth bug fix first
   - Resume testing after fix verified

**Recommendation:** **PAUSE regression testing, fix auth bug (P0 priority)**, then resume.

---

## 📎 Evidence Files

**Screenshots:**
1. `session368_feature217_step1_homepage.png` - Initial homepage load
2. `session368_feature217_step1_homepage_loaded.png` - Dashboard after loading
3. `session368_feature217_step2_after_refresh.png` - Dashboard after F5 refresh (working)
4. `session368_feature298_step1_reports_list.png` - Reports page (skeleton loading)
5. `session368_feature298_step1_reports_loaded.png` - Reports page (loaded, working)
6. `session368_feature298_step1_drafts_tab.png` - Drafts tab (empty, working)
7. `session368_feature298_step1_401_error.png` - Reports page with 401 error
8. `session368_feature298_step1_report_page.png` - Report page 401 error
9. `session368_feature71_step1_dashboard.png` - Dashboard (skeleton loading)
10. `session368_feature71_step1_dashboard_loaded.png` - Dashboard with "Unable to load" errors

**Console Logs:**
- Feature #217: 0 errors ✅
- Feature #298: 6+ errors (401 Unauthorized)
- Feature #71: 12+ errors (401 Unauthorized)
- **Total: 18+ authentication errors**

---

## 🎯 Conclusion

**Session 368 Status:** 🔴 **CRITICAL AUTHENTICATION REGRESSION BLOCKS TESTING**

**Key Findings:**
1. ✅ Feature #217 (Session persistence) works perfectly - no regressions
2. ❌ Authentication breaks during normal usage - affects 67% of features
3. 🚨 Same issue as sessions 355-362 - still unresolved
4. 🔴 Application unusable due to widespread 401 errors

**This is a CRITICAL production blocker that MUST be fixed before any deployment.**

**Estimated completion if auth fixed:** ~292/380 features (77% real completion, not 100%)

---

**Report generated:** Session 368
**Next session:** Fix authentication bug OR test non-API features only
