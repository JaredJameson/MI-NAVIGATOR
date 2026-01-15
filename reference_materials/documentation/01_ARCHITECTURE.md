# 01. Architektura Systemu

## 1. Przegląd Architektury

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Chat     │  │  Research   │  │   Reports   │  │  Dashboard  │        │
│  │  Interface  │  │    View     │  │   Studio    │  │   & Alerts  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                              WebSocket / REST
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────┐
│                              API GATEWAY                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Authentication │ Rate Limiting │ Request Routing │ Session Mgmt   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                │
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │   CONVERSATION   │───▶│      ROUTER      │───▶│   ORCHESTRATOR   │      │
│  │      AGENT       │    │                  │    │                  │      │
│  │                  │    │  • Classify      │    │  • Plan          │      │
│  │  • Chat flow     │    │  • Route         │    │  • Coordinate    │      │
│  │  • Context mgmt  │    │  • Estimate time │    │  • Aggregate     │      │
│  │  • User intent   │    │  • Set depth     │    │  • Verify        │      │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘      │
│                                                           │                 │
└───────────────────────────────────────────────────────────┼─────────────────┘
                                                            │
                    ┌───────────────────────────────────────┼───────────────┐
                    │                                       │               │
┌───────────────────┼───────────────────┐  ┌───────────────┼───────────────┼───┐
│         AGENT LAYER - COLLECTORS      │  │      AGENT LAYER - ANALYZERS  │   │
│                                       │  │                               │   │
│  ┌─────────────┐  ┌─────────────┐    │  │  ┌─────────────┐  ┌──────────┐│   │
│  │   Company   │  │   Market    │    │  │  │    Fact     │  │ Insight  ││   │
│  │   Intel     │  │   Intel     │    │  │  │   Checker   │  │Generator ││   │
│  │   Agents    │  │   Agents    │    │  │  │             │  │          ││   │
│  └─────────────┘  └─────────────┘    │  │  └─────────────┘  └──────────┘│   │
│                                       │  │                               │   │
│  ┌─────────────┐  ┌─────────────┐    │  │  ┌─────────────┐  ┌──────────┐│   │
│  │ Competitive │  │   Website   │    │  │  │  Framework  │  │  Report  ││   │
│  │   Intel     │  │   Crawler   │    │  │  │  Applier    │  │ Composer ││   │
│  │   Agents    │  │   Agent     │    │  │  │             │  │          ││   │
│  └─────────────┘  └─────────────┘    │  │  └─────────────┘  └──────────┘│   │
└───────────────────────────────────────┘  └───────────────────────────────────┘
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        │
┌───────────────────────────────────────┼─────────────────────────────────────┐
│                              TOOLS LAYER                                     │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │   Web    │ │   Deep   │ │   File   │ │   KRS    │ │  Social  │          │
│  │  Search  │ │  Crawler │ │ Processor│ │   API    │ │ Analyzer │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ LinkedIn │ │ Similar  │ │ BuiltWith│ │ News API │ │ Financial│          │
│  │   API    │ │   Web    │ │   API    │ │          │ │   APIs   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
┌───────────────────────────────────────┼─────────────────────────────────────┐
│                              DATA LAYER                                      │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   VECTOR STORE   │  │   GRAPH DATABASE │  │   SQL DATABASE   │          │
│  │                  │  │                  │  │                  │          │
│  │  • Documents     │  │  • Company       │  │  • User data     │          │
│  │  • Reports       │  │    relations     │  │  • Projects      │          │
│  │  • Industry KB   │  │  • Ownership     │  │  • Reports       │          │
│  │  • Embeddings    │  │  • Competitors   │  │  • Financials    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                                 │
│  │      CACHE       │  │   FILE STORAGE   │                                 │
│  │                  │  │                  │                                 │
│  │  • API responses │  │  • Uploaded docs │                                 │
│  │  • Search cache  │  │  • Generated     │                                 │
│  │  • Session data  │  │    reports       │                                 │
│  └──────────────────┘  └──────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Struktura Katalogów

```
market-intelligence-platform/
│
├── 📁 frontend/                          # React/Next.js Application
│   ├── 📁 app/                           # Next.js App Router
│   │   ├── page.tsx                      # Landing/Dashboard
│   │   ├── chat/page.tsx                 # Main Chat Interface
│   │   ├── research/page.tsx             # Research Projects
│   │   ├── reports/page.tsx              # Reports Library
│   │   └── settings/page.tsx             # User Settings
│   │
│   ├── 📁 components/
│   │   ├── 📁 chat/
│   │   │   ├── ChatWindow.tsx            # Main chat container
│   │   │   ├── MessageList.tsx           # Messages display
│   │   │   ├── MessageBubble.tsx         # Single message
│   │   │   ├── InputArea.tsx             # Text input + actions
│   │   │   ├── FileUploader.tsx          # Drag & drop upload
│   │   │   ├── URLInput.tsx              # URL analysis input
│   │   │   ├── AgentStatus.tsx           # Agent working indicator
│   │   │   ├── SourcesDrawer.tsx         # Expand sources panel
│   │   │   └── SuggestedActions.tsx      # Quick action chips
│   │   │
│   │   ├── 📁 research/
│   │   │   ├── BriefBuilder.tsx          # Step-by-step brief
│   │   │   ├── LiveResearchView.tsx      # Real-time progress
│   │   │   ├── AgentPipeline.tsx         # Visual agent flow
│   │   │   ├── CheckpointCard.tsx        # Human-in-the-loop
│   │   │   └── SourcesPanel.tsx          # Collected sources
│   │   │
│   │   ├── 📁 reports/
│   │   │   ├── ReportViewer.tsx          # Interactive report
│   │   │   ├── ReportEditor.tsx          # Edit with AI assist
│   │   │   ├── ExportDialog.tsx          # Export options
│   │   │   ├── CitationList.tsx          # Source citations
│   │   │   └── ChartComponents.tsx       # Data visualizations
│   │   │
│   │   └── 📁 dashboard/
│   │       ├── ProjectCard.tsx           # Project summary
│   │       ├── AlertsFeed.tsx            # Competition alerts
│   │       ├── QuickSearch.tsx           # Fast lookup
│   │       └── RecentActivity.tsx        # Activity timeline
│   │
│   ├── 📁 hooks/
│   │   ├── useChat.ts                    # Chat state management
│   │   ├── useResearch.ts                # Research session
│   │   ├── useWebSocket.ts               # Real-time connection
│   │   └── useFileUpload.ts              # File handling
│   │
│   └── 📁 lib/
│       ├── api.ts                        # API client
│       ├── websocket.ts                  # WS connection
│       └── formatters.ts                 # Data formatting
│
├── 📁 backend/                           # Python FastAPI
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app
│   │   ├── routes/
│   │   │   ├── chat.py                   # Chat endpoints
│   │   │   ├── research.py               # Research endpoints
│   │   │   ├── reports.py                # Reports endpoints
│   │   │   ├── files.py                  # File upload/process
│   │   │   └── webhooks.py               # External webhooks
│   │   └── websocket/
│   │       ├── handler.py                # WS connection handler
│   │       └── events.py                 # Event types
│   │
│   ├── 📁 agents/
│   │   ├── 📁 core/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py             # Abstract base agent
│   │   │   ├── orchestrator.py           # Main coordinator
│   │   │   ├── router.py                 # Task classifier
│   │   │   └── conversation.py           # Chat agent
│   │   │
│   │   ├── 📁 collectors/
│   │   │   ├── __init__.py
│   │   │   ├── company_profile.py        # Company data
│   │   │   ├── financial_data.py         # Financial info
│   │   │   ├── ownership_mapping.py      # Ownership structure
│   │   │   ├── digital_footprint.py      # Online presence
│   │   │   ├── news_collector.py         # News & mentions
│   │   │   ├── market_data.py            # Market statistics
│   │   │   └── competitor_data.py        # Competitor info
│   │   │
│   │   ├── 📁 analyzers/
│   │   │   ├── __init__.py
│   │   │   ├── fact_checker.py           # Verify & cross-ref
│   │   │   ├── insight_generator.py      # Extract insights
│   │   │   ├── framework_applier.py      # Apply frameworks
│   │   │   └── report_composer.py        # Generate reports
│   │   │
│   │   └── 📁 specialized/
│   │       ├── __init__.py
│   │       ├── website_analyzer.py       # Deep site analysis
│   │       └── relationship_mapper.py    # Connection graphs
│   │
│   ├── 📁 tools/
│   │   ├── __init__.py
│   │   ├── web_search.py                 # SerpAPI wrapper
│   │   ├── deep_crawler.py               # Website crawler
│   │   ├── pdf_extractor.py              # PDF processing
│   │   ├── docx_processor.py             # DOCX processing
│   │   ├── image_analyzer.py             # Image/OCR
│   │   ├── krs_api.py                    # KRS integration
│   │   ├── linkedin_scraper.py           # LinkedIn data
│   │   ├── similarweb_api.py             # Traffic data
│   │   ├── builtwith_api.py              # Tech stack
│   │   └── news_api.py                   # News aggregation
│   │
│   ├── 📁 data/
│   │   ├── __init__.py
│   │   ├── vector_store.py               # Pinecone/Qdrant
│   │   ├── graph_db.py                   # Neo4j
│   │   ├── sql_db.py                     # PostgreSQL
│   │   ├── cache.py                      # Redis
│   │   └── file_storage.py               # S3/MinIO
│   │
│   └── 📁 services/
│       ├── __init__.py
│       ├── llm_service.py                # LLM API calls
│       ├── embedding_service.py          # Text embeddings
│       └── export_service.py             # Report export
│
├── 📁 knowledge_base/                    # Agent Knowledge
│   ├── 📁 system_prompts/                # Level 1 prompts
│   ├── 📁 agent_prompts/                 # Level 2 prompts
│   ├── 📁 frameworks/                    # Strategic frameworks
│   ├── 📁 templates/                     # Output templates
│   ├── 📁 industry/                      # Domain knowledge
│   └── 📁 examples/                      # Few-shot examples
│
├── 📁 config/
│   ├── agents.yaml                       # Agent configurations
│   ├── routing.yaml                      # Routing rules
│   ├── sources.yaml                      # Data source config
│   └── prompts.yaml                      # Prompt registry
│
├── 📁 tests/
│   ├── 📁 unit/
│   ├── 📁 integration/
│   └── 📁 e2e/
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 3. Przepływ Danych

### 3.1 Chat Message Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER SENDS MESSAGE                               │
│  "Przeanalizuj firmę FADO z Bydgoszczy - konkurenci, finanse, strategie" │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      1. CONVERSATION AGENT                               │
│  • Parse user intent                                                     │
│  • Extract entities: company="FADO", location="Bydgoszcz"               │
│  • Identify scope: competitors, financials, strategy                     │
│  • Confirm understanding (if ambiguous)                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           2. ROUTER                                      │
│  Classification:                                                         │
│  {                                                                       │
│    "route": "competitive_analysis",                                      │
│    "depth": "comprehensive",                                             │
│    "estimated_time": "8-12min",                                          │
│    "required_chains": ["company_profile", "competitor_mapping",          │
│                        "financial_analysis", "strategic_frameworks"]     │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        3. ORCHESTRATOR                                   │
│  Execution Plan:                                                         │
│                                                                          │
│  Phase 1 (Parallel):                                                     │
│    ├── company_profile_agent(FADO)                                       │
│    ├── financial_agent(FADO)                                             │
│    └── digital_footprint_agent(FADO)                                     │
│                                                                          │
│  Phase 2 (After Phase 1):                                                │
│    └── competitor_mapping_agent(industry=plastics, region=PL)            │
│                                                                          │
│  Phase 3 (Parallel for each competitor):                                 │
│    ├── company_profile_agent(competitor_1)                               │
│    ├── company_profile_agent(competitor_2)                               │
│    └── ...                                                               │
│                                                                          │
│  Phase 4 (Synthesis):                                                    │
│    ├── fact_checker(all_data)                                            │
│    ├── framework_applier(SWOT, Porter)                                   │
│    └── insight_generator(verified_data)                                  │
│                                                                          │
│  Phase 5 (Output):                                                       │
│    └── report_composer(insights, format=comprehensive)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    4. AGENT EXECUTION                                    │
│                                                                          │
│  [WS Event] → "Pobieram dane rejestrowe FADO..."                        │
│  [WS Event] → "Analizuję sprawozdania finansowe..."                     │
│  [WS Event] → "Identyfikuję konkurentów w branży..."                    │
│  [WS Event] → "Zbieram dane o 5 konkurentach..."                        │
│  [WS Event] → "Weryfikuję zebrane informacje..."                        │
│  [WS Event] → "Generuję analizę SWOT..."                                │
│  [WS Event] → "Przygotowuję raport końcowy..."                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      5. RESPONSE TO USER                                 │
│                                                                          │
│  Structured Response:                                                    │
│  ├── Executive Summary (key findings)                                    │
│  ├── Company Profile (FADO details)                                      │
│  ├── Financial Analysis (revenue, growth)                                │
│  ├── Competitive Landscape (5 competitors + matrix)                      │
│  ├── SWOT Analysis                                                       │
│  ├── Strategic Recommendations                                           │
│  ├── Sources & Confidence Levels                                         │
│  └── Suggested Follow-ups                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 File Upload Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User drops  │────▶│   Frontend   │────▶│   Backend    │
│    file      │     │  validates   │     │   /upload    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                     ┌───────────────────────────┼───────────────────────────┐
                     │                           ▼                           │
              ┌──────┴──────┐            ┌──────────────┐            ┌──────┴──────┐
              │    PDF      │            │    DOCX      │            │    CSV      │
              │  Extractor  │            │  Processor   │            │   Parser    │
              └──────┬──────┘            └──────┬───────┘            └──────┬──────┘
                     │                          │                           │
                     └──────────────────────────┼───────────────────────────┘
                                                │
                                                ▼
                                    ┌──────────────────────┐
                                    │   Content Analyzer   │
                                    │                      │
                                    │  • Extract entities  │
                                    │  • Identify type     │
                                    │  • Summarize content │
                                    │  • Suggest actions   │
                                    └──────────────────────┘
                                                │
                                                ▼
                                    ┌──────────────────────┐
                                    │   Store in Context   │
                                    │                      │
                                    │  • Vector embeddings │
                                    │  • Session context   │
                                    │  • Available for     │
                                    │    agent queries     │
                                    └──────────────────────┘
```

### 3.3 URL Analysis Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER PROVIDES URL                              │
│  "Przeanalizuj stronę: https://example-company.pl"               │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DEEP CRAWLER AGENT                             │
│                                                                   │
│  Level 1: Homepage Analysis                                       │
│  ├── Extract: title, meta, main content                          │
│  ├── Identify: navigation structure                              │
│  └── Detect: technology stack (BuiltWith)                        │
│                                                                   │
│  Level 2: Key Pages Crawl                                        │
│  ├── /about, /o-nas → Company info                               │
│  ├── /products, /services → Offerings                            │
│  ├── /team, /zespol → Key people                                 │
│  ├── /contact → Locations, details                               │
│  ├── /blog, /news → Recent activity                              │
│  └── /careers → Growth indicators                                │
│                                                                   │
│  Level 3: External Links                                         │
│  ├── Social media profiles                                       │
│  ├── Partner/client logos                                        │
│  └── Certifications, awards                                      │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                  WEBSITE INTELLIGENCE AGENT                       │
│                                                                   │
│  Extracted Data:                                                  │
│  {                                                                │
│    "company_name": "...",                                         │
│    "tagline": "...",                                              │
│    "products_services": [...],                                    │
│    "team_members": [...],                                         │
│    "locations": [...],                                            │
│    "social_links": {...},                                         │
│    "tech_stack": [...],                                           │
│    "content_freshness": "2024-01",                                │
│    "traffic_estimate": "~10k/month",                              │
│    "seo_keywords": [...]                                          │
│  }                                                                │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ENRICHMENT & CROSS-REF                         │
│                                                                   │
│  • Match with KRS data (verify legal entity)                     │
│  • Pull SimilarWeb traffic data                                  │
│  • Check social media followers/engagement                       │
│  • Search news mentions                                          │
│  • Identify competitors (similar businesses)                     │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                    STRUCTURED OUTPUT                              │
│                                                                   │
│  Website Analysis Report:                                         │
│  ├── Company Overview (from website)                             │
│  ├── Products/Services Catalog                                   │
│  ├── Digital Presence Score                                      │
│  ├── Competitive Position                                        │
│  ├── Key Findings & Red Flags                                    │
│  └── Recommended Deep Dives                                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Komponenty Techniczne

### 4.1 Tech Stack

| Warstwa | Technologia | Uzasadnienie |
|---------|-------------|--------------|
| Frontend | Next.js 14 + TypeScript | SSR, App Router, streaming |
| UI Components | shadcn/ui + Tailwind | Elastyczność, profesjonalny wygląd |
| Real-time | WebSocket (Socket.io) | Live updates z agentów |
| Backend | FastAPI (Python) | Async, typing, OpenAPI |
| LLM | Claude API (Sonnet 4.5) | Niezawodność, tool use |
| Vector DB | Qdrant | Self-hosted, dobra wydajność |
| Graph DB | Neo4j | Relacje firmowe |
| SQL DB | PostgreSQL | Dane użytkowników, projekty |
| Cache | Redis | Sesje, cache API |
| Queue | Celery + Redis | Background tasks |
| Storage | MinIO (S3-compatible) | Pliki, raporty |

### 4.2 Integracje Zewnętrzne

```yaml
data_sources:
  company_data:
    - name: KRS API
      type: government
      rate_limit: 100/day
      data: legal_entity, ownership, financials
      
    - name: CEIDG API
      type: government
      data: sole_proprietors
      
    - name: Rejestr.io
      type: commercial
      data: enriched_company_data
      
  web_intelligence:
    - name: SerpAPI
      type: commercial
      rate_limit: 1000/month
      data: search_results, news
      
    - name: SimilarWeb API
      type: commercial
      data: traffic, competitors
      
    - name: BuiltWith API
      type: commercial
      data: technology_stack
      
  social_data:
    - name: LinkedIn (unofficial)
      type: scraping
      data: employees, company_info
      risk: rate_limiting
      
    - name: Social Media APIs
      type: official
      data: followers, engagement
      
  financial_data:
    - name: InfoVeriti
      type: commercial
      data: financial_reports
      
    - name: Bisnode/Dun&Bradstreet
      type: commercial
      data: credit_ratings, risk
```

---

## 5. Bezpieczeństwo i Skalowalność

### 5.1 Security

```yaml
security:
  authentication:
    - JWT tokens
    - OAuth2 (Google, Microsoft)
    - API keys for integrations
    
  authorization:
    - Role-based access (user, admin, enterprise)
    - Project-level permissions
    - Rate limiting per user tier
    
  data_protection:
    - Encryption at rest (AES-256)
    - Encryption in transit (TLS 1.3)
    - PII handling (GDPR compliance)
    - Audit logging
    
  api_security:
    - Input validation
    - SQL injection prevention
    - XSS protection
    - CORS configuration
```

### 5.2 Scalability

```yaml
scalability:
  horizontal:
    - Stateless API servers
    - Load balancer (nginx)
    - Auto-scaling on demand
    
  vertical:
    - Agent worker pools
    - Parallel execution
    - Async processing
    
  caching:
    - API response cache (1h)
    - Search results cache (24h)
    - Company data cache (7d)
    
  queuing:
    - Long-running research jobs
    - Priority queues (quick vs deep)
    - Retry with exponential backoff
```

---

## 6. Metryki i Monitoring

```yaml
observability:
  metrics:
    - Request latency (p50, p95, p99)
    - Agent execution time
    - LLM token usage
    - Cache hit ratio
    - Error rates by type
    
  logging:
    - Structured JSON logs
    - Request tracing (correlation IDs)
    - Agent decision logging
    
  alerting:
    - Error rate spikes
    - API rate limit warnings
    - Long-running jobs
    - LLM cost thresholds
```

---

*Następny dokument: 02_KNOWLEDGE_BASE_STRUCTURE.md*
