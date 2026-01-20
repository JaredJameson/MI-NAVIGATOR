# SESSION 327 - CRITICAL BUG REPORT

**Date:** 2026-01-20
**Session:** 327
**Feature:** #10 "User data isolation"
**Status:** ❌ **FAILING** (CRITICAL SECURITY BUG)

---

## 🚨 EXECUTIVE SUMMARY

Feature #10 "User data isolation" is **BROKEN**. Users receive **403 Forbidden** when trying to access their OWN reports. This is a **CRITICAL SECURITY REGRESSION** that was previously fixed in Session 325 but has returned due to a different root cause.

---

## PROBLEM DESCRIPTION

**Symptom:**
- User can see list of reports (1000 auto-generated pagination test reports)
- When user clicks on ANY report, they get "403 Forbidden"
- Error message: "Nie masz uprawnień do wyświetlenia tego raportu" (You don't have permissions to view this report)

**Impact:**
- Users CANNOT access their own reports
- Complete breakdown of reports functionality
- Security vulnerability (though ironically blocking too much, not too little)

---

## ROOT CAUSE ANALYSIS

### The Problem

`MOCK_REPORTS` is a **global in-memory list** shared across ALL requests and ALL users. When multiple users access the system:

1. **User A** calls `/api/v1/reports/` (LIST endpoint)
   - Backend filters: `filtered_reports = [r for r in MOCK_REPORTS if r.get("created_by") == userA_id]`
   - Result: 0 reports (first time user)
   - Backend generates: 1000 reports with IDs `pagination_test_0001` to `pagination_test_1000`
   - All reports have `created_by = userA_id`
   - Backend adds to global list: `MOCK_REPORTS.extend(test_reports)`

2. **User B** calls `/api/v1/reports/` (LIST endpoint)
   - Backend filters: `filtered_reports = [r for r in MOCK_REPORTS if r.get("created_by") == userB_id]`
   - Result: 0 reports (no reports belong to User B)
   - Backend generates: 1000 NEW reports with SAME IDs `pagination_test_0001` to `pagination_test_1000`
   - All reports have `created_by = userB_id`
   - Backend adds to global list: `MOCK_REPORTS.extend(test_reports)`
   - **NOW MOCK_REPORTS HAS DUPLICATES!**

3. **User B** tries to open report `pagination_test_0001`
   - Backend searches: `for report in MOCK_REPORTS: if report["id"] == report_id`
   - **Finds FIRST match** → This is User A's report!
   - Backend checks: `if report.get("created_by") != str(current_user.id)` → **MISMATCH!**
   - Backend returns: **403 Forbidden**

### The Code

**File:** `backend/app/api/v1/endpoints/reports.py`

**Problematic section (lines 1156-1169):**
```python
# SECURITY: Only show reports belonging to the current user
user_id = str(current_user.id)
filtered_reports = [r for r in MOCK_REPORTS if r.get("created_by") == user_id]

# AUTO-GENERATE TEST DATA: If user has no reports, generate 1000 test reports for testing
if len(filtered_reports) == 0:
    # BUGFIX Session 327: Remove old pagination test reports to avoid ID conflicts
    # When backend restarts, MOCK_REPORTS gets reset but may contain old pagination_test_* reports
    # from previous sessions with different user_ids, causing 403 errors
    MOCK_REPORTS[:] = [r for r in MOCK_REPORTS if not r["id"].startswith("pagination_test_")]

    test_reports = generate_pagination_test_reports(1000, user_id)
    MOCK_REPORTS.extend(test_reports)  # ← THIS LINE CREATES DUPLICATES
    filtered_reports = test_reports
```

**GET endpoint (lines 1519-1532):**
```python
@router.get("/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get report details."""
    for report in MOCK_REPORTS:  # ← ITERATES AND FINDS FIRST MATCH
        if report["id"] == report_id:
            # SECURITY: Check if user is the owner of the report
            if report.get("created_by") and report.get("created_by") != str(current_user.id):
                raise HTTPException(
                    status_code=403,
                    detail="Nie masz uprawnień do wyświetlenia tego raportu."
                )  # ← 403 HERE!
```

---

## ATTEMPTED FIX (INCOMPLETE)

**What I tried:**
Added code to remove old `pagination_test_*` reports before generating new ones:

```python
MOCK_REPORTS[:] = [r for r in MOCK_REPORTS if not r["id"].startswith("pagination_test_")]
```

**Why it didn't fully work:**
- The fix removes duplicates IN THEORY
- BUT backend restart resets `MOCK_REPORTS` to initial state
- Duplicates from previous backend runs may still exist
- In-place modification `[:]` works but timing matters

---

## COMPLETE SOLUTION (TODO)

### Option 1: Per-User Unique IDs (RECOMMENDED)

Modify `generate_pagination_test_reports()` to include user_id in report IDs:

```python
def generate_pagination_test_reports(count: int = 1000, user_id: str):
    """Generate test reports with per-user unique IDs"""
    reports = []
    # Use first 8 chars of user_id to make IDs unique per user
    user_prefix = user_id[:8]

    for i in range(1, count + 1):
        report = {
            "id": f"pagination_test_{user_prefix}_{i:04d}",  # ← UNIQUE!
            "title": f"Pagination Test Report #{i}",
            # ... rest of fields
            "created_by": user_id,
        }
        reports.append(report)
    return reports
```

**Pros:**
- Completely prevents ID collisions
- No need to remove old reports
- Scalable to unlimited users

**Cons:**
- Changes report IDs (but these are test data anyway)

### Option 2: Deduplicate on GET

Modify GET endpoint to find the CORRECT report when duplicates exist:

```python
@router.get("/{report_id}")
async def get_report(report_id: str, current_user: User = Depends(get_current_user)):
    user_id = str(current_user.id)

    # Find ALL reports with this ID
    matching_reports = [r for r in MOCK_REPORTS if r["id"] == report_id]

    # Find the one belonging to current user
    user_report = next((r for r in matching_reports if r.get("created_by") == user_id), None)

    if not user_report:
        # No report with this ID belongs to this user
        raise HTTPException(status_code=404, detail="Report not found")

    # Check ownership (redundant but safe)
    if user_report.get("created_by") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Return the correct report
    return ReportDetail(...)
```

**Pros:**
- Works with existing data
- Handles duplicates gracefully

**Cons:**
- Doesn't fix root cause
- Performance impact (searches all reports)

### Option 3: Robust Cleanup on LIST

Improve the cleanup logic:

```python
if len(filtered_reports) == 0:
    # Remove ALL pagination_test reports (not just ours)
    MOCK_REPORTS[:] = [r for r in MOCK_REPORTS if not r["id"].startswith("pagination_test_")]

    # Generate new reports
    test_reports = generate_pagination_test_reports(1000, user_id)

    # Add them
    MOCK_REPORTS.extend(test_reports)
    filtered_reports = test_reports
```

**Pros:**
- Simple fix
- Removes all duplicates

**Cons:**
- Deletes other users' test reports (not ideal but acceptable for test data)

---

## RECOMMENDED ACTION

**Implement Option 1** (Per-User Unique IDs) as it's the cleanest solution that:
1. Prevents the problem at the source
2. Scales to unlimited users
3. Requires minimal code changes
4. Doesn't affect other users

---

## TESTING PROTOCOL

After implementing fix:

1. **Start fresh backend** (kill and restart to reset MOCK_REPORTS)
2. **Create User A** and login
3. **Navigate to /reports** → should see 1000 reports
4. **Click first report** → should open successfully (200 OK)
5. **Logout**
6. **Create User B** and login
7. **Navigate to /reports** → should see 1000 DIFFERENT reports
8. **Click first report** → should open successfully (200 OK)
9. **Verify User A's reports have different IDs than User B's reports**

**Success criteria:**
- ✅ No 403 errors
- ✅ Each user sees their own reports
- ✅ Report IDs are unique per user
- ✅ No duplicates in MOCK_REPORTS

---

## FILES MODIFIED

- `backend/app/api/v1/endpoints/reports.py` (lines 1162-1165) - Partial fix added
- Screenshots captured in `.playwright-mcp/regression_feature10_*.png`

---

## STATUS

- Feature #10: ❌ **FAILING**
- Fix status: ⚠️ **PARTIAL** (attempted but incomplete)
- Severity: 🚨 **CRITICAL** (blocks core functionality)
- Next action: Implement Option 1 (Per-User Unique IDs)

---

**Session End:** 2026-01-20 13:35
**Next Session TODO:** Complete the fix using Option 1 and verify with full regression test
