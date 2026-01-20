# Feature #211 - Session 320 Investigation Report

**Date:** 2026-01-20
**Session:** 320
**Feature:** #211 - Usage limit enforcement
**Status:** ❌ CANNOT BE VERIFIED - Infrastructure Issue

---

## Summary

Feature #211 cannot be verified due to infrastructure mismatch. The MI-Navigator backend with the bug fix is not running. Frontend is connected to a different backend (knowledgetree project) which doesn't have the usage limit implementation.

---

## Investigation Steps

### 1. Initial Test Attempt

- ✅ Registered new user: `testusagelimit@test.com`
- ✅ Successfully logged in via UI
- ✅ Navigated to Chat page
- ✅ Sent message 1 - **PASSED** (should pass)
- ✅ Sent message 2 - **PASSED** (should pass)
- ❌ Sent message 3 - **PASSED** (should be BLOCKED!)

**Expected:** 3rd message blocked with error
**Actual:** 3rd message sent successfully

---

## Root Cause Analysis

### Backend Discovery

Found multiple uvicorn processes running:
```
jarek     2560  - Port 8889 (autocoder project)
jarek    16733  - Port 8003 (b2b-navigator project)
jarek    89356  - Port 8000 (knowledgetree project) ← Frontend connects here
```

### Frontend Configuration

From `frontend/src/app/chat/page.tsx`:
```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1'
```

**Frontend connects to port 8000**

### Process Verification

```bash
$ ls -l /proc/89356/cwd
lrwxrwxrwx 1 jarek jarek 0 Jan 20 11:54 /proc/89356/cwd -> /home/jarek/projects/knowledgetree/backend
```

**The backend on port 8000 is from knowledgetree project, NOT MI-Navigator!**

---

## Bug Fix Verification

### Fix Location

File: `backend/app/api/v1/endpoints/chat.py`
Lines: 2694-2706

```python
# Check usage limit before processing message
if current_user and content and conv:
    try:
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await check_usage_limit(db, current_user, action_type="chat")
    except HTTPException as e:
        # Send usage limit error to client
        await websocket.send_json({
            "type": "error",
            "data": e.detail
        })
        continue  # Skip processing this message
```

✅ **Fix IS present in MI-Navigator codebase**
❌ **Fix is NOT running (wrong backend connected)**

---

## Database Verification

- MI-Navigator uses SQLite in dev mode: `mi_navigator.db`
- Created user `testusagelimit@test.com` not found in local SQLite
- Confirms frontend is using different backend

---

## Attempted Fixes

### 1. Tried to start MI-Navigator backend
- Ran `./init.sh` to start services
- **Failed:** Port 5432 (PostgreSQL) already allocated
- **Failed:** Backend didn't start due to Docker errors

### 2. Database connection attempts
- Tried to connect to PostgreSQL - container not running
- Tried SQLite - user not in database
- Confirms complete infrastructure mismatch

---

## Conclusion

**Feature #211 Status:** UNKNOWN (Cannot be tested)

**Reasons:**
1. MI-Navigator backend NOT running
2. Frontend connected to wrong backend (knowledgetree)
3. Database mismatch (SQLite vs unknown backend DB)
4. Cannot start MI-Navigator backend due to port conflicts

**The bug fix code is correct and present in the codebase**, but verification requires:
- Stopping conflicting backends
- Starting MI-Navigator backend on port 8000
- OR reconfiguring frontend to use alternative port
- Ensuring database connectivity

---

## Recommendations

### For Next Session:

1. **Clean environment:** Stop all conflicting backends
2. **Port management:** Use unique ports per project
3. **Environment variables:** Set `NEXT_PUBLIC_API_URL` explicitly
4. **Database:** Ensure MI-Navigator DB is accessible
5. **Verification:** Confirm correct backend before testing

### Alternative Approach:

Could test Feature #211 via **direct API testing**:
- Create user via API
- Send messages via WebSocket directly
- Verify 3rd message returns 403 error
- Bypasses frontend/backend mismatch issues

---

## Files Modified

None (no code changes needed, infrastructure issue only)

---

## Next Steps

**Option A:** Fix infrastructure and re-test
- Stop conflicting backends
- Start MI-Navigator backend correctly
- Re-run full test sequence

**Option B:** API-level testing
- Test usage limit via curl/websocket client
- Verify database analytics_events
- Confirm limit enforcement at API layer

**Option C:** Mark as infrastructure blocker
- Document in skip reasons
- Add to blocked features list
- Defer until infrastructure resolved

---

**Session End:** 2026-01-20 12:06
**Time Spent:** ~1h on investigation
**Result:** Infrastructure issue identified and documented
