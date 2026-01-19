# Session 239 - CSRF Token Issue Discovered

## Date: 2026-01-19 19:40

## Issue Summary

During regression testing for Feature #242 (Comment reply functionality) and Feature #49 (Report embed code generation), I discovered a critical issue with CSRF token management that prevents users from creating projects after login.

## Problem Description

**Symptom:**
- Users who are already logged in (from previous sessions) cannot create new projects
- POST request to `/api/v1/projects/` returns 403 Forbidden
- Error message: "CSRF token missing or invalid"

**Root Cause:**
The CSRF token is only fetched during the login flow (`frontend/src/app/auth/login/page.tsx:178`). Users who remain logged in across sessions (token still valid) do not have a CSRF token in localStorage, causing all POST/PUT/DELETE/PATCH requests to fail.

## Evidence

Backend logs show:
```
[CSRF] Blocking request to /api/v1/projects/ - invalid/missing CSRF token
INFO: 127.0.0.1:40232 - "POST /api/v1/projects/ HTTP/1.1" 403 Forbidden
```

Browser console shows:
```
Access to fetch at 'http://localhost:8000/api/v1/projects/' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Workaround Applied

Manually fetched CSRF token via browser console:
```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/csrf-token');
const data = await response.json();
localStorage.setItem('mi_navigator_csrf_token', data.csrf_token);
```

After applying workaround, project creation succeeded.

## Recommended Fix

**Option 1 (Preferred):** Fetch CSRF token on app initialization
- Add CSRF token fetch to app layout or root component
- Ensures token is available even for already-logged-in users
- Location: `frontend/src/app/layout.tsx` or create a `CSRFProvider` component

**Option 2:** Fetch CSRF token on first API error
- Modify `fetchApi` in `frontend/src/services/api.ts`
- On 403 with "CSRF token missing", fetch token and retry
- Similar to existing 401 token refresh logic

**Option 3:** Remove CSRF protection (NOT RECOMMENDED)
- Security vulnerability
- Only for development/testing

## Impact

**Severity:** HIGH
- Affects all authenticated users who don't re-login
- Blocks critical functionality: project creation, report saving, data modification
- User experience severely degraded

**Affected Features:**
- Project creation (confirmed)
- Report saving (likely affected)
- Any POST/PUT/DELETE endpoints (likely affected)

## Files Involved

- `backend/app/core/csrf.py` - CSRF middleware
- `backend/app/api/v1/endpoints/auth.py:552` - CSRF token endpoint
- `frontend/src/services/api.ts:57-71` - CSRF token fetching
- `frontend/src/services/api.ts:96-102` - CSRF token usage
- `frontend/src/app/auth/login/page.tsx:178` - Token fetch on login

## Status

- Issue: IDENTIFIED
- Workaround: APPLIED (manual fetch)
- Fix: PENDING
- Priority: HIGH (should be fixed before Feature #200 implementation)

## Next Steps

1. Implement proper CSRF token initialization on app load
2. Test that all POST/PUT/DELETE endpoints work after refresh
3. Verify token refresh/rotation works correctly
4. Add error handling for expired CSRF tokens
5. Resume regression testing after fix
