# Frontend i18n Roadmap - MI-Navigator
## Complete Internationalization Strategy (Polish + English)

**Created**: 2026-01-29
**Updated**: 2026-02-02 (Session 418 - Core Detail Pages STARTED)
**Status**: 🔄 **IN PROGRESS** (55% complete - 29/53 pages)
**Framework**: next-intl with cookie-based locale detection
**Languages**: Polish (pl - default), English (en)
**Target**: 100% frontend i18n coverage across all 53 pages

---

## 📊 Current Status (Session 418 - 2026-02-02)

### ✅ Completed Pages (29/53 = 55%)

**Session 381** (2026-01-28):
1. ✅ **Activity page** (`/activity`) - User activity log
2. ✅ **Feedback page** (`/feedback`) - User feedback submission
3. ✅ **Onboarding page** (`/onboarding`) - New user onboarding
4. ✅ **Offline page** (`/offline`) - PWA offline state
5. ✅ **Maintenance page** (maintenance mode) - System maintenance

**Session 382** (2026-01-29):
6. ✅ **Notifications page** (`/notifications`, 314 lines) - User notifications
7. ✅ **Invitations page** (`/invitations`, 338 lines) - Workspace invitations
8. ✅ **Chat page** (`/chat`, 1,517 lines) - AI chat interface (LARGEST & MOST COMPLEX)

**Session 394** (2026-01-29) - Test Pages (Production Quality):
9. ✅ **test-error** (149 lines) - Error tracking test
10. ✅ **test-pwa** (111 lines) - PWA Service Worker test
11. ✅ **test-offline** (145 lines) - Offline indicator test
12. ✅ **test-ab** (164 lines) - A/B testing demo
13. ✅ **test-batch-progress** (226 lines) - Batch progress tracking
14. ✅ **test-cancel** (335 lines) - Cancel operation test
15. ✅ **test-chart-colors** (309 lines) - Chart color accessibility
16. ✅ **test-print-preview** (218 lines) - Print preview test
17. ✅ **test-retry** (372 lines) - Retry failed operation test
18. ✅ **test-skeleton** (165 lines) - Skeleton loading states
19. ✅ **test-sync** (287 lines) - Data sync on reconnection
20. ✅ **test-timeout** (220 lines) - Timeout handling test
21. ✅ **test-table-scroll** (165 lines) - Table horizontal scroll
22. ✅ **test-table-sorting** (70 lines) - Table sorting functionality

**Session 417** (2026-02-02) - Authentication Pages (COMPLETE):
23. ✅ **auth/login** - Login page with email/password
24. ✅ **auth/register** - Registration with full validation
25. ✅ **auth/forgot-password** - Password reset request
26. ✅ **auth/reset-password** - Password reset completion
27. ✅ **auth/verify-email** - Email verification instructions
28. ✅ **auth/verify/[token]** - Token verification (4 states)

**Session 418** (2026-02-02) - Core Detail Pages (STARTED):
29. ✅ **page.tsx** (root) - Root landing page with redirect
30. 🔄 **companies/[id]/page.tsx** - PARTIAL (Data Quality & Conflicts sections + loading states)

### 📈 Translation Coverage

**Translation Keys**:
- **Total**: ~1,485 keys across pl.json + en.json
- **Session 381**: ~120 keys (activity, feedback, onboarding, offline, maintenance)
- **Session 382**: ~105 keys (notifications, invitations, chat)
- **Session 394**: ~920 keys (14 test pages, ~460 per language)
- **Session 417**: ~300 keys (6 Authentication pages, ~150 per language)
- **Session 418**: ~40 keys (root + companies/[id] Data Quality/Conflicts sections, ~20 per language)

**Test Pages Translation Keys Breakdown**:
- test-error: ~35 keys
- test-pwa: ~20 keys
- test-offline: ~40 keys
- test-ab: ~45 keys
- test-batch-progress: ~60 keys
- test-cancel: ~85 keys
- test-chart-colors: ~70 keys
- test-print-preview: ~55 keys
- test-retry: ~95 keys
- test-skeleton: ~50 keys
- test-sync: ~120 keys
- test-timeout: ~70 keys
- test-table-scroll: ~25 keys
- test-table-sorting: ~30 keys

**Authentication Pages Translation Keys Breakdown** (Session 417):
- auth/login: ~8 keys (placeholders, labels)
- auth/register: ~35 keys (form fields, validation errors, states)
- auth/forgot-password: ~20 keys (form, success screen, errors)
- auth/reset-password: ~30 keys (validation, fields, states)
- auth/verify-email: ~30 keys (instructions, tips, resend functionality)
- auth/verify/[token]: ~27 keys (4 states: loading, success, already_verified, error)

**Core Detail Pages Translation Keys Breakdown** (Session 418):
- page.tsx (root): ~1 key (loading message)
- companies/[id]/page.tsx (PARTIAL): ~19 keys per language:
  - conflicts.*: 11 keys (title, description, loading, verified, recommended, source, confidence, lastUpdated, noConflicts, allConsistent, foundValues)
  - dataQuality.*: 4 keys (title, improvements, loadingMetrics, noData, loadError)
  - timeline.*: 3 keys (loading, noEventsDescription, source)
  - news.*: 2 keys (loading, noArticlesDescription)
  - Note: Page is PARTIALLY translated - many sections still have hardcoded Polish strings (Financials, People, Timeline details, etc.)

**Key Features Implemented**:
- ✅ Cookie-based locale detection (NEXT_LOCALE)
- ✅ Header propagation for SSR (x-locale)
- ✅ Parameter interpolation (`{count}`, `{filename}`, `{date}`)
- ✅ Nested translation structure
- ✅ SSR-safe implementation patterns
- ✅ Emoji removal for text-based i18n

---

## 🎯 Remaining Work (25 pages = 47%)

### **High Priority Pages** (12 pages) - Core User Journeys

**Estimated Effort**: 8-10 hours total

1. **Dashboard** (`/dashboard`) - Main landing page
   - **Complexity**: HIGH (charts, widgets, real-time data)
   - **Estimated**: 1.5 hours
   - **Keys**: ~40 (metrics, widgets, actions)

2. **Reports List** (`/reports`) - Report listing and management
   - **Complexity**: HIGH (tables, filters, sorting)
   - **Estimated**: 1 hour
   - **Keys**: ~35 (columns, filters, actions)

3. **Report Detail** (`/reports/[id]`) - Individual report view (6,794 lines - LARGEST FILE)
   - **Complexity**: VERY HIGH (54 functions, complex visualizations)
   - **Estimated**: 2.5 hours
   - **Keys**: ~80 (sections, charts, metrics, actions)

4. **Settings** (`/settings`) - User settings hub
   - **Complexity**: MEDIUM (navigation, sections)
   - **Estimated**: 0.5 hours
   - **Keys**: ~25 (navigation, sections)

5. **Settings - Workspace** (`/settings/workspace`) - Workspace configuration
   - **Complexity**: MEDIUM (forms, validation)
   - **Estimated**: 0.5 hours
   - **Keys**: ~30 (fields, validation, actions)

6. **Settings - Security** (`/settings/security`) - Security settings (2FA, etc.)
   - **Complexity**: MEDIUM (forms, sensitive operations)
   - **Estimated**: 0.5 hours
   - **Keys**: ~30 (fields, warnings, actions)

7. **Companies List** (`/companies`) - Company directory
   - **Complexity**: MEDIUM (search, filters, cards)
   - **Estimated**: 0.5 hours
   - **Keys**: ~30 (filters, sorting, actions)

8. 🔄 **Company Detail** (`/companies/[id]`) - Individual company view (1,997 lines) - **PARTIAL**
   - **Complexity**: HIGH (multiple sections, data visualization)
   - **Estimated**: 1.5 hours total, ~0.5 hours remaining
   - **Keys**: ~50 total (~19 done, ~31 remaining)
   - **Status**: Session 418 - Data Quality & Conflicts sections COMPLETE, Timeline/News/Financials/People sections have hardcoded Polish strings remaining

9. **Search** (`/search`) - Global search interface
   - **Complexity**: HIGH (filters, results, facets)
   - **Estimated**: 1 hour
   - **Keys**: ~35 (filters, results, actions)

10. **Analysis** (`/analysis`) - Analysis tools hub
    - **Complexity**: MEDIUM (navigation, tools)
    - **Estimated**: 0.5 hours
    - **Keys**: ~25 (tools, descriptions, actions)

11. **Analysis - SWOT** (`/analysis/swot`) - SWOT analysis tool
    - **Complexity**: HIGH (interactive forms, visualization)
    - **Estimated**: 0.5 hours
    - **Keys**: ~30 (quadrants, fields, actions)

12. **Not Found** (`/not-found`) - 404 error page
    - **Complexity**: LOW (simple error page)
    - **Estimated**: 0.25 hours
    - **Keys**: ~10 (message, actions)

### **Medium Priority Pages** (10 pages) - Important Features

**Estimated Effort**: 5-7 hours total

13. **Alerts** (`/alerts`) - Alert management
    - **Complexity**: MEDIUM (list, filters, actions)
    - **Estimated**: 0.5 hours
    - **Keys**: ~30

14. **Alert Detail** (`/alerts/[id]`) - Individual alert view
    - **Complexity**: MEDIUM (details, actions)
    - **Estimated**: 0.5 hours
    - **Keys**: ~25

15. **Alert Create/Edit** (`/alerts/new`, `/alerts/edit/[id]`) - Alert forms
    - **Complexity**: MEDIUM (forms, validation)
    - **Estimated**: 0.75 hours
    - **Keys**: ~35

16. **Projects** (`/projects`) - Project management
    - **Complexity**: MEDIUM (list, cards, actions)
    - **Estimated**: 0.5 hours
    - **Keys**: ~30

17. **Admin** (`/admin`) - Admin dashboard
    - **Complexity**: MEDIUM (metrics, actions)
    - **Estimated**: 0.5 hours
    - **Keys**: ~30

18. **Admin - Users** (`/admin/users`) - User management
    - **Complexity**: HIGH (table, filters, actions)
    - **Estimated**: 1 hour
    - **Keys**: ~40

19. **Watchlist** (`/watchlist`) - Saved companies
    - **Complexity**: MEDIUM (list, actions)
    - **Estimated**: 0.5 hours
    - **Keys**: ~25

20. **Compare** (`/compare`) - Company comparison
    - **Complexity**: HIGH (side-by-side comparison)
    - **Estimated**: 1 hour
    - **Keys**: ~40

21. **Competitive** (`/competitive`) - Competitive analysis
    - **Complexity**: HIGH (complex visualizations)
    - **Estimated**: 1 hour
    - **Keys**: ~40

22. **Help** (`/help`) - Help and documentation
    - **Complexity**: LOW (documentation pages)
    - **Estimated**: 0.5 hours
    - **Keys**: ~20

### **Lower Priority Pages** (10+ pages) - Settings, Testing, Specialized

**Estimated Effort**: 4-6 hours total

**Settings Pages** (6 pages):
23. **Settings - Privacy** (`/settings/privacy`)
24. **Settings - API Keys** (`/settings/api-keys`)
25. **Settings - API Usage** (`/settings/api-usage`)
26. **Settings - Audit** (`/settings/audit`)
27. **Settings - Webhooks** (`/settings/webhooks`)
28. **Settings - Feature Flags** (`/settings/feature-flags`)
29. **Settings - Tags** (`/settings/tags`)
30. **Settings - Billing** (`/settings/billing`)
31. **Settings - Billing Upgrade/Downgrade** (`/settings/billing/upgrade`, `/settings/billing/downgrade`)
32. **Settings - Payment Methods** (`/settings/billing/payment-methods`)

**Specialized Pages** (4 pages):
33. **Share** (`/share/[token]`) - Shared report viewing
34. **Company Schedules** (`/companies/schedules`) - Schedule management
35. **Report Templates** (`/reports/templates`) - Report templates
36. **Report Infinite Scroll Test** (`/reports/infinite`) - Infinite scroll testing

**Test Pages** ✅ **COMPLETED in Session 394** (14 pages):
- ✅ `/test-error` - Error boundary testing (149 lines)
- ✅ `/test-pwa` - PWA functionality testing (111 lines)
- ✅ `/test-offline` - Offline functionality testing (145 lines)
- ✅ `/test-ab` - A/B testing demonstration (164 lines)
- ✅ `/test-batch-progress` - Batch progress UI testing (226 lines)
- ✅ `/test-cancel` - Cancellation flow testing (335 lines)
- ✅ `/test-chart-colors` - Chart color palette testing (309 lines)
- ✅ `/test-print-preview` - Print preview testing (218 lines)
- ✅ `/test-retry` - Retry logic testing (372 lines)
- ✅ `/test-skeleton` - Skeleton loading testing (165 lines)
- ✅ `/test-sync` - Sync queue testing (287 lines)
- ✅ `/test-timeout` - Timeout handling testing (220 lines)
- ✅ `/test-table-scroll` - Table scrolling testing (165 lines)
- ✅ `/test-table-sorting` - Table sorting testing (70 lines)

---

## 📅 Implementation Timeline

### Phase 1: High Priority Pages (Sessions 383-387)
**Duration**: 5 sessions (~8-10 hours)
**Pages**: 12 core pages
**Target Completion**: Week 23 (Early February 2026)

**Session 383** (2 hours):
- Dashboard (1.5h)
- Settings hub (0.5h)

**Session 384** (2 hours):
- Report List (1h)
- Companies List (0.5h)
- Settings - Workspace (0.5h)

**Session 385** (2.5 hours):
- Report Detail (2.5h) - LARGEST FILE, needs dedicated session

**Session 386** (2 hours):
- Company Detail (1.5h)
- Settings - Security (0.5h)

**Session 387** (2 hours):
- Search (1h)
- Analysis hub (0.5h)
- SWOT Analysis (0.5h)
- Not Found (0.25h)

### Phase 2: Medium Priority Pages (Sessions 388-390)
**Duration**: 3 sessions (~5-7 hours)
**Pages**: 10 important feature pages
**Target Completion**: Week 23 (Mid February 2026)

**Session 388** (2.5 hours):
- Alerts pages (2h)
- Projects (0.5h)

**Session 389** (2.5 hours):
- Admin pages (1.5h)
- Watchlist (0.5h)
- Help (0.5h)

**Session 390** (2 hours):
- Compare (1h)
- Competitive (1h)

### Phase 3: Lower Priority Pages (Sessions 391-393)
**Duration**: 3 sessions (~4-6 hours)
**Pages**: 10+ settings and specialized pages
**Target Completion**: Week 24 (Late February 2026)

**Session 391** (2 hours):
- Settings pages (Privacy, API Keys, API Usage, Audit)

**Session 392** (2 hours):
- Settings pages (Webhooks, Feature Flags, Tags, Billing)

**Session 393** (2 hours):
- Specialized pages (Share, Schedules, Templates, Infinite scroll)

### Phase 4: Test Pages ✅ **COMPLETED** (Session 394 - 2026-01-29)
**Duration**: 1 session (~2 hours)
**Pages**: 14 test pages
**Status**: ✅ **COMPLETED**

**Decision**: User chose production-quality implementation for all test pages
**Result**: All 14 test pages fully internationalized with ~920 translation keys

---

## 📋 Session-by-Session Roadmap

### Session 383: Dashboard + Settings Hub
**Priority**: HIGH
**Estimated**: 2 hours

**Tasks**:
1. Dashboard page i18n (1.5h)
   - ~40 translation keys (metrics, widgets, charts, actions)
   - Complex visualizations and real-time data
   - Emoji removal where needed
2. Settings hub page i18n (0.5h)
   - ~25 translation keys (navigation, sections)
   - Simple navigation structure

**Deliverables**:
- Dashboard fully internationalized
- Settings hub fully internationalized
- pl.json + en.json updated with ~65 new keys

### Session 384: Reports + Companies + Settings
**Priority**: HIGH
**Estimated**: 2 hours

**Tasks**:
1. Report List page i18n (1h)
   - ~35 translation keys (columns, filters, sorting, actions)
   - Table headers, filters, pagination
2. Companies List page i18n (0.5h)
   - ~30 translation keys (search, filters, cards)
   - Search interface and filtering
3. Settings - Workspace page i18n (0.5h)
   - ~30 translation keys (forms, validation, actions)
   - Form fields and validation messages

**Deliverables**:
- 3 pages fully internationalized
- pl.json + en.json updated with ~95 new keys

### Session 385: Report Detail (Dedicated)
**Priority**: HIGH
**Estimated**: 2.5 hours

**Tasks**:
1. Report Detail page i18n (2.5h)
   - ~80 translation keys (largest file: 6,794 lines, 54 functions)
   - Multiple sections: header, metrics, charts, tables, actions
   - Complex nested components
   - Special attention to chart labels, axis titles, tooltips

**Deliverables**:
- Report Detail fully internationalized
- pl.json + en.json updated with ~80 new keys
- Most complex page completed

### Session 386: Company Detail + Security
**Priority**: HIGH
**Estimated**: 2 hours

**Tasks**:
1. Company Detail page i18n (1.5h)
   - ~50 translation keys (1,887 lines, multiple sections)
   - Tabs, sections, metrics, visualizations
2. Settings - Security page i18n (0.5h)
   - ~30 translation keys (2FA, password, sessions)
   - Sensitive operations and warnings

**Deliverables**:
- 2 pages fully internationalized
- pl.json + en.json updated with ~80 new keys

### Session 387: Search + Analysis
**Priority**: HIGH
**Estimated**: 2 hours

**Tasks**:
1. Search page i18n (1h)
   - ~35 translation keys (search, filters, results)
   - Faceted search interface
2. Analysis hub page i18n (0.5h)
   - ~25 translation keys (tools, descriptions)
   - Analysis tools overview
3. SWOT Analysis page i18n (0.5h)
   - ~30 translation keys (quadrants, fields, actions)
   - Interactive SWOT builder
4. Not Found page i18n (0.25h)
   - ~10 translation keys (error message, actions)
   - Simple 404 page

**Deliverables**:
- 4 pages fully internationalized
- pl.json + en.json updated with ~100 new keys
- **Phase 1 Complete**: All 12 high-priority pages done

---

## 🔧 Technical Implementation Guidelines

### 1. next-intl Integration Pattern

**Standard Implementation**:
```typescript
import { useTranslations } from 'next-intl'

export default function PageName() {
  const t = useTranslations('pageName')

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
      <button onClick={handleAction}>{t('actions.save')}</button>
    </div>
  )
}
```

**With Parameter Interpolation**:
```typescript
// Translation key: "welcome": "Welcome, {name}!"
{t('welcome', { name: user.name })}

// Translation key: "itemCount": "{count} items found"
{t('itemCount', { count: items.length })}

// Translation key: "lastUpdated": "Last updated: {date}"
{t('lastUpdated', { date: new Date(timestamp).toLocaleDateString() })}
```

**Nested Translations**:
```json
{
  "dashboard": {
    "title": "Dashboard",
    "widgets": {
      "revenue": "Revenue",
      "users": "Active Users"
    },
    "actions": {
      "refresh": "Refresh",
      "export": "Export"
    }
  }
}
```

### 2. Emoji Removal Strategy

**Replace emojis with translation keys**:
```typescript
// Before
<span>⏱️ Estimated time: {minutes} minutes</span>

// After
<span>{t('progress.estimatedTime', { minutes })}</span>
```

**Translation files**:
```json
{
  "pl": {
    "progress": {
      "estimatedTime": "Szacowany czas: {minutes} minut"
    }
  },
  "en": {
    "progress": {
      "estimatedTime": "Estimated time: {minutes} minutes"
    }
  }
}
```

### 3. SSR-Safe Patterns

**Always check for browser-only APIs**:
```typescript
// Good
if (typeof window !== 'undefined') {
  localStorage.setItem('key', value)
}

// Bad
localStorage.setItem('key', value) // ReferenceError during SSR
```

### 4. Dynamic Content Translation

**For dynamic lists**:
```typescript
const statuses = ['pending', 'approved', 'rejected']

{statuses.map(status => (
  <option key={status} value={status}>
    {t(`statuses.${status}`)}
  </option>
))}
```

**Translation files**:
```json
{
  "statuses": {
    "pending": "Oczekujące",
    "approved": "Zatwierdzone",
    "rejected": "Odrzucone"
  }
}
```

### 5. Error Handling Translation

**Comprehensive error messages**:
```typescript
try {
  await uploadFile(file)
} catch (error) {
  if (error.code === 'FILE_TOO_LARGE') {
    setError(t('errors.fileTooLarge', {
      filename: file.name,
      maxSize: '50MB'
    }))
  } else {
    setError(t('errors.uploadFailed'))
  }
}
```

---

## ✅ Quality Assurance Strategy

### 1. Translation Completeness Checklist

**Per Page**:
- [ ] All user-facing text translated
- [ ] All button labels translated
- [ ] All error messages translated
- [ ] All placeholder text translated
- [ ] All tooltip text translated
- [ ] All validation messages translated
- [ ] All dynamic content patterns covered
- [ ] No hardcoded English strings remain

### 2. Testing Checklist

**Per Page**:
- [ ] Polish (pl) language loads correctly
- [ ] English (en) language loads correctly
- [ ] Language switching preserves state
- [ ] Parameter interpolation works
- [ ] Date/number formatting correct
- [ ] No console errors
- [ ] No missing translation warnings
- [ ] SSR renders without errors

### 3. Visual Regression Testing

**Key Areas**:
- Button sizes (text length differences)
- Layout shifts (longer translations)
- Table column widths
- Form field labels
- Modal dialog titles
- Navigation menu items

### 4. Performance Monitoring

**Metrics to Track**:
- Translation bundle size (pl.json + en.json)
- Initial page load time with i18n
- Language switching performance
- Memory usage with loaded translations

---

## 🌍 Future Enhancements (Post-100% Coverage)

### 1. Additional Languages (Priority Order)

**Tier 1** (EU Markets):
- 🇩🇪 German (de) - Major EU economy
- 🇫🇷 French (fr) - EU market
- 🇪🇸 Spanish (es) - EU + Latin America

**Tier 2** (Global Markets):
- 🇮🇹 Italian (it) - EU market
- 🇳🇱 Dutch (nl) - EU market
- 🇵🇹 Portuguese (pt) - EU + Brazil

**Tier 3** (Expansion):
- 🇯🇵 Japanese (ja) - Asia market
- 🇨🇳 Chinese (zh) - Asia market
- 🇰🇷 Korean (ko) - Asia market

### 2. Translation Management System

**Features**:
- Translation key validation
- Missing translation detection
- Unused key cleanup
- Translation memory
- Professional translator portal
- Context screenshots for translators
- Translation approval workflow

### 3. Dynamic Locale Loading

**Optimization**:
```typescript
// Load only needed locale bundle
const messages = await import(`../messages/${locale}.json`)
```

**Benefits**:
- Reduced initial bundle size
- Faster page loads
- On-demand locale loading

### 4. RTL Language Support

**For Arabic/Hebrew** (if needed):
- RTL layout mirroring
- Text direction handling
- Icon flipping
- Date/number formatting

---

## 📊 Success Metrics

### Completion Tracking

| Phase | Pages | Keys | Hours | Target Date | Status |
|-------|-------|------|-------|-------------|--------|
| **Phase 0** (Done) | 8 | ~225 | 10 | 2026-01-29 | ✅ **COMPLETE** |
| **Phase 1** (High) | 12 | ~400 | 10 | Week 23 | ⏳ **NEXT** |
| **Phase 2** (Medium) | 10 | ~300 | 7 | Week 23 | ⏳ **PENDING** |
| **Phase 3** (Low) | 10 | ~200 | 6 | Week 24 | ⏳ **PENDING** |
| **Phase 4** (Test Pages) | 14 | ~920 | 2 | 2026-01-29 | ✅ **COMPLETE** |
| **Phase 5** (Auth Pages) | 6 | ~150 | 1 | 2026-02-02 | ✅ **COMPLETE** |
| **TOTAL** | 53 | ~2,195 | 36 | Week 24 | 🔄 **53% DONE** |

### Quality Metrics

- **Translation Accuracy**: Target ≥95%
- **Coverage**: Target 100% user-facing strings
- **Performance**: <5% overhead vs non-i18n
- **Bundle Size**: <100KB per language file
- **No Console Errors**: 0 missing translation warnings

### User Experience Metrics

- **Language Switching**: <500ms perceived delay
- **Layout Stability**: No CLS (Cumulative Layout Shift)
- **Accessibility**: WCAG 2.1 AA compliance maintained
- **Mobile Experience**: Responsive in both languages

---

## 🚀 Next Steps (Immediate)

### Session 395 Preparation (Phase 1 Start)

**Priority**: Dashboard + Settings Hub
**Estimated**: 2 hours
**Target**: Complete Phase 1 kickoff

**Pre-Session Checklist**:
- [x] Phase 4 (Test Pages) completed - Session 394 ✅
- [ ] Verify backend on port 8002 running
- [ ] Verify frontend on port 3001 running
- [ ] Verify language switching working
- [ ] Review SESSION_382_I18N_IMPLEMENTATION.md patterns
- [ ] Prepare dashboard page for i18n refactoring

**During Session**:
1. Read dashboard page (`/dashboard`)
2. Identify all user-facing strings
3. Create translation keys (~40 keys)
4. Update pl.json + en.json
5. Test Polish language
6. Test English language
7. Verify functionality preserved

**Session Completion Criteria**:
- ✅ Dashboard fully translated
- ✅ Settings hub fully translated
- ✅ ~65 new translation keys added
- ✅ Both languages verified working
- ✅ No console errors or warnings
- ✅ Layout stable in both languages

---

## 📚 References

**Key Documents**:
1. **SESSION_382_I18N_IMPLEMENTATION.md** - Current progress and patterns
2. **PROJECT_STATUS_REPORT.md** - Overall project status
3. **frontend/src/i18n.ts** - next-intl configuration
4. **frontend/middleware.ts** - Locale detection middleware
5. **frontend/messages/pl.json** - Polish translations
6. **frontend/messages/en.json** - English translations

**External Resources**:
- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [Next.js App Router i18n](https://nextjs.org/docs/app/building-your-application/routing/internationalization)
- [ICU Message Format](https://unicode-org.github.io/icu/userguide/format_parse/messages/)

---

**Last Updated**: 2026-02-02 (Session 417 - Authentication pages completed)
**Status**: 🔄 IN PROGRESS (53% complete, 28/53 pages)
**Next Session**: Session 418 - Core Detail Pages (3 pages: root, companies/[id], reports/[id])
**Target Completion**: Week 24 (Late February 2026)
