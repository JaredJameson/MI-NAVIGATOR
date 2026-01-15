# 11. UI Dashboard & Reports

## Przegląd

Interfejsy zarządzania i raportowania:
1. **Dashboard** - przegląd projektów, alerty, metryki
2. **Reports Studio** - przeglądanie, edycja, eksport raportów
3. **Research Projects** - zarządzanie badaniami
4. **Export & Sharing** - formaty eksportu

---

## 1. DASHBOARD

### 1.1 Layout Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DASHBOARD                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  QUICK SEARCH                                                            ││
│  │  ┌──────────────────────────────────────────────────────────────────┐   ││
│  │  │ 🔍  Szukaj firmy, osoby lub wpisz URL...                        │   ││
│  │  └──────────────────────────────────────────────────────────────────┘   ││
│  │  Recent: FADO Sp. z o.o. • Splast S.A. • Rynek okien PL              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌───────────────────────────┐  ┌───────────────────────────────────────────┐│
│  │  ACTIVE RESEARCH          │  │  RECENT ACTIVITY                          ││
│  │                           │  │                                           ││
│  │  ┌─────────────────────┐  │  │  • 14:32 - Raport FADO zakończony       ││
│  │  │  🔄 Analiza FADO    │  │  │  • 12:15 - Nowy alert: Konkurent X       ││
│  │  │  Progress: 67%      │  │  │  • 11:45 - Upload: raport_q3.pdf         ││
│  │  │  Est: 5 min         │  │  │  • wczoraj - Analiza rynku okien         ││
│  │  └─────────────────────┘  │  │                                           ││
│  │                           │  │  [Zobacz wszystkie →]                     ││
│  │  [Start New Research]     │  │                                           ││
│  └───────────────────────────┘  └───────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  MY PROJECTS                                                    [+New]   ││
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       ││
│  │  │ 📁 Due Diligence │  │ 📁 Market Entry  │  │ 📁 Competitive   │       ││
│  │  │    ACME Corp     │  │    Germany       │  │    Watch         │       ││
│  │  │    ────────────  │  │    ────────────  │  │    ────────────  │       ││
│  │  │    5 reports     │  │    3 reports     │  │    12 alerts     │       ││
│  │  │    Updated: 2d   │  │    Updated: 1w   │  │    Active        │       ││
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌───────────────────────────────────┐  ┌───────────────────────────────────┐│
│  │  ALERTS & MONITORING              │  │  USAGE STATS                      ││
│  │                                   │  │                                   ││
│  │  🔴 Konkurent X: nowy produkt     │  │  Analyses this month: 42/100     ││
│  │  🟡 FADO: zmiana w zarządzie      │  │  ████████████░░░░ 42%            ││
│  │  🟢 Rynek +5% vs prognoza         │  │                                   ││
│  │                                   │  │  API calls: 8,432                 ││
│  │  [Manage Alerts →]                │  │  Storage: 2.4 GB / 10 GB          ││
│  └───────────────────────────────────┘  └───────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Dashboard Components

```typescript
// components/dashboard/Dashboard.tsx

interface DashboardProps {
  user: User;
  projects: Project[];
  alerts: Alert[];
  recentActivity: Activity[];
  activeResearch: Research | null;
  usageStats: UsageStats;
}

// Quick Search Component
const QuickSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const router = useRouter();
  
  const handleSearch = (q: string) => {
    // Detect jeśli to URL
    if (isURL(q)) {
      router.push(`/chat?url=${encodeURIComponent(q)}`);
      return;
    }
    
    // Detect jeśli to NIP/KRS
    if (isNIP(q) || isKRS(q)) {
      router.push(`/chat?company_id=${q}`);
      return;
    }
    
    // Standardowe wyszukiwanie
    router.push(`/chat?query=${encodeURIComponent(q)}`);
  };
  
  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white">
      <h2 className="text-xl font-semibold mb-4">Rozpocznij badanie</h2>
      
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          placeholder="Szukaj firmy, osoby, wklej URL do analizy..."
          className="w-full px-4 py-3 pl-12 rounded-lg text-gray-900 text-lg"
        />
        <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
        
        {/* Autocomplete Suggestions */}
        {suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-xl z-10">
            {suggestions.map((suggestion) => (
              <SuggestionItem key={suggestion.id} suggestion={suggestion} onClick={handleSearch} />
            ))}
          </div>
        )}
      </div>
      
      {/* Recent Searches */}
      <div className="mt-3 flex gap-2 flex-wrap">
        <span className="text-blue-200 text-sm">Ostatnie:</span>
        {recentSearches.map((search) => (
          <button
            key={search.id}
            onClick={() => handleSearch(search.query)}
            className="text-sm bg-white/20 hover:bg-white/30 px-2 py-1 rounded"
          >
            {search.label}
          </button>
        ))}
      </div>
    </div>
  );
};

// Project Card
const ProjectCard: React.FC<{ project: Project }> = ({ project }) => {
  return (
    <Link href={`/projects/${project.id}`}>
      <div className="bg-white border rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex items-start gap-3">
          <div className="text-2xl">{getProjectIcon(project.type)}</div>
          <div className="flex-1">
            <h3 className="font-semibold">{project.name}</h3>
            <p className="text-sm text-gray-500">{project.description}</p>
          </div>
        </div>
        
        <div className="mt-4 flex items-center justify-between text-sm">
          <div className="flex gap-4 text-gray-500">
            <span>📄 {project.reportsCount} raportów</span>
            <span>🔔 {project.alertsCount} alertów</span>
          </div>
          <span className="text-gray-400">
            Aktualizacja: {formatRelativeTime(project.updatedAt)}
          </span>
        </div>
        
        {/* Progress bar dla aktywnych badań */}
        {project.activeResearch && (
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>W toku: {project.activeResearch.name}</span>
              <span>{project.activeResearch.progress}%</span>
            </div>
            <div className="h-1.5 bg-gray-200 rounded-full">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{ width: `${project.activeResearch.progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </Link>
  );
};

// Alert Item
const AlertItem: React.FC<{ alert: Alert }> = ({ alert }) => {
  const severityColors = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200'
  };
  
  return (
    <div className={`p-3 rounded-lg border ${severityColors[alert.severity]}`}>
      <div className="flex items-start gap-2">
        <span>{alert.severity === 'high' ? '🔴' : alert.severity === 'medium' ? '🟡' : '🟢'}</span>
        <div className="flex-1">
          <p className="text-sm font-medium">{alert.title}</p>
          <p className="text-xs mt-1 opacity-80">{alert.description}</p>
        </div>
        <span className="text-xs opacity-60">{formatRelativeTime(alert.createdAt)}</span>
      </div>
    </div>
  );
};

// Usage Stats
const UsageStats: React.FC<{ stats: UsageStats }> = ({ stats }) => {
  return (
    <div className="bg-gray-50 rounded-xl p-4">
      <h3 className="font-semibold text-sm text-gray-700 mb-4">Wykorzystanie</h3>
      
      <div className="space-y-4">
        {/* Analyses */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Analizy w tym miesiącu</span>
            <span className="font-medium">{stats.analysesUsed}/{stats.analysesLimit}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full">
            <div
              className={`h-full rounded-full ${
                stats.analysesUsed / stats.analysesLimit > 0.8 ? 'bg-red-500' : 'bg-blue-500'
              }`}
              style={{ width: `${(stats.analysesUsed / stats.analysesLimit) * 100}%` }}
            />
          </div>
        </div>
        
        {/* Storage */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Przestrzeń dyskowa</span>
            <span className="font-medium">{formatBytes(stats.storageUsed)} / {formatBytes(stats.storageLimit)}</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full">
            <div
              className="h-full bg-green-500 rounded-full"
              style={{ width: `${(stats.storageUsed / stats.storageLimit) * 100}%` }}
            />
          </div>
        </div>
        
        {/* API Calls */}
        <div className="text-sm text-gray-600">
          <span>Wywołania API: </span>
          <span className="font-medium">{stats.apiCalls.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};
```

---

## 2. REPORTS STUDIO

### 2.1 Reports List View

```typescript
// components/reports/ReportsLibrary.tsx

interface Report {
  id: string;
  title: string;
  type: 'company_profile' | 'market_analysis' | 'competitive_analysis' | 'due_diligence' | 'custom';
  subject: string; // np. "FADO Sp. z o.o."
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'complete' | 'archived';
  sections: ReportSection[];
  sources: Source[];
  project?: Project;
  tags: string[];
  collaborators?: User[];
}

const ReportsLibrary: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [filter, setFilter] = useState<ReportFilter>({});
  const [sort, setSort] = useState<'date' | 'name' | 'type'>('date');
  
  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Raporty</h1>
        <div className="flex gap-3">
          <SearchInput value={filter.search} onChange={(v) => setFilter({ ...filter, search: v })} />
          <FilterDropdown filter={filter} onChange={setFilter} />
          <ViewToggle view={view} onChange={setView} />
        </div>
      </div>
      
      {/* Filters Bar */}
      <div className="flex gap-2 mb-4 overflow-x-auto">
        <FilterChip label="Wszystkie" active={!filter.type} onClick={() => setFilter({ ...filter, type: undefined })} />
        <FilterChip label="Profile firm" active={filter.type === 'company_profile'} onClick={() => setFilter({ ...filter, type: 'company_profile' })} />
        <FilterChip label="Analizy rynku" active={filter.type === 'market_analysis'} onClick={() => setFilter({ ...filter, type: 'market_analysis' })} />
        <FilterChip label="Konkurencja" active={filter.type === 'competitive_analysis'} onClick={() => setFilter({ ...filter, type: 'competitive_analysis' })} />
        <FilterChip label="Due Diligence" active={filter.type === 'due_diligence'} onClick={() => setFilter({ ...filter, type: 'due_diligence' })} />
      </div>
      
      {/* Reports Grid/List */}
      {view === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {reports.map((report) => (
            <ReportListItem key={report.id} report={report} />
          ))}
        </div>
      )}
    </div>
  );
};

// Report Card (Grid View)
const ReportCard: React.FC<{ report: Report }> = ({ report }) => {
  const typeIcons = {
    company_profile: '🏢',
    market_analysis: '📈',
    competitive_analysis: '🎯',
    due_diligence: '🔍',
    custom: '📄'
  };
  
  return (
    <Link href={`/reports/${report.id}`}>
      <div className="bg-white border rounded-xl p-4 hover:shadow-lg transition-shadow cursor-pointer">
        {/* Header */}
        <div className="flex items-start gap-3 mb-3">
          <span className="text-2xl">{typeIcons[report.type]}</span>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold truncate">{report.title}</h3>
            <p className="text-sm text-gray-500 truncate">{report.subject}</p>
          </div>
          <ReportStatusBadge status={report.status} />
        </div>
        
        {/* Preview */}
        <div className="bg-gray-50 rounded-lg p-3 mb-3">
          <p className="text-xs text-gray-600 line-clamp-3">
            {report.sections[0]?.preview || 'Brak podglądu'}
          </p>
        </div>
        
        {/* Meta */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex gap-2">
            <span>📊 {report.sections.length} sekcji</span>
            <span>📎 {report.sources.length} źródeł</span>
          </div>
          <span>{formatDate(report.updatedAt)}</span>
        </div>
        
        {/* Tags */}
        {report.tags.length > 0 && (
          <div className="mt-3 flex gap-1 flex-wrap">
            {report.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                {tag}
              </span>
            ))}
            {report.tags.length > 3 && (
              <span className="text-xs text-gray-400">+{report.tags.length - 3}</span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
};
```

### 2.2 Report Viewer

```typescript
// components/reports/ReportViewer.tsx

interface ReportViewerProps {
  report: Report;
  onEdit: () => void;
  onExport: (format: ExportFormat) => void;
  onShare: () => void;
}

const ReportViewer: React.FC<ReportViewerProps> = ({ report, onEdit, onExport, onShare }) => {
  const [activeSection, setActiveSection] = useState<string>(report.sections[0]?.id);
  const [showSources, setShowSources] = useState(false);
  
  return (
    <div className="flex h-screen">
      {/* Sidebar - Table of Contents */}
      <div className="w-64 bg-gray-50 border-r p-4 overflow-y-auto">
        <h2 className="font-bold text-lg mb-4">{report.title}</h2>
        <p className="text-sm text-gray-500 mb-4">{report.subject}</p>
        
        <nav className="space-y-1">
          {report.sections.map((section, index) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`
                w-full text-left px-3 py-2 rounded-lg text-sm
                ${activeSection === section.id 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'hover:bg-gray-100'}
              `}
            >
              <span className="text-gray-400 mr-2">{index + 1}.</span>
              {section.title}
            </button>
          ))}
        </nav>
        
        {/* Quick Stats */}
        <div className="mt-6 pt-4 border-t">
          <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Informacje</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Utworzono:</span>
              <span>{formatDate(report.createdAt)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Źródła:</span>
              <span>{report.sources.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Status:</span>
              <ReportStatusBadge status={report.status} />
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Toolbar */}
        <div className="sticky top-0 bg-white border-b px-6 py-3 flex items-center justify-between z-10">
          <div className="flex items-center gap-2">
            <button onClick={onEdit} className="btn-secondary">
              ✏️ Edytuj
            </button>
            <button onClick={() => setShowSources(!showSources)} className="btn-secondary">
              📎 Źródła ({report.sources.length})
            </button>
          </div>
          <div className="flex items-center gap-2">
            <ExportDropdown onExport={onExport} />
            <button onClick={onShare} className="btn-primary">
              🔗 Udostępnij
            </button>
          </div>
        </div>
        
        {/* Report Content */}
        <div className="p-6 max-w-4xl mx-auto">
          {report.sections.map((section) => (
            <ReportSection
              key={section.id}
              section={section}
              isActive={activeSection === section.id}
              sources={report.sources}
            />
          ))}
        </div>
      </div>
      
      {/* Sources Panel (slide-in) */}
      {showSources && (
        <div className="w-80 bg-white border-l overflow-y-auto">
          <SourcesPanel sources={report.sources} onClose={() => setShowSources(false)} />
        </div>
      )}
    </div>
  );
};

// Report Section Component
const ReportSection: React.FC<{ section: ReportSection; isActive: boolean; sources: Source[] }> = ({ 
  section, 
  isActive, 
  sources 
}) => {
  return (
    <section id={section.id} className={`mb-8 scroll-mt-20 ${isActive ? '' : ''}`}>
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        {section.icon && <span>{section.icon}</span>}
        {section.title}
      </h2>
      
      {/* Section content based on type */}
      {section.type === 'text' && (
        <div className="prose prose-lg max-w-none">
          <MarkdownRenderer content={section.content} />
        </div>
      )}
      
      {section.type === 'table' && (
        <DataTable data={section.content} />
      )}
      
      {section.type === 'chart' && (
        <InteractiveChart data={section.content} />
      )}
      
      {section.type === 'framework' && (
        <FrameworkVisualization 
          type={section.content.frameworkType}
          data={section.content.data}
        />
      )}
      
      {section.type === 'comparison' && (
        <ComparisonMatrix data={section.content} />
      )}
      
      {/* Section Sources */}
      {section.sourceIds && section.sourceIds.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-medium text-gray-500 mb-2">Źródła dla tej sekcji:</h4>
          <div className="flex flex-wrap gap-2">
            {section.sourceIds.map((sourceId) => {
              const source = sources.find(s => s.id === sourceId);
              return source ? (
                <SourceBadge key={sourceId} source={source} />
              ) : null;
            })}
          </div>
        </div>
      )}
    </section>
  );
};
```

### 2.3 Report Editor

```typescript
// components/reports/ReportEditor.tsx

interface ReportEditorProps {
  report: Report;
  onSave: (report: Report) => void;
  onCancel: () => void;
}

const ReportEditor: React.FC<ReportEditorProps> = ({ report, onSave, onCancel }) => {
  const [editedReport, setEditedReport] = useState<Report>(report);
  const [activeSectionId, setActiveSectionId] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  
  return (
    <div className="flex h-screen">
      {/* Sections List */}
      <div className="w-64 bg-gray-50 border-r p-4">
        <h3 className="font-semibold mb-4">Sekcje raportu</h3>
        
        <DragDropContext onDragEnd={handleSectionReorder}>
          <Droppable droppableId="sections">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {editedReport.sections.map((section, index) => (
                  <Draggable key={section.id} draggableId={section.id} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={`
                          p-2 mb-1 rounded cursor-pointer flex items-center gap-2
                          ${activeSectionId === section.id ? 'bg-blue-100' : 'hover:bg-gray-100'}
                        `}
                        onClick={() => setActiveSectionId(section.id)}
                      >
                        <span className="text-gray-400">⋮⋮</span>
                        <span className="flex-1 truncate text-sm">{section.title}</span>
                        <button 
                          onClick={(e) => { e.stopPropagation(); deleteSection(section.id); }}
                          className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100"
                        >
                          ×
                        </button>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
        
        <button
          onClick={addSection}
          className="w-full mt-4 p-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500"
        >
          + Dodaj sekcję
        </button>
      </div>
      
      {/* Editor Area */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="border-b px-4 py-2 flex items-center justify-between bg-white">
          <input
            type="text"
            value={editedReport.title}
            onChange={(e) => updateReport({ title: e.target.value })}
            className="text-xl font-bold border-none focus:ring-0 p-0"
            placeholder="Tytuł raportu"
          />
          <div className="flex gap-2">
            <button onClick={onCancel} className="btn-secondary">
              Anuluj
            </button>
            <button onClick={() => onSave(editedReport)} className="btn-primary" disabled={!isDirty}>
              💾 Zapisz
            </button>
          </div>
        </div>
        
        {/* Section Editor */}
        {activeSectionId ? (
          <SectionEditor
            section={editedReport.sections.find(s => s.id === activeSectionId)!}
            onChange={updateSection}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Wybierz sekcję do edycji lub dodaj nową
          </div>
        )}
      </div>
      
      {/* AI Assistant Panel */}
      <div className="w-80 border-l bg-gray-50 p-4">
        <h3 className="font-semibold mb-4">🤖 Asystent AI</h3>
        
        <div className="space-y-3">
          <button className="w-full text-left p-3 bg-white rounded-lg border hover:border-blue-500">
            <div className="font-medium text-sm">Rozwiń sekcję</div>
            <div className="text-xs text-gray-500">AI doda więcej szczegółów</div>
          </button>
          
          <button className="w-full text-left p-3 bg-white rounded-lg border hover:border-blue-500">
            <div className="font-medium text-sm">Przepisz na bardziej formalnie</div>
            <div className="text-xs text-gray-500">Zmień ton na biznesowy</div>
          </button>
          
          <button className="w-full text-left p-3 bg-white rounded-lg border hover:border-blue-500">
            <div className="font-medium text-sm">Dodaj wnioski</div>
            <div className="text-xs text-gray-500">AI wygeneruje podsumowanie</div>
          </button>
          
          <button className="w-full text-left p-3 bg-white rounded-lg border hover:border-blue-500">
            <div className="font-medium text-sm">Wzbogać danymi</div>
            <div className="text-xs text-gray-500">Dołącz aktualne dane rynkowe</div>
          </button>
        </div>
        
        {/* Custom AI Request */}
        <div className="mt-4">
          <textarea
            placeholder="Lub opisz co chcesz zmienić..."
            className="w-full p-3 border rounded-lg text-sm"
            rows={3}
          />
          <button className="w-full mt-2 btn-primary">
            Zastosuj AI
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

## 3. EXPORT & SHARING

### 3.1 Export Options

```typescript
// components/reports/ExportDialog.tsx

interface ExportDialogProps {
  report: Report;
  onExport: (format: ExportFormat, options: ExportOptions) => Promise<void>;
  onClose: () => void;
}

type ExportFormat = 'pdf' | 'docx' | 'pptx' | 'xlsx' | 'json' | 'html';

interface ExportOptions {
  includeSources: boolean;
  includeCharts: boolean;
  includeRawData: boolean;
  branding: 'none' | 'company' | 'custom';
  sections: string[]; // IDs sekcji do eksportu
  language: 'pl' | 'en';
}

const ExportDialog: React.FC<ExportDialogProps> = ({ report, onExport, onClose }) => {
  const [format, setFormat] = useState<ExportFormat>('pdf');
  const [options, setOptions] = useState<ExportOptions>({
    includeSources: true,
    includeCharts: true,
    includeRawData: false,
    branding: 'company',
    sections: report.sections.map(s => s.id),
    language: 'pl'
  });
  const [isExporting, setIsExporting] = useState(false);
  
  const formats: { id: ExportFormat; label: string; icon: string; description: string }[] = [
    { id: 'pdf', label: 'PDF', icon: '📄', description: 'Dokument PDF gotowy do druku' },
    { id: 'docx', label: 'Word', icon: '📝', description: 'Edytowalny dokument Word' },
    { id: 'pptx', label: 'PowerPoint', icon: '📊', description: 'Prezentacja z kluczowymi slajdami' },
    { id: 'xlsx', label: 'Excel', icon: '📈', description: 'Tabele i dane w arkuszu' },
    { id: 'json', label: 'JSON', icon: '{ }', description: 'Surowe dane w formacie JSON' },
    { id: 'html', label: 'HTML', icon: '🌐', description: 'Strona HTML do osadzenia' }
  ];
  
  const handleExport = async () => {
    setIsExporting(true);
    try {
      await onExport(format, options);
      onClose();
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };
  
  return (
    <Dialog open onClose={onClose}>
      <div className="p-6 max-w-xl">
        <h2 className="text-xl font-bold mb-4">Eksportuj raport</h2>
        
        {/* Format Selection */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Format</h3>
          <div className="grid grid-cols-3 gap-2">
            {formats.map((f) => (
              <button
                key={f.id}
                onClick={() => setFormat(f.id)}
                className={`
                  p-3 rounded-lg border text-left
                  ${format === f.id ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}
                `}
              >
                <div className="text-2xl mb-1">{f.icon}</div>
                <div className="font-medium text-sm">{f.label}</div>
                <div className="text-xs text-gray-500">{f.description}</div>
              </button>
            ))}
          </div>
        </div>
        
        {/* Sections Selection */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Sekcje do eksportu</h3>
          <div className="max-h-40 overflow-y-auto border rounded-lg p-2">
            {report.sections.map((section) => (
              <label key={section.id} className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded">
                <input
                  type="checkbox"
                  checked={options.sections.includes(section.id)}
                  onChange={(e) => {
                    const newSections = e.target.checked
                      ? [...options.sections, section.id]
                      : options.sections.filter(id => id !== section.id);
                    setOptions({ ...options, sections: newSections });
                  }}
                />
                <span className="text-sm">{section.title}</span>
              </label>
            ))}
          </div>
        </div>
        
        {/* Options */}
        <div className="mb-6 space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Opcje</h3>
          
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={options.includeSources}
              onChange={(e) => setOptions({ ...options, includeSources: e.target.checked })}
            />
            <span className="text-sm">Dołącz listę źródeł</span>
          </label>
          
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={options.includeCharts}
              onChange={(e) => setOptions({ ...options, includeCharts: e.target.checked })}
            />
            <span className="text-sm">Dołącz wykresy i wizualizacje</span>
          </label>
          
          {format === 'xlsx' && (
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={options.includeRawData}
                onChange={(e) => setOptions({ ...options, includeRawData: e.target.checked })}
              />
              <span className="text-sm">Dołącz surowe dane</span>
            </label>
          )}
        </div>
        
        {/* Branding */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Branding</h3>
          <select
            value={options.branding}
            onChange={(e) => setOptions({ ...options, branding: e.target.value as any })}
            className="w-full p-2 border rounded-lg"
          >
            <option value="none">Bez brandingu</option>
            <option value="company">Logo firmy</option>
            <option value="custom">Własne logo</option>
          </select>
        </div>
        
        {/* Actions */}
        <div className="flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">
            Anuluj
          </button>
          <button
            onClick={handleExport}
            disabled={isExporting || options.sections.length === 0}
            className="btn-primary"
          >
            {isExporting ? (
              <>
                <Spinner size="sm" /> Eksportuję...
              </>
            ) : (
              `Eksportuj do ${format.toUpperCase()}`
            )}
          </button>
        </div>
      </div>
    </Dialog>
  );
};
```

### 3.2 Share Dialog

```typescript
// components/reports/ShareDialog.tsx

interface ShareDialogProps {
  report: Report;
  onClose: () => void;
}

const ShareDialog: React.FC<ShareDialogProps> = ({ report, onClose }) => {
  const [shareMethod, setShareMethod] = useState<'link' | 'email' | 'embed'>('link');
  const [shareLink, setShareLink] = useState<string>('');
  const [linkSettings, setLinkSettings] = useState({
    requirePassword: false,
    password: '',
    expiresIn: '7d',
    allowDownload: true
  });
  
  const generateShareLink = async () => {
    const response = await api.post('/reports/share', {
      reportId: report.id,
      settings: linkSettings
    });
    setShareLink(response.data.shareUrl);
  };
  
  return (
    <Dialog open onClose={onClose}>
      <div className="p-6 max-w-md">
        <h2 className="text-xl font-bold mb-4">Udostępnij raport</h2>
        
        {/* Method Tabs */}
        <div className="flex border-b mb-4">
          {[
            { id: 'link', label: '🔗 Link' },
            { id: 'email', label: '📧 Email' },
            { id: 'embed', label: '< > Embed' }
          ].map((method) => (
            <button
              key={method.id}
              onClick={() => setShareMethod(method.id as any)}
              className={`
                px-4 py-2 border-b-2 font-medium text-sm
                ${shareMethod === method.id 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'}
              `}
            >
              {method.label}
            </button>
          ))}
        </div>
        
        {/* Link Sharing */}
        {shareMethod === 'link' && (
          <div className="space-y-4">
            {shareLink ? (
              <>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={shareLink}
                    readOnly
                    className="flex-1 p-2 border rounded-lg bg-gray-50"
                  />
                  <button
                    onClick={() => navigator.clipboard.writeText(shareLink)}
                    className="btn-secondary"
                  >
                    📋 Kopiuj
                  </button>
                </div>
                <p className="text-sm text-gray-500">
                  Link wygasa: {formatExpiration(linkSettings.expiresIn)}
                </p>
              </>
            ) : (
              <>
                <div className="space-y-3">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={linkSettings.requirePassword}
                      onChange={(e) => setLinkSettings({ ...linkSettings, requirePassword: e.target.checked })}
                    />
                    <span className="text-sm">Wymagaj hasła</span>
                  </label>
                  
                  {linkSettings.requirePassword && (
                    <input
                      type="password"
                      placeholder="Hasło dostępu"
                      value={linkSettings.password}
                      onChange={(e) => setLinkSettings({ ...linkSettings, password: e.target.value })}
                      className="w-full p-2 border rounded-lg"
                    />
                  )}
                  
                  <div>
                    <label className="text-sm text-gray-700">Wygasa po:</label>
                    <select
                      value={linkSettings.expiresIn}
                      onChange={(e) => setLinkSettings({ ...linkSettings, expiresIn: e.target.value })}
                      className="w-full p-2 border rounded-lg mt-1"
                    >
                      <option value="1d">1 dzień</option>
                      <option value="7d">7 dni</option>
                      <option value="30d">30 dni</option>
                      <option value="never">Nigdy</option>
                    </select>
                  </div>
                  
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={linkSettings.allowDownload}
                      onChange={(e) => setLinkSettings({ ...linkSettings, allowDownload: e.target.checked })}
                    />
                    <span className="text-sm">Pozwól na pobieranie</span>
                  </label>
                </div>
                
                <button onClick={generateShareLink} className="w-full btn-primary">
                  Wygeneruj link
                </button>
              </>
            )}
          </div>
        )}
        
        {/* Email Sharing */}
        {shareMethod === 'email' && (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-700">Odbiorcy (email)</label>
              <input
                type="text"
                placeholder="jan@firma.pl, anna@firma.pl"
                className="w-full p-2 border rounded-lg mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-gray-700">Wiadomość (opcjonalnie)</label>
              <textarea
                placeholder="Cześć, przesyłam raport do przeglądu..."
                className="w-full p-2 border rounded-lg mt-1"
                rows={3}
              />
            </div>
            <button className="w-full btn-primary">
              📧 Wyślij
            </button>
          </div>
        )}
        
        {/* Embed Code */}
        {shareMethod === 'embed' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Osadź raport na swojej stronie internetowej:
            </p>
            <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-xs overflow-x-auto">
              {`<iframe src="${window.location.origin}/embed/${report.id}" width="100%" height="600" frameborder="0"></iframe>`}
            </div>
            <button
              onClick={() => navigator.clipboard.writeText(`<iframe src="${window.location.origin}/embed/${report.id}" width="100%" height="600" frameborder="0"></iframe>`)}
              className="btn-secondary"
            >
              📋 Kopiuj kod
            </button>
          </div>
        )}
      </div>
    </Dialog>
  );
};
```

---

*Następny dokument: 12_TOOLS_WEBSITE_ANALYSIS.md*
