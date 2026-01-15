# MI-Navigator

**Market Intelligence Navigator** - Platforma do automatycznej analizy rynku i wywiadu biznesowego z wykorzystaniem AI.

## Przegląd

MI-Navigator to kompleksowa platforma Market Intelligence, która automatyzuje badania rynkowe poprzez:

- **Profil Firmy** - automatyczne pobieranie danych z KRS, CEIDG, CRBR
- **Analiza Finansowa** - ekstrakcja i analiza sprawozdań finansowych
- **Analiza Stron WWW** - deep crawling i ekstrakcja informacji
- **Mapowanie Konkurencji** - identyfikacja i benchmarking konkurentów
- **Analiza Rynku** - sizing rynku (TAM/SAM/SOM), trendy, segmentacja
- **Frameworki Strategiczne** - SWOT, Porter's Five Forces, PESTLE
- **Monitoring** - alerty i śledzenie zmian

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AI**: Claude API (Anthropic)
- **Vector DB**: Qdrant (semantic search)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS + shadcn/ui
- **State**: Zustand + React Query
- **Charts**: Recharts

## Szybki Start

### Wymagania
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- API key dla Claude (Anthropic)

### Instalacja

```bash
# Klonowanie repozytorium
git clone <repository-url>
cd MI-NAVIGATOR

# Uruchomienie setup script
./init.sh
```

### Uruchomienie

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Dostęp
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## Struktura Projektu

```
MI-NAVIGATOR/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── db/                # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── agents/            # AI agents
│   │   ├── prompts/           # LLM prompts
│   │   └── utils/             # Utilities
│   ├── tests/                 # Test suite
│   └── alembic/               # Database migrations
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   ├── services/          # API services
│   │   ├── stores/            # Zustand stores
│   │   └── types/             # TypeScript types
│   └── public/                # Static assets
│
├── reference_materials/        # Documentation & specs
│   └── documentation/         # Project documentation
│
├── docker-compose.yml         # Docker services
├── init.sh                    # Setup script
└── README.md                  # This file
```

## Architektura

### System Agentów AI

Platforma wykorzystuje hierarchiczny system agentów:

1. **L1 Agents** - Core agents (Orchestrator, Router, Conversation)
2. **L2 Agents** - Data acquisition agents (KRS, Website Crawler, News)
3. **L3 Agents** - Analysis agents (Financial, Competitive, Market)
4. **L4 Agents** - Synthesis agents (Fact Checker, Report Composer)

### Przepływ Danych

```
User Query → Router → Orchestrator → Agent Chain → Synthesis → Report
```

## Konfiguracja

### Backend (.env)
```env
ANTHROPIC_API_KEY=your-key
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testowanie

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Dokumentacja

Szczegółowa dokumentacja znajduje się w `reference_materials/documentation/`:

- `01_ARCHITECTURE.md` - Architektura systemu
- `02_KNOWLEDGE_BASE_STRUCTURE.md` - Struktura bazy wiedzy
- `03_PROMPTS_L1_SYSTEM.md` - System prompts
- `10_UI_CHAT_INTERFACE.md` - Interfejs czatu
- `11_UI_DASHBOARD_REPORTS.md` - Dashboard i raporty
- `17_IMPLEMENTATION_ROADMAP.md` - Plan implementacji

## Licencja

Proprietary - All rights reserved.

## Kontakt

Dla pytań i wsparcia skontaktuj się z zespołem development.
