# Feature #91 Fix Plan: Remove Mock Data

## Problem Summary
Dashboard shows hardcoded mock data for ALL users, including brand new users with no data.

## Files with Mock Data

### 1. backend/app/api/v1/endpoints/activity.py
- Lines 37-168: `generate_mock_activities()` - Hardcoded mock activities
- Line 168: `MOCK_ACTIVITIES` used by all endpoints
- Line 206: Endpoint returns MOCK_ACTIVITIES instead of user-specific data

**Issue**: All users see the same mock activities regardless of their actual usage.

### 2. backend/app/api/v1/endpoints/alerts.py
- Lines 25-81: `generate_mock_alerts()` - Hardcoded mock alerts
- Lines 87-91: `get_user_alerts()` - Initializes new users with mock data
- Line 170: Returns mock alerts for all users

**Issue**: New users immediately get 5 pre-generated alerts.

### 3. frontend/src/app/dashboard/page.tsx
- Lines 718-803: `ActiveResearchWidget` - NOW FIXED (fetches from API)
- But backend endpoint `/research/active` doesn't exist yet

## Required Fixes

### Phase 1: Empty States (Quick Win)
1. ✅ Update `ActiveResearchWidget` to fetch from API
2. ⬜ Create backend endpoint `/api/v1/research/active` that returns empty list for new users
3. ⬜ Update `activity.py` to return empty list for new users (no mock data)
4. ⬜ Update `alerts.py` to return empty list for new users (no mock data)

###Phase 2: Real Data (Full Fix)
1. Create database models:
   - `Activity` table with user_id, type, title, description, metadata, timestamp
   - `Alert` table with user_id, severity, title, description, source, company, created_at, read
   - `Research` table with user_id, name, status, progress, created_at

2. Create migration files

3. Update endpoints to:
   - Log real activities when users perform actions
   - Create alerts based on monitoring rules
   - Track research sessions

4. Update services to emit activity events

## Testing Plan
1. Create new user
2. Navigate to dashboard
3. Verify all widgets show empty states:
   - "No active research. Start a new analysis!"
   - "Brak ostatniej aktywności"
   - "No alerts"
   - "No projects yet" (already working)

## Current Status
- **Phase 1.1**: ✅ Frontend updated
- **Phase 1.2**: ⬜ Backend needs endpoints
- **Phase 1.3**: ⬜ Activity endpoint needs fixing
- **Phase 1.4**: ⬜ Alerts endpoint needs fixing
