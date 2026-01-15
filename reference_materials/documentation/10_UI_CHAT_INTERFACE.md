# 10. UI Chat Interface

## Przegląd

Szczegółowy projekt interfejsu konwersacyjnego platformy Market Intelligence:
1. **Chat Window** - główne okno rozmowy
2. **Input Area** - wprowadzanie tekstu, upload, URL
3. **Agent Status** - wizualizacja pracy agentów
4. **Sources Panel** - źródła i cytowania
5. **Actions & Suggestions** - szybkie akcje

---

## 1. ARCHITEKTURA INTERFEJSU

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HEADER BAR                                      │
│  ┌─────────┐  ┌──────────────────────────────────┐  ┌─────────────────────┐ │
│  │  Logo   │  │     Research: "Analiza FADO"     │  │  User │ Settings   │ │
│  └─────────┘  └──────────────────────────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────┐  ┌───────────────────────────┐ │
│  │                                         │  │      SOURCES PANEL        │ │
│  │              CHAT AREA                  │  │                           │ │
│  │                                         │  │  ┌─────────────────────┐  │ │
│  │  ┌─────────────────────────────────┐   │  │  │ Source 1: KRS       │  │ │
│  │  │  User: Przeanalizuj firmę FADO  │   │  │  │ Confidence: 95%     │  │ │
│  │  └─────────────────────────────────┘   │  │  └─────────────────────┘  │ │
│  │                                         │  │                           │ │
│  │  ┌─────────────────────────────────┐   │  │  ┌─────────────────────┐  │ │
│  │  │  Agent: Rozumiem. Zaczynam...   │   │  │  │ Source 2: Website   │  │ │
│  │  │  [Agent Status Component]        │   │  │  │ fado.pl             │  │ │
│  │  │  ───────────────────────────     │   │  │  └─────────────────────┘  │ │
│  │  │  📊 Pobieram dane z KRS...       │   │  │                           │ │
│  │  │  [████████░░░░░░░░] 45%          │   │  │  ┌─────────────────────┐  │ │
│  │  └─────────────────────────────────┘   │  │  │ Source 3: LinkedIn  │  │ │
│  │                                         │  │  └─────────────────────┘  │ │
│  │  ┌─────────────────────────────────┐   │  │                           │ │
│  │  │  [STRUCTURED REPORT CARD]        │   │  │  ┌─────────────────────┐  │ │
│  │  │  Company Profile: FADO           │   │  │  │ 📎 Uploaded Files   │  │ │
│  │  │  ├── Overview                    │   │  │  │ • raport.pdf        │  │ │
│  │  │  ├── Financials                  │   │  │  │ • dane.xlsx         │  │ │
│  │  │  └── Competition                 │   │  │  └─────────────────────┘  │ │
│  │  └─────────────────────────────────┘   │  │                           │ │
│  │                                         │  └───────────────────────────┘ │
│  │  ┌─────────────────────────────────┐   │                                 │
│  │  │  SUGGESTED ACTIONS               │   │                                 │
│  │  │  [🔍 Konkurenci] [📈 Finanse]   │   │                                 │
│  │  │  [📊 SWOT] [🌐 Eksport]          │   │                                 │
│  │  └─────────────────────────────────┘   │                                 │
│  └─────────────────────────────────────────┘                                 │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                              INPUT AREA                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ 📎  🔗  │  Zadaj pytanie o firmę, rynek lub wklej URL do analizy...  │➤││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. KOMPONENTY SZCZEGÓŁOWO

### 2.1 ChatWindow Component

```typescript
// components/chat/ChatWindow.tsx

interface ChatWindowProps {
  sessionId: string;
  initialMessages?: Message[];
  onNewResearch?: (research: Research) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string | StructuredContent;
  timestamp: Date;
  metadata?: MessageMetadata;
}

interface MessageMetadata {
  agentType?: string;
  sources?: Source[];
  confidence?: number;
  processingTime?: number;
  tokens?: number;
}

interface StructuredContent {
  type: 'text' | 'report' | 'chart' | 'table' | 'card' | 'status';
  data: any;
}

// Stan komponentu
interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentAgent: AgentStatus | null;
  sources: Source[];
  uploadedFiles: UploadedFile[];
  suggestions: Suggestion[];
}
```

### 2.2 Message Types & Rendering

```typescript
// Typy wiadomości i ich renderowanie

// 1. TEXT MESSAGE (prosty tekst)
{
  type: 'text',
  content: 'Analizuję firmę FADO z Bydgoszczy...'
}

// 2. REPORT CARD (rozwijane sekcje)
{
  type: 'report',
  data: {
    title: 'Profil Firmy: FADO Sp. z o.o.',
    sections: [
      {
        id: 'overview',
        title: 'Przegląd',
        icon: '🏢',
        expanded: true,
        content: {...}
      },
      {
        id: 'financials',
        title: 'Dane Finansowe',
        icon: '📊',
        expanded: false,
        content: {...}
      },
      {
        id: 'ownership',
        title: 'Struktura Właścicielska',
        icon: '👥',
        expanded: false,
        content: {...}
      }
    ],
    actions: ['export_pdf', 'export_docx', 'continue_analysis']
  }
}

// 3. COMPARISON TABLE
{
  type: 'table',
  data: {
    title: 'Porównanie Konkurentów',
    columns: ['Firma', 'Przychody', 'Pracownicy', 'Market Share'],
    rows: [
      ['FADO', '45M PLN', '150', '18%'],
      ['Konkurent A', '62M PLN', '200', '24%'],
      ['Konkurent B', '38M PLN', '120', '14%']
    ],
    sortable: true,
    exportable: true
  }
}

// 4. CHART
{
  type: 'chart',
  data: {
    chartType: 'bar' | 'line' | 'pie' | 'radar',
    title: 'Przychody 2020-2024',
    data: {...},
    interactive: true
  }
}

// 5. STATUS UPDATE (podczas pracy agenta)
{
  type: 'status',
  data: {
    phase: 'data_collection',
    agent: 'company_profile',
    status: 'running',
    message: 'Pobieram dane rejestrowe z KRS...',
    progress: 45,
    subTasks: [
      { name: 'KRS lookup', status: 'completed' },
      { name: 'Website crawl', status: 'running' },
      { name: 'LinkedIn search', status: 'pending' }
    ]
  }
}

// 6. FRAMEWORK CARD (SWOT, Porter, etc.)
{
  type: 'framework',
  data: {
    frameworkType: 'swot',
    company: 'FADO',
    content: {
      strengths: [...],
      weaknesses: [...],
      opportunities: [...],
      threats: [...]
    },
    visualization: 'quadrant' | 'list',
    editable: true
  }
}

// 7. SOURCE CITATION
{
  type: 'citation',
  data: {
    text: 'Przychody firmy wyniosły 45M PLN w 2023 roku',
    source: {
      name: 'e-KRS Sprawozdanie Finansowe',
      url: 'https://ekrs.ms.gov.pl/...',
      date: '2024-06-15',
      confidence: 0.95
    }
  }
}
```

### 2.3 MessageBubble Component

```typescript
// components/chat/MessageBubble.tsx

interface MessageBubbleProps {
  message: Message;
  isLatest: boolean;
  onAction: (action: string, data?: any) => void;
  onExpandSection: (sectionId: string) => void;
}

// Renderowanie w zależności od typu
const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onAction }) => {
  // User messages - prosta bańka po prawej
  if (message.role === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-2 max-w-[70%]">
          {message.content}
          {message.attachments && <AttachmentPreview files={message.attachments} />}
        </div>
      </div>
    );
  }
  
  // Assistant messages - po lewej z avatar
  return (
    <div className="flex gap-3 mb-4">
      <AgentAvatar agent={message.metadata?.agentType} />
      <div className="flex-1 max-w-[80%]">
        {renderContent(message.content, onAction)}
        {message.metadata?.sources && (
          <SourcesIndicator sources={message.metadata.sources} />
        )}
      </div>
    </div>
  );
};

// Renderowanie różnych typów contentu
function renderContent(content: string | StructuredContent, onAction: Function) {
  if (typeof content === 'string') {
    return <TextContent text={content} />;
  }
  
  switch (content.type) {
    case 'report':
      return <ReportCard data={content.data} onAction={onAction} />;
    case 'table':
      return <DataTable data={content.data} />;
    case 'chart':
      return <InteractiveChart data={content.data} />;
    case 'status':
      return <AgentStatusCard data={content.data} />;
    case 'framework':
      return <FrameworkVisualization data={content.data} />;
    default:
      return <TextContent text={JSON.stringify(content)} />;
  }
}
```

---

## 3. INPUT AREA - Szczegółowy Design

### 3.1 Struktura Inputu

```typescript
// components/chat/InputArea.tsx

interface InputAreaProps {
  onSendMessage: (message: UserInput) => void;
  onFileUpload: (files: File[]) => void;
  onUrlSubmit: (url: string) => void;
  isDisabled: boolean;
  placeholder?: string;
}

interface UserInput {
  text: string;
  attachments?: File[];
  urls?: string[];
  context?: {
    selectedCompany?: string;
    selectedFramework?: string;
  };
}

const InputArea: React.FC<InputAreaProps> = (props) => {
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isUrlMode, setIsUrlMode] = useState(false);
  const [showCommands, setShowCommands] = useState(false);
  
  return (
    <div className="border-t bg-white p-4">
      {/* Attachment Preview */}
      {attachments.length > 0 && (
        <AttachmentPreviewBar 
          files={attachments} 
          onRemove={(index) => removeAttachment(index)} 
        />
      )}
      
      {/* URL Preview (jeśli wykryto URL) */}
      {detectedUrls.length > 0 && (
        <UrlPreviewBar urls={detectedUrls} />
      )}
      
      {/* Main Input */}
      <div className="flex items-end gap-2">
        {/* Action Buttons */}
        <div className="flex gap-1">
          <FileUploadButton onUpload={handleFileUpload} />
          <UrlInputButton onClick={() => setIsUrlMode(!isUrlMode)} />
          <CommandPaletteButton onClick={() => setShowCommands(true)} />
        </div>
        
        {/* Text Input */}
        <div className="flex-1 relative">
          <AutoResizeTextarea
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder={getPlaceholder()}
            maxRows={6}
          />
          
          {/* Slash Commands Dropdown */}
          {showCommands && (
            <CommandPalette 
              commands={availableCommands}
              onSelect={handleCommandSelect}
              onClose={() => setShowCommands(false)}
            />
          )}
        </div>
        
        {/* Send Button */}
        <SendButton 
          onClick={handleSend}
          disabled={!canSend()}
          isLoading={props.isDisabled}
        />
      </div>
      
      {/* Quick Actions */}
      <QuickActionsBar actions={contextualActions} onAction={handleQuickAction} />
    </div>
  );
};
```

### 3.2 File Upload Flow

```typescript
// components/chat/FileUploader.tsx

interface FileUploaderProps {
  onUpload: (files: ProcessedFile[]) => void;
  acceptedTypes: string[];
  maxSize: number; // MB
}

interface ProcessedFile {
  id: string;
  name: string;
  type: FileType;
  size: number;
  preview?: string; // thumbnail or first page
  extractedContent?: ExtractedContent;
  status: 'uploading' | 'processing' | 'ready' | 'error';
}

interface ExtractedContent {
  text?: string;
  tables?: any[];
  entities?: ExtractedEntity[];
  summary?: string;
}

// Obsługiwane typy plików
const SUPPORTED_FILE_TYPES = {
  pdf: {
    mimeTypes: ['application/pdf'],
    maxSize: 50, // MB
    processor: 'pdf_extractor',
    icon: '📄'
  },
  docx: {
    mimeTypes: ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    maxSize: 20,
    processor: 'docx_processor',
    icon: '📝'
  },
  xlsx: {
    mimeTypes: ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
    maxSize: 20,
    processor: 'xlsx_processor',
    icon: '📊'
  },
  csv: {
    mimeTypes: ['text/csv'],
    maxSize: 10,
    processor: 'csv_parser',
    icon: '📋'
  },
  image: {
    mimeTypes: ['image/png', 'image/jpeg', 'image/webp'],
    maxSize: 10,
    processor: 'image_analyzer',
    icon: '🖼️'
  }
};

// Upload Flow
const handleFileUpload = async (files: File[]) => {
  for (const file of files) {
    // 1. Walidacja
    const validation = validateFile(file);
    if (!validation.valid) {
      showError(validation.error);
      continue;
    }
    
    // 2. Upload do serwera
    const uploadedFile = await uploadToServer(file);
    
    // 3. Processing na backendzie
    const processedFile = await processFile(uploadedFile);
    
    // 4. Dodaj do kontekstu
    addToContext(processedFile);
    
    // 5. Wyświetl preview i sugestie
    showFilePreview(processedFile);
    suggestActions(processedFile);
  }
};

// Komponent Drag & Drop
const DragDropZone: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  
  return (
    <div
      className={`
        border-2 border-dashed rounded-lg p-8 text-center transition-colors
        ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
      <p className="mt-2 text-sm text-gray-600">
        Przeciągnij pliki lub <span className="text-blue-600 cursor-pointer">wybierz z dysku</span>
      </p>
      <p className="text-xs text-gray-500 mt-1">
        PDF, DOCX, XLSX, CSV, PNG, JPG do 50MB
      </p>
    </div>
  );
};
```

### 3.3 URL Analysis Flow

```typescript
// components/chat/URLAnalyzer.tsx

interface URLAnalyzerProps {
  onAnalyze: (result: URLAnalysisResult) => void;
}

interface URLAnalysisResult {
  url: string;
  status: 'analyzing' | 'complete' | 'error';
  websiteInfo?: WebsiteInfo;
  suggestedActions?: string[];
}

interface WebsiteInfo {
  domain: string;
  title: string;
  description: string;
  type: 'company' | 'product' | 'news' | 'other';
  extractedData: {
    companyName?: string;
    industry?: string;
    products?: string[];
    contacts?: Contact[];
    socialLinks?: SocialLink[];
  };
  techStack?: string[];
  screenshot?: string;
}

// URL Input Component
const URLInput: React.FC<URLAnalyzerProps> = ({ onAnalyze }) => {
  const [url, setUrl] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [preview, setPreview] = useState<URLPreview | null>(null);
  
  // Auto-detect URLs w tekście
  useEffect(() => {
    const detected = detectURL(url);
    setIsValid(detected.valid);
    if (detected.valid) {
      fetchPreview(detected.url);
    }
  }, [url]);
  
  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <GlobeIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Wklej URL strony do analizy..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          {isValid && <CheckIcon className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500" />}
        </div>
        <button
          onClick={() => onAnalyze({ url, status: 'analyzing' })}
          disabled={!isValid}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
        >
          Analizuj
        </button>
      </div>
      
      {/* URL Preview Card */}
      {preview && (
        <URLPreviewCard preview={preview} />
      )}
    </div>
  );
};

// URL Preview Card
const URLPreviewCard: React.FC<{ preview: URLPreview }> = ({ preview }) => (
  <div className="flex gap-3 p-3 border rounded-lg bg-gray-50">
    {preview.favicon && (
      <img src={preview.favicon} alt="" className="w-8 h-8 rounded" />
    )}
    <div className="flex-1 min-w-0">
      <h4 className="font-medium text-sm truncate">{preview.title}</h4>
      <p className="text-xs text-gray-500 truncate">{preview.url}</p>
      <p className="text-xs text-gray-600 mt-1 line-clamp-2">{preview.description}</p>
    </div>
  </div>
);
```

---

## 4. AGENT STATUS VISUALIZATION

### 4.1 Agent Status Component

```typescript
// components/chat/AgentStatus.tsx

interface AgentStatusProps {
  status: AgentExecutionStatus;
  onCancel?: () => void;
  onPause?: () => void;
}

interface AgentExecutionStatus {
  sessionId: string;
  phase: string;
  currentAgent: string;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  progress: number;
  message: string;
  tasks: AgentTask[];
  startTime: Date;
  estimatedCompletion?: Date;
  checkpoint?: Checkpoint;
}

interface AgentTask {
  id: string;
  name: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'skipped';
  startTime?: Date;
  endTime?: Date;
  result?: any;
  error?: string;
}

interface Checkpoint {
  type: 'confirmation' | 'selection' | 'input';
  message: string;
  options?: CheckpointOption[];
  timeout?: number;
  defaultAction?: string;
}

// Główny komponent statusu
const AgentStatus: React.FC<AgentStatusProps> = ({ status, onCancel, onPause }) => {
  return (
    <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AgentAvatar agent={status.currentAgent} animated={status.status === 'running'} />
          <div>
            <span className="font-medium text-sm">{getAgentDisplayName(status.currentAgent)}</span>
            <span className="text-xs text-slate-500 ml-2">{status.phase}</span>
          </div>
        </div>
        <div className="flex gap-2">
          {status.status === 'running' && (
            <>
              <button onClick={onPause} className="text-xs text-slate-600 hover:text-slate-800">
                ⏸️ Pauza
              </button>
              <button onClick={onCancel} className="text-xs text-red-600 hover:text-red-800">
                ✕ Anuluj
              </button>
            </>
          )}
        </div>
      </div>
      
      {/* Current Message */}
      <div className="flex items-center gap-2 mb-3">
        {status.status === 'running' && <Spinner size="sm" />}
        <p className="text-sm text-slate-700">{status.message}</p>
      </div>
      
      {/* Progress Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Postęp</span>
          <span>{status.progress}%</span>
        </div>
        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 rounded-full transition-all duration-300"
            style={{ width: `${status.progress}%` }}
          />
        </div>
      </div>
      
      {/* Task List */}
      <div className="space-y-1">
        {status.tasks.map((task) => (
          <TaskItem key={task.id} task={task} />
        ))}
      </div>
      
      {/* Checkpoint (jeśli aktywny) */}
      {status.checkpoint && (
        <CheckpointCard checkpoint={status.checkpoint} />
      )}
      
      {/* Estimated Time */}
      {status.estimatedCompletion && (
        <div className="mt-3 text-xs text-slate-500 text-right">
          Szacowany czas: {formatTimeRemaining(status.estimatedCompletion)}
        </div>
      )}
    </div>
  );
};

// Task Item
const TaskItem: React.FC<{ task: AgentTask }> = ({ task }) => {
  const statusIcons = {
    pending: '⏳',
    running: '🔄',
    completed: '✅',
    error: '❌',
    skipped: '⏭️'
  };
  
  return (
    <div className="flex items-center gap-2 text-sm">
      <span>{statusIcons[task.status]}</span>
      <span className={task.status === 'running' ? 'text-blue-600 font-medium' : 'text-slate-600'}>
        {task.name}
      </span>
      {task.status === 'completed' && task.endTime && task.startTime && (
        <span className="text-xs text-slate-400">
          ({formatDuration(task.endTime - task.startTime)})
        </span>
      )}
    </div>
  );
};

// Checkpoint Card - Human-in-the-loop
const CheckpointCard: React.FC<{ checkpoint: Checkpoint }> = ({ checkpoint }) => {
  return (
    <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <div className="flex items-start gap-2">
        <span className="text-amber-600">⚠️</span>
        <div className="flex-1">
          <p className="text-sm font-medium text-amber-800">{checkpoint.message}</p>
          
          {checkpoint.options && (
            <div className="mt-2 flex flex-wrap gap-2">
              {checkpoint.options.map((option) => (
                <button
                  key={option.id}
                  onClick={() => handleCheckpointAction(option.action)}
                  className={`
                    px-3 py-1 text-sm rounded-lg border
                    ${option.isDefault 
                      ? 'bg-amber-600 text-white border-amber-600' 
                      : 'bg-white text-amber-700 border-amber-300 hover:bg-amber-50'}
                  `}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
          
          {checkpoint.timeout && (
            <p className="mt-2 text-xs text-amber-600">
              Auto-wybór za {checkpoint.timeout}s: {checkpoint.defaultAction}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
```

### 4.2 Pipeline Visualization

```typescript
// components/chat/AgentPipeline.tsx

interface AgentPipelineProps {
  plan: ExecutionPlan;
  currentPhase: number;
}

const AgentPipeline: React.FC<AgentPipelineProps> = ({ plan, currentPhase }) => {
  return (
    <div className="bg-slate-900 text-white p-4 rounded-xl">
      <h4 className="text-sm font-medium mb-4">Plan Wykonania</h4>
      
      <div className="space-y-4">
        {plan.phases.map((phase, index) => (
          <PhaseVisualization
            key={phase.id}
            phase={phase}
            isActive={index === currentPhase}
            isCompleted={index < currentPhase}
            isPending={index > currentPhase}
          />
        ))}
      </div>
    </div>
  );
};

const PhaseVisualization: React.FC<PhaseProps> = ({ phase, isActive, isCompleted, isPending }) => {
  return (
    <div className={`flex items-start gap-3 ${isPending ? 'opacity-50' : ''}`}>
      {/* Status Icon */}
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center text-sm
        ${isCompleted ? 'bg-green-500' : isActive ? 'bg-blue-500 animate-pulse' : 'bg-slate-700'}
      `}>
        {isCompleted ? '✓' : isActive ? '►' : phase.index}
      </div>
      
      {/* Phase Details */}
      <div className="flex-1">
        <div className="font-medium text-sm">{phase.name}</div>
        
        {/* Agents in Phase */}
        <div className="mt-1 flex flex-wrap gap-1">
          {phase.agents.map((agent) => (
            <span
              key={agent.id}
              className={`
                text-xs px-2 py-0.5 rounded
                ${agent.status === 'completed' ? 'bg-green-600' :
                  agent.status === 'running' ? 'bg-blue-600' : 'bg-slate-700'}
              `}
            >
              {agent.name}
            </span>
          ))}
        </div>
        
        {/* Execution Type */}
        <div className="mt-1 text-xs text-slate-400">
          {phase.execution === 'parallel' ? '⚡ Równolegle' : '➡️ Sekwencyjnie'}
        </div>
      </div>
    </div>
  );
};
```

---

## 5. SOURCES PANEL

### 5.1 Sources Panel Component

```typescript
// components/chat/SourcesPanel.tsx

interface SourcesPanelProps {
  sources: Source[];
  uploadedFiles: UploadedFile[];
  onSourceClick: (source: Source) => void;
  isCollapsed: boolean;
  onToggle: () => void;
}

interface Source {
  id: string;
  type: 'krs' | 'website' | 'linkedin' | 'news' | 'report' | 'user_file';
  name: string;
  url?: string;
  date?: Date;
  confidence: number; // 0-1
  usedInSections: string[];
  preview?: string;
}

const SourcesPanel: React.FC<SourcesPanelProps> = ({ sources, uploadedFiles, onSourceClick }) => {
  const [filter, setFilter] = useState<string>('all');
  
  const filteredSources = sources.filter(s => filter === 'all' || s.type === filter);
  
  return (
    <div className="h-full flex flex-col bg-slate-50 border-l">
      {/* Header */}
      <div className="p-3 border-b bg-white">
        <h3 className="font-semibold text-sm">Źródła ({sources.length})</h3>
        
        {/* Filter Tabs */}
        <div className="flex gap-1 mt-2 overflow-x-auto">
          {['all', 'krs', 'website', 'news', 'user_file'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`
                px-2 py-1 text-xs rounded whitespace-nowrap
                ${filter === type ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:bg-slate-100'}
              `}
            >
              {getFilterLabel(type)}
            </button>
          ))}
        </div>
      </div>
      
      {/* Sources List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {filteredSources.map((source) => (
          <SourceCard key={source.id} source={source} onClick={onSourceClick} />
        ))}
      </div>
      
      {/* Uploaded Files Section */}
      {uploadedFiles.length > 0 && (
        <div className="p-3 border-t bg-white">
          <h4 className="text-xs font-medium text-slate-500 mb-2">📎 Twoje pliki</h4>
          <div className="space-y-1">
            {uploadedFiles.map((file) => (
              <UploadedFileItem key={file.id} file={file} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Source Card
const SourceCard: React.FC<{ source: Source; onClick: (s: Source) => void }> = ({ source, onClick }) => {
  const typeIcons = {
    krs: '🏛️',
    website: '🌐',
    linkedin: '💼',
    news: '📰',
    report: '📊',
    user_file: '📎'
  };
  
  return (
    <div
      onClick={() => onClick(source)}
      className="p-2 bg-white rounded-lg border border-slate-200 hover:border-blue-300 cursor-pointer transition-colors"
    >
      <div className="flex items-start gap-2">
        <span className="text-lg">{typeIcons[source.type]}</span>
        <div className="flex-1 min-w-0">
          <h5 className="text-sm font-medium truncate">{source.name}</h5>
          {source.url && (
            <p className="text-xs text-slate-500 truncate">{new URL(source.url).hostname}</p>
          )}
          {source.preview && (
            <p className="text-xs text-slate-600 mt-1 line-clamp-2">{source.preview}</p>
          )}
        </div>
        <ConfidenceBadge confidence={source.confidence} />
      </div>
      
      {/* Used In Sections */}
      {source.usedInSections.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {source.usedInSections.map((section) => (
            <span key={section} className="text-xs px-1 py-0.5 bg-slate-100 rounded text-slate-600">
              {section}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

// Confidence Badge
const ConfidenceBadge: React.FC<{ confidence: number }> = ({ confidence }) => {
  const color = confidence > 0.8 ? 'green' : confidence > 0.5 ? 'yellow' : 'red';
  
  return (
    <span className={`
      text-xs px-1.5 py-0.5 rounded-full
      ${color === 'green' ? 'bg-green-100 text-green-700' :
        color === 'yellow' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}
    `}>
      {Math.round(confidence * 100)}%
    </span>
  );
};
```

---

## 6. SUGGESTED ACTIONS & QUICK COMMANDS

### 6.1 Suggestions Component

```typescript
// components/chat/SuggestedActions.tsx

interface SuggestedActionsProps {
  suggestions: Suggestion[];
  context: ConversationContext;
  onSelect: (suggestion: Suggestion) => void;
}

interface Suggestion {
  id: string;
  type: 'follow_up' | 'deep_dive' | 'framework' | 'export' | 'compare';
  label: string;
  icon: string;
  prompt: string;
  priority: number;
}

const SuggestedActions: React.FC<SuggestedActionsProps> = ({ suggestions, onSelect }) => {
  // Sortuj po priorytecie
  const sortedSuggestions = [...suggestions].sort((a, b) => b.priority - a.priority);
  
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {sortedSuggestions.slice(0, 6).map((suggestion) => (
        <button
          key={suggestion.id}
          onClick={() => onSelect(suggestion)}
          className="
            flex items-center gap-1 px-3 py-1.5 
            bg-white border border-slate-200 rounded-full
            text-sm text-slate-700 
            hover:bg-slate-50 hover:border-blue-300
            transition-colors
          "
        >
          <span>{suggestion.icon}</span>
          <span>{suggestion.label}</span>
        </button>
      ))}
    </div>
  );
};

// Kontekstowe sugestie generowane przez system
const generateSuggestions = (context: ConversationContext): Suggestion[] => {
  const suggestions: Suggestion[] = [];
  
  // Jeśli mamy profil firmy - sugeruj dalsze analizy
  if (context.hasCompanyProfile) {
    suggestions.push(
      { id: 's1', type: 'deep_dive', label: 'Analiza konkurencji', icon: '🎯', prompt: 'Znajdź i porównaj głównych konkurentów', priority: 90 },
      { id: 's2', type: 'framework', label: 'Analiza SWOT', icon: '📊', prompt: 'Przygotuj analizę SWOT', priority: 85 },
      { id: 's3', type: 'deep_dive', label: 'Dane finansowe', icon: '💰', prompt: 'Pokaż szczegółowe dane finansowe', priority: 80 },
      { id: 's4', type: 'deep_dive', label: 'Struktura właścicielska', icon: '👥', prompt: 'Kto jest właścicielem firmy?', priority: 75 }
    );
  }
  
  // Jeśli analizowaliśmy konkurencję
  if (context.hasCompetitors) {
    suggestions.push(
      { id: 's5', type: 'framework', label: 'Porter Five Forces', icon: '🔄', prompt: 'Przeprowadź analizę Porter Five Forces', priority: 85 },
      { id: 's6', type: 'compare', label: 'Tabela porównawcza', icon: '📋', prompt: 'Stwórz tabelę porównawczą konkurentów', priority: 80 },
      { id: 's7', type: 'export', label: 'Eksport do PDF', icon: '📄', prompt: 'Eksportuj raport do PDF', priority: 70 }
    );
  }
  
  // Jeśli jest framework
  if (context.currentFramework) {
    suggestions.push(
      { id: 's8', type: 'export', label: 'Eksport do PowerPoint', icon: '📊', prompt: 'Eksportuj do prezentacji', priority: 75 },
      { id: 's9', type: 'deep_dive', label: 'Rozwiń szczegóły', icon: '🔍', prompt: 'Rozwiń analizę o dodatkowe szczegóły', priority: 65 }
    );
  }
  
  return suggestions;
};
```

### 6.2 Command Palette (Slash Commands)

```typescript
// components/chat/CommandPalette.tsx

interface CommandPaletteProps {
  isOpen: boolean;
  commands: Command[];
  onSelect: (command: Command) => void;
  onClose: () => void;
  filter: string;
}

interface Command {
  id: string;
  name: string;
  description: string;
  shortcut: string; // np. "/profil"
  category: 'analysis' | 'framework' | 'export' | 'settings';
  action: string;
  icon: string;
}

const AVAILABLE_COMMANDS: Command[] = [
  // Analysis
  { id: 'c1', name: 'Profil firmy', description: 'Pełny profil firmy z danymi rejestrowymi', shortcut: '/profil', category: 'analysis', action: 'company_profile', icon: '🏢' },
  { id: 'c2', name: 'Analiza finansowa', description: 'Szczegółowa analiza finansowa', shortcut: '/finanse', category: 'analysis', action: 'financial_analysis', icon: '💰' },
  { id: 'c3', name: 'Analiza konkurencji', description: 'Znajdź i porównaj konkurentów', shortcut: '/konkurencja', category: 'analysis', action: 'competitive_analysis', icon: '🎯' },
  { id: 'c4', name: 'Analiza rynku', description: 'Wielkość rynku, trendy, segmentacja', shortcut: '/rynek', category: 'analysis', action: 'market_analysis', icon: '📈' },
  { id: 'c5', name: 'Analiza strony', description: 'Głęboka analiza strony internetowej', shortcut: '/strona', category: 'analysis', action: 'website_analysis', icon: '🌐' },
  
  // Frameworks
  { id: 'c6', name: 'SWOT', description: 'Analiza SWOT firmy', shortcut: '/swot', category: 'framework', action: 'swot', icon: '📊' },
  { id: 'c7', name: 'Porter', description: 'Analiza Five Forces', shortcut: '/porter', category: 'framework', action: 'porter', icon: '🔄' },
  { id: 'c8', name: 'PESTLE', description: 'Analiza makrootoczenia', shortcut: '/pestle', category: 'framework', action: 'pestle', icon: '🌍' },
  { id: 'c9', name: 'BCG Matrix', description: 'Analiza portfolio produktowego', shortcut: '/bcg', category: 'framework', action: 'bcg', icon: '⭐' },
  
  // Export
  { id: 'c10', name: 'Eksport PDF', description: 'Eksportuj raport do PDF', shortcut: '/pdf', category: 'export', action: 'export_pdf', icon: '📄' },
  { id: 'c11', name: 'Eksport PowerPoint', description: 'Eksportuj do prezentacji', shortcut: '/pptx', category: 'export', action: 'export_pptx', icon: '📊' },
  { id: 'c12', name: 'Eksport Word', description: 'Eksportuj do dokumentu Word', shortcut: '/docx', category: 'export', action: 'export_docx', icon: '📝' }
];

const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, commands, onSelect, onClose, filter }) => {
  const filteredCommands = commands.filter(cmd => 
    cmd.name.toLowerCase().includes(filter.toLowerCase()) ||
    cmd.shortcut.includes(filter.toLowerCase())
  );
  
  const groupedCommands = groupBy(filteredCommands, 'category');
  
  if (!isOpen) return null;
  
  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-xl border max-h-80 overflow-y-auto">
      {Object.entries(groupedCommands).map(([category, cmds]) => (
        <div key={category}>
          <div className="px-3 py-2 text-xs font-medium text-slate-500 uppercase bg-slate-50">
            {getCategoryLabel(category)}
          </div>
          {cmds.map((cmd) => (
            <button
              key={cmd.id}
              onClick={() => onSelect(cmd)}
              className="w-full px-3 py-2 flex items-center gap-3 hover:bg-slate-50 text-left"
            >
              <span className="text-xl">{cmd.icon}</span>
              <div className="flex-1">
                <div className="font-medium text-sm">{cmd.name}</div>
                <div className="text-xs text-slate-500">{cmd.description}</div>
              </div>
              <span className="text-xs text-slate-400 font-mono">{cmd.shortcut}</span>
            </button>
          ))}
        </div>
      ))}
    </div>
  );
};
```

---

## 7. WEBSOCKET INTEGRATION

```typescript
// hooks/useChat.ts

interface UseChatReturn {
  messages: Message[];
  isConnected: boolean;
  isLoading: boolean;
  agentStatus: AgentStatus | null;
  sources: Source[];
  suggestions: Suggestion[];
  sendMessage: (input: UserInput) => void;
  uploadFile: (file: File) => Promise<ProcessedFile>;
  cancelExecution: () => void;
  respondToCheckpoint: (response: any) => void;
}

const useChat = (sessionId: string): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const ws = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    // Połącz WebSocket
    ws.current = new WebSocket(`wss://api.example.com/chat/${sessionId}`);
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    return () => ws.current?.close();
  }, [sessionId]);
  
  const handleWebSocketMessage = (data: WebSocketMessage) => {
    switch (data.type) {
      case 'message':
        // Nowa wiadomość od agenta
        setMessages(prev => [...prev, data.message]);
        break;
        
      case 'status_update':
        // Update statusu agenta
        setAgentStatus(data.status);
        break;
        
      case 'source_added':
        // Nowe źródło znalezione
        setSources(prev => [...prev, data.source]);
        break;
        
      case 'checkpoint':
        // Human-in-the-loop checkpoint
        setAgentStatus(prev => ({ ...prev, checkpoint: data.checkpoint }));
        break;
        
      case 'completed':
        // Wykonanie zakończone
        setAgentStatus(null);
        setSuggestions(generateSuggestions(data.context));
        break;
        
      case 'error':
        // Błąd
        setMessages(prev => [...prev, createErrorMessage(data.error)]);
        setAgentStatus(null);
        break;
    }
  };
  
  const sendMessage = (input: UserInput) => {
    // Dodaj wiadomość użytkownika
    const userMessage = createUserMessage(input);
    setMessages(prev => [...prev, userMessage]);
    
    // Wyślij przez WebSocket
    ws.current?.send(JSON.stringify({
      type: 'user_message',
      content: input
    }));
  };
  
  return {
    messages,
    isConnected: ws.current?.readyState === WebSocket.OPEN,
    isLoading: agentStatus?.status === 'running',
    agentStatus,
    sources,
    suggestions,
    sendMessage,
    uploadFile,
    cancelExecution,
    respondToCheckpoint
  };
};
```

---

*Następny dokument: 11_UI_DASHBOARD_REPORTS.md*
