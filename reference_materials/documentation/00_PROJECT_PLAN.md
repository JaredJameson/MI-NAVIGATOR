# Market Intelligence Platform - Plan Projektu

## ✅ Status: KOMPLETNY (18/18 dokumentów)

**Data aktualizacji:** 2025-01-15

---

## 📋 Mapa Dokumentacji

### Etap 1: Fundamenty ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 01 | `01_ARCHITECTURE.md` | Struktura projektu, komponenty, przepływ danych | ✅ |
| 02 | `02_KNOWLEDGE_BASE_STRUCTURE.md` | Organizacja bazy wiedzy dla agentów | ✅ |

### Etap 2: System Promptów (Wielopoziomowy) ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 03 | `03_PROMPTS_L1_SYSTEM.md` | Level 1: Orchestrator, Router, Conversation | ✅ |
| 04 | `04_PROMPTS_L2_COMPANY.md` | Level 2: Agenci analizy firmowej (6 agentów) | ✅ |
| 05 | `05_PROMPTS_L2_MARKET.md` | Level 2: Agenci analizy rynkowej (5 agentów) | ✅ |
| 06 | `06_PROMPTS_L2_COMPETITIVE.md` | Level 2: Agenci wywiadu konkurencyjnego (5 agentów) | ✅ |
| 07 | `07_PROMPTS_L3_SYNTHESIS.md` | Level 3: Weryfikacja, synteza, raporty (4 agenci) | ✅ |

### Etap 3: Frameworki Strategiczne ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 08 | `08_FRAMEWORKS_STRATEGIC.md` | SWOT, PESTLE, Porter, BCG, Ansoff | ✅ |
| 09 | `09_FRAMEWORKS_OPERATIONAL.md` | Value Chain, Business Model Canvas, Lean Canvas, JTBD | ✅ |

### Etap 4: Interfejs Użytkownika ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 10 | `10_UI_CHAT_INTERFACE.md` | Chat, upload, URL input, agent status, WebSocket | ✅ |
| 11 | `11_UI_DASHBOARD_REPORTS.md` | Dashboard, Reports Studio, Export, Sharing | ✅ |

### Etap 5: Narzędzia Deep Analysis ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 12 | `12_TOOLS_WEBSITE_ANALYSIS.md` | Deep Crawler, Tech Detector, Content Extractor | ✅ |
| 13 | `13_TOOLS_DATA_SOURCES.md` | KRS, CEIDG, LinkedIn, SimilarWeb, News, Financial | ✅ |
| 14 | `14_TOOLS_FILE_PROCESSING.md` | PDF, DOCX, XLSX/CSV, Image analysis | ✅ |

### Etap 6: Konfiguracja i Wdrożenie ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 15 | `15_CONFIG_ROUTING.yaml` | 6 routes, routing rules, rate limits | ✅ |
| 16 | `16_CONFIG_AGENTS.yaml` | 25+ agent configurations, dependencies | ✅ |
| 17 | `17_IMPLEMENTATION_ROADMAP.md` | Plan wdrożenia: MVP(3m) → Full(7m+) | ✅ |

### Etap 7: Dynamic Context System ✅
| # | Plik | Opis | Status |
|---|------|------|--------|
| 18 | `18_DYNAMIC_CONTEXT_SYSTEM.md` | Onboarding, Brief Collection, Industry KB, Dynamic Prompts | ✅ |

---

## 📊 Podsumowanie Zawartości

### Agenci (25+)
```
ORCHESTRATION (3)
├── Orchestrator - koordynacja pipeline'u
├── Router - klasyfikacja intencji
└── Conversation - dialog z użytkownikiem

COMPANY INTELLIGENCE (6)
├── Company Profile - dane rejestrowe KRS/CEIDG
├── Financial Analysis - sprawozdania, wskaźniki
├── Ownership Mapping - struktura właścicielska
├── Digital Presence - website, social, traffic
├── Key People - zarząd, menedżerowie
└── News & Sentiment - monitoring, sentyment

MARKET ANALYSIS (5)
├── Market Sizing - TAM/SAM/SOM
├── Trend Analysis - trendy technologiczne, rynkowe
├── Segmentation - segmenty, white spaces
├── Value Chain - łańcuch wartości branży
└── Regulatory - otoczenie regulacyjne

COMPETITIVE INTELLIGENCE (5)
├── Competitor Mapping - identyfikacja konkurentów
├── Benchmarking - porównanie wielowymiarowe
├── Share of Voice - widoczność vs konkurencja
├── Pricing Intelligence - strategie cenowe
└── Strategic Moves - ruchy strategiczne

SYNTHESIS (4)
├── Fact Checker - weryfikacja wieloźródłowa
├── Insight Generator - actionable insights
├── Framework Applier - aplikacja frameworków
└── Report Composer - kompilacja raportów
```

### Frameworki Strategiczne (9)
1. **SWOT Analysis** - mocne/słabe strony, szanse/zagrożenia
2. **PESTLE Analysis** - makrootoczenie 6-wymiarowe
3. **Porter's Five Forces** - siły konkurencyjne branży
4. **BCG Matrix** - portfolio produktowe
5. **Ansoff Matrix** - strategie wzrostu
6. **Value Chain** - łańcuch wartości Portera
7. **Business Model Canvas** - model biznesowy 9-blokowy
8. **Lean Canvas** - canvas dla startupów
9. **Jobs to Be Done** - analiza potrzeb klientów

### Routing Paths (6)
| Route | Czas | Opis |
|-------|------|------|
| Quick Lookup | ~30s | Proste pytania faktograficzne |
| Company Profile | ~2min | Pełny profil firmy |
| Market Analysis | ~5min | Analiza rynku i trendów |
| Competitive Analysis | ~10min | Deep dive konkurencja |
| Full Research Chain | ~30min | Kompleksowe badanie z checkpointami |
| Website Analysis | ~3-5min | Głęboka analiza strony www |

### Integracje Danych
```
POLISH REGISTRIES
├── KRS (API + rejestr.io)
├── CEIDG
└── CRBR (beneficjenci rzeczywiści)

COMPANY INTELLIGENCE
├── LinkedIn (via Proxycurl)
├── Glassdoor
└── Crunchbase

WEB INTELLIGENCE
├── SimilarWeb (traffic)
├── BuiltWith (tech stack)
└── Moz/Ahrefs (SEO)

NEWS & MEDIA
├── Google News (SerpAPI)
├── Polish portals (RSS)
└── Industry publications

FINANCIAL DATA
├── e-KRS (sprawozdania PDF)
├── EMIS
└── InfoVeriti
```

### Dynamic Context System (Dokument 18)
```
ONBOARDING FLOW
├── Industry Selection → zapisuje branżę użytkownika
├── Role Context → CEO/Sales/Analyst/etc.
├── Use Case Preferences → co najczęściej analizuje
└── Output Preferences → język, format, głębokość

BRIEF COLLECTION CHAT (przed każdym zadaniem)
├── Intent Analysis (Claude-based parsing)
├── 2-4 pytania doprecyzowujące (cel, geografia, głębokość)
├── Plan Generation (workflow preview)
└── User Confirmation/Modification

INDUSTRY KNOWLEDGE BASE
├── Taxonomy branż (plastics, tooling, IT, etc.)
├── Terminologia branżowa (PL/EN)
├── Kluczowe KPI per branża
├── Źródła danych per branża
└── PKD codes i wskaźniki konkurentów

DYNAMIC PROMPT COMPOSER
├── Base prompt agenta
├── + Industry-specific injection
├── + Task-specific instructions  
├── + User preferences
└── = Fully customized prompt

WORKFLOW CUSTOMIZER
├── Depth-based workflow (quick/standard/deep)
├── Industry-specific agents injection
├── Time budget fitting
└── Checkpoint generation for reviews
```

---

## 🎯 Architektura Promptów (3 poziomy)

```
┌─────────────────────────────────────────────────────────────┐
│ LEVEL 1: SYSTEM PROMPTS                                     │
│ Tożsamość agenta, podstawowe zachowania, dostępne narzędzia │
│ → 03_PROMPTS_L1_SYSTEM.md                                   │
├─────────────────────────────────────────────────────────────┤
│ LEVEL 2: TASK PROMPTS                                       │
│ Instrukcje dla konkretnych typów analiz i zadań             │
│ → 04, 05, 06 _PROMPTS_L2_*.md                               │
├─────────────────────────────────────────────────────────────┤
│ LEVEL 3: CONTEXT PROMPTS                                    │
│ Dynamiczne: brief użytkownika, zebrane dane, kontekst       │
│ → 07_PROMPTS_L3_SYNTHESIS.md + runtime                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Plan Implementacji

| Faza | Czas | Główne Deliverables |
|------|------|---------------------|
| **MVP** | 3 miesiące | Chat + Company Profile + Website Analysis + Export |
| **Enhanced** | 2 miesiące | Financial + Ownership + Competitive + SWOT + Dashboard |
| **Advanced** | 2 miesiące | Market Sizing + All Frameworks + News + Full Research |
| **Scale** | ongoing | Performance + Team features + API + Custom templates |

**Szczegóły:** `17_IMPLEMENTATION_ROADMAP.md`

---

## 📁 Struktura Plików

```
/home/claude/mi-platform/
├── 00_PROJECT_PLAN.md          # Ten dokument
├── 01_ARCHITECTURE.md          # 40KB - pełna architektura
├── 02_KNOWLEDGE_BASE_STRUCTURE.md  # 30KB - hierarchia promptów
├── 03_PROMPTS_L1_SYSTEM.md     # 8KB - orchestration agents
├── 04_PROMPTS_L2_COMPANY.md    # 18KB - 6 agentów firmowych
├── 05_PROMPTS_L2_MARKET.md     # 18KB - 5 agentów rynkowych
├── 06_PROMPTS_L2_COMPETITIVE.md # 21KB - 5 agentów konkurencyjnych
├── 07_PROMPTS_L3_SYNTHESIS.md  # 22KB - 4 agentów syntezy
├── 08_FRAMEWORKS_STRATEGIC.md  # 35KB - 5 frameworków strategicznych
├── 09_FRAMEWORKS_OPERATIONAL.md # 30KB - 4 frameworki operacyjne
├── 10_UI_CHAT_INTERFACE.md     # 25KB - komponenty czatu
├── 11_UI_DASHBOARD_REPORTS.md  # 20KB - dashboard i raporty
├── 12_TOOLS_WEBSITE_ANALYSIS.md # 25KB - crawler, tech detection
├── 13_TOOLS_DATA_SOURCES.md    # 30KB - wszystkie integracje API
├── 14_TOOLS_FILE_PROCESSING.md # 25KB - procesory plików
├── 15_CONFIG_ROUTING.yaml      # 10KB - konfiguracja routingu
├── 16_CONFIG_AGENTS.yaml       # 15KB - konfiguracja agentów
├── 17_IMPLEMENTATION_ROADMAP.md # 15KB - plan wdrożenia
└── 18_DYNAMIC_CONTEXT_SYSTEM.md # 35KB - onboarding, brief collection, industry KB

RAZEM: ~450KB szczegółowej dokumentacji PRD
```

---

## ✅ Następne Kroki

1. **Review** - przegląd dokumentacji pod kątem spójności
2. **Setup** - inicjalizacja projektu (Docker, repo, CI/CD)
3. **MVP Sprint 1** - Chat interface + Claude API
4. **MVP Sprint 2** - KRS integration + Company Profile Agent
5. **MVP Sprint 3** - Website Analysis + Router

---

*Dokumentacja kompletna. Gotowe do implementacji.*
