# REGRESSION FAILURE: Feature #51 - Company Profile from CEIDG

**Date:** 2026-01-19
**Session:** #236
**Status:** ❌ FAILED
**Severity:** HIGH - Core functionality broken

---

## Summary

Feature #51 (Company profile from CEIDG) has regressed. The NIP lookup functionality fails to execute research and instead returns a generic welcome message.

---

## Test Details

### Expected Behavior
When entering a NIP number of a sole proprietor (CEIDG company):
1. System detects NIP
2. User clicks "Lookup Company"
3. Brief questions collect research parameters
4. System executes research plan
5. **CEIDG data is fetched and displayed**
6. Company name, owner, address, PKD codes are shown

### Actual Behavior
1. ✅ System detects NIP correctly
2. ✅ "Lookup Company" button appears
3. ✅ Brief questions work (objective, scope, depth)
4. ✅ Research plan is generated
5. ✅ User proceeds with plan
6. ❌ **System returns generic welcome message instead of executing research**

---

## Reproduction Steps

1. Navigate to http://localhost:3000/chat
2. Enter text: "Podaj informacje o firmie NIP 5170359498"
3. Click "Lookup Company" button
4. Answer brief questions:
   - Objective: "Podstawowa weryfikacja firmy"
   - Scope: "Company only"
   - Depth: "Executive Summary"
5. Click "✓ Proceed with Plan"
6. **OBSERVED:** Generic welcome message appears
7. **EXPECTED:** Research executes and CEIDG data is displayed

---

## Technical Analysis

### Frontend Behavior
- ✅ WebSocket connects successfully
- ✅ NIP detection works (`5170359498` detected)
- ✅ Brief question flow completes
- ✅ Plan generation succeeds
- ❌ After "Proceed with Plan", receives wrong response

### Backend Logs
```
INFO: WebSocket /api/v1/chat/ws/790a52c1-a794-4bb5-adc0-793af252cc81 [accepted]
```

- WebSocket connection established
- No further processing logs visible
- No error messages in backend logs
- Suggests message routing or agent invocation failure

### Console Errors
```
[ERROR] Failed to load resource: 401 (Unauthorized) @ /api/v1/users/me
[ERROR] Failed to load resource: 401 (Unauthorized) @ /api/v1/research/active
[ERROR] Failed to load resource: 401 (Unauthorized) @ /api/v1/projects/
```

**Note:** These 401 errors appear throughout the app, suggesting a broader authentication issue that may or may not be related to this specific bug.

---

## Response Received

```
"Dziekuje za wiadomosc. Jestem asystentem Market Intelligence i pomagam w:
- Analizie firm i konkurencji
- Tworzeniu raportow biznesowych
- Monitorowaniu rynku

Czy chcialbys przeprowadzic analize konkretnej firmy lub uzyskac raport?
Podaj wiecej szczegolow, a chetnie pomoge."
```

This is a **fallback/default greeting message**, not the expected research execution.

---

## Conversation Flow

```
User Message: "Lookup company with NIP: 5170359498"
↓
Brief Questions (3 questions answered)
↓
Plan Generated (confirmed by user)
↓
❌ FAILURE POINT: Generic response instead of research execution
```

---

## Hypotheses

### 1. Agent Routing Failure
- The message after plan confirmation may not be routing to Orchestrator
- Could be hitting a fallback conversational agent instead
- Router might not recognize the "proceed with plan" signal

### 2. WebSocket Message Format Issue
- Plan confirmation message format may be incorrect
- Backend may not parse the "confirm" action properly
- Message type mismatch between frontend and backend

### 3. Orchestrator Not Invoked
- Research plan exists but Orchestrator never receives execution command
- Could be middleware issue between Router and Orchestrator
- Agent chain may be broken

### 4. Authentication Side Effect
- Multiple 401 errors suggest auth issues
- May affect certain agent operations
- Could block external API calls (CEIDG)

---

## Files to Investigate

### Backend
```
backend/app/api/v1/chat.py          # WebSocket handler
backend/app/services/router.py       # Message routing
backend/app/services/orchestrator.py # Research execution
backend/app/agents/router_agent.py   # Agent routing logic
```

### Frontend
```
frontend/src/app/chat/page.tsx       # WebSocket client
frontend/src/services/chat.ts        # Chat service
```

---

## Impact Assessment

**Severity:** HIGH
- Core feature completely broken
- Affects all company lookup functionality
- Blocks:
  - Feature #51 (CEIDG lookups)
  - Feature #196 (Quick research - current test)
  - Potentially all research features

**User Impact:**
- Cannot perform company lookups
- Research functionality non-operational
- System appears to work but doesn't execute

---

## Next Steps

1. ✅ Document regression (this file)
2. ⬜ Investigate WebSocket message flow in backend
3. ⬜ Check Router agent logic for plan confirmation handling
4. ⬜ Verify Orchestrator invocation
5. ⬜ Add debug logging to trace message path
6. ⬜ Fix identified issue
7. ⬜ Re-test Feature #51
8. ⬜ Re-test Feature #196

---

## Screenshots

- `feature51_regression_failure.png` - Shows generic response instead of research execution

---

## Related Issues

- Multiple 401 (Unauthorized) errors on various endpoints
- May indicate broader system authentication issues
- Should be investigated separately

---

## Conclusion

Feature #51 has completely regressed. The NIP lookup flow appears to work through plan generation, but fails at execution. This is a critical bug that blocks all research functionality and must be fixed before marking any new features as passing.

**Action Required:** Fix this regression before proceeding with Feature #196 or any other tests.
