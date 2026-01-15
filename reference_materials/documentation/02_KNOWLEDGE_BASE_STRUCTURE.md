# 02. Struktura Bazy Wiedzy dla Agentów

## 1. Przegląd Knowledge Base

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE BASE ARCHITECTURE                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     PROMPT LIBRARY                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │   Level 1   │  │   Level 2   │  │   Level 3   │                 │   │
│  │  │   System    │  │    Task     │  │   Context   │                 │   │
│  │  │   Prompts   │  │   Prompts   │  │   Prompts   │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     FRAMEWORK LIBRARY                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │  Strategic  │  │ Operational │  │  Financial  │                 │   │
│  │  │  Frameworks │  │  Frameworks │  │  Frameworks │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     DOMAIN KNOWLEDGE                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │  Industry   │  │  Regional   │  │  Technical  │                 │   │
│  │  │  Verticals  │  │   Context   │  │  Reference  │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     OUTPUT TEMPLATES                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │   Reports   │  │   Analyses  │  │   Exports   │                 │   │
│  │  │  Templates  │  │  Templates  │  │   Formats   │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Struktura Katalogów Knowledge Base

```
knowledge_base/
│
├── 📁 system_prompts/                    # LEVEL 1 - Tożsamość agentów
│   ├── orchestrator.md                   # Główny koordynator
│   ├── router.md                         # Klasyfikator zadań
│   ├── conversation.md                   # Agent konwersacyjny
│   └── _meta.yaml                        # Metadata i wersjonowanie
│
├── 📁 agent_prompts/                     # LEVEL 2 - Task prompts
│   │
│   ├── 📁 company_intelligence/
│   │   ├── profile_analysis.md           # Profil firmy
│   │   ├── financial_analysis.md         # Analiza finansowa
│   │   ├── ownership_mapping.md          # Struktura właścicielska
│   │   ├── digital_presence.md           # Obecność cyfrowa
│   │   ├── news_sentiment.md             # News i sentyment
│   │   └── key_people.md                 # Kluczowe osoby
│   │
│   ├── 📁 market_intelligence/
│   │   ├── market_sizing.md              # TAM/SAM/SOM
│   │   ├── trend_analysis.md             # Trendy rynkowe
│   │   ├── segmentation.md               # Segmentacja
│   │   ├── value_chain.md                # Łańcuch wartości
│   │   └── regulatory.md                 # Otoczenie regulacyjne
│   │
│   ├── 📁 competitive_intelligence/
│   │   ├── competitor_mapping.md         # Mapa konkurentów
│   │   ├── benchmarking.md               # Porównania
│   │   ├── share_of_voice.md             # Udział w dyskusji
│   │   ├── pricing_intel.md              # Wywiad cenowy
│   │   └── strategic_moves.md            # Ruchy strategiczne
│   │
│   ├── 📁 website_analysis/
│   │   ├── deep_crawl.md                 # Głęboki crawl
│   │   ├── content_extraction.md         # Ekstrakcja treści
│   │   ├── tech_stack.md                 # Stack technologiczny
│   │   └── seo_analysis.md               # Analiza SEO
│   │
│   └── 📁 synthesis/
│       ├── fact_checking.md              # Weryfikacja faktów
│       ├── insight_generation.md         # Generowanie wniosków
│       ├── framework_application.md      # Aplikowanie frameworków
│       └── report_composition.md         # Składanie raportów
│
├── 📁 frameworks/                        # Szablony frameworków
│   │
│   ├── 📁 strategic/
│   │   ├── swot.md                       # SWOT Analysis
│   │   ├── pestle.md                     # PESTLE Analysis
│   │   ├── porter_five_forces.md         # Porter's Five Forces
│   │   ├── bcg_matrix.md                 # BCG Matrix
│   │   ├── ansoff_matrix.md              # Ansoff Matrix
│   │   └── blue_ocean.md                 # Blue Ocean Strategy
│   │
│   ├── 📁 operational/
│   │   ├── value_chain.md                # Value Chain Analysis
│   │   ├── business_model_canvas.md      # BMC
│   │   ├── lean_canvas.md                # Lean Canvas
│   │   └── jobs_to_be_done.md            # JTBD Framework
│   │
│   └── 📁 financial/
│       ├── ratio_analysis.md             # Wskaźniki finansowe
│       ├── dcf_basics.md                 # DCF fundamentals
│       └── break_even.md                 # Break-even analysis
│
├── 📁 industry_knowledge/                # Wiedza domenowa
│   │
│   ├── 📁 manufacturing/
│   │   ├── plastics_processing.md        # Przetwórstwo tworzyw
│   │   ├── injection_molding.md          # Wtryskiwanie
│   │   ├── toolmaking.md                 # Narzędziownie
│   │   ├── cnc_machining.md              # Obróbka CNC
│   │   └── key_players_poland.md         # Kluczowi gracze PL
│   │
│   ├── 📁 technology/
│   │   ├── saas_metrics.md               # SaaS KPIs
│   │   ├── ai_ml_landscape.md            # AI/ML rynek
│   │   └── cybersecurity.md              # Cyberbezpieczeństwo
│   │
│   └── 📁 general/
│       ├── polish_business_entities.md   # Formy prawne w PL
│       ├── krs_guide.md                  # Jak czytać KRS
│       ├── eu_regulations.md             # Regulacje EU
│       └── financial_statements.md       # Sprawozdania fin.
│
├── 📁 output_templates/                  # Szablony wyjściowe
│   │
│   ├── 📁 reports/
│   │   ├── executive_summary.md          # Streszczenie wykonawcze
│   │   ├── full_company_report.md        # Pełny raport firmowy
│   │   ├── market_overview.md            # Przegląd rynku
│   │   ├── competitive_analysis.md       # Analiza konkurencji
│   │   └── due_diligence.md              # Due diligence
│   │
│   ├── 📁 quick_outputs/
│   │   ├── company_snapshot.md           # Szybki profil
│   │   ├── competitor_comparison.md      # Porównanie
│   │   └── market_brief.md               # Brief rynkowy
│   │
│   └── 📁 exports/
│       ├── docx_structure.md             # Struktura DOCX
│       ├── pptx_structure.md             # Struktura PPTX
│       └── csv_exports.md                # Eksporty CSV
│
├── 📁 examples/                          # Few-shot examples
│   ├── company_analysis_example.md
│   ├── market_sizing_example.md
│   ├── competitive_intel_example.md
│   └── framework_application_example.md
│
└── 📁 config/
    ├── prompt_registry.yaml              # Rejestr wszystkich promptów
    ├── framework_selector.yaml           # Reguły wyboru frameworków
    └── output_rules.yaml                 # Reguły formatowania
```

---

## 3. System Składania Promptów

### 3.1 Architektura 3-poziomowa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FINAL PROMPT                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LEVEL 1: SYSTEM PROMPT (static)                                      │   │
│  │ "Jesteś agentem analizy firmowej. Twoja rola to..."                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    +                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LEVEL 2: TASK PROMPT (selected based on task)                        │   │
│  │ "Przeprowadź analizę profilu firmy według następującej metodologii..." │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    +                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LEVEL 3: CONTEXT (dynamic, injected at runtime)                      │   │
│  │ "Firma: FADO Sp. z o.o., NIP: ..., Dane KRS: ..., User brief: ..." │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    +                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ OUTPUT TEMPLATE (guides structure)                                   │   │
│  │ "Zwróć wynik w formacie JSON: { company_name: ..., ... }"          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Prompt Composition Engine

```python
# backend/services/prompt_composer.py

class PromptComposer:
    """
    Składa wielopoziomowe prompty z bazy wiedzy.
    """
    
    def __init__(self, kb_path: str = "knowledge_base"):
        self.kb_path = kb_path
        self.registry = self._load_registry()
        
    def compose(
        self,
        agent_type: str,
        task_type: str,
        context: dict,
        output_format: str = "json"
    ) -> str:
        """
        Składa pełny prompt z 3 poziomów.
        
        Args:
            agent_type: np. "company_intelligence"
            task_type: np. "profile_analysis"  
            context: dane dynamiczne (firma, brief, zebrane dane)
            output_format: format wyjścia
            
        Returns:
            Złożony prompt gotowy do wysłania do LLM
        """
        
        # Level 1: System prompt
        system_prompt = self._load_system_prompt(agent_type)
        
        # Level 2: Task prompt
        task_prompt = self._load_task_prompt(agent_type, task_type)
        
        # Level 3: Context injection
        context_block = self._format_context(context)
        
        # Output template
        output_template = self._load_output_template(task_type, output_format)
        
        # Compose final prompt
        final_prompt = f"""
{system_prompt}

---
ZADANIE:
{task_prompt}

---
KONTEKST:
{context_block}

---
FORMAT WYJŚCIA:
{output_template}
"""
        return final_prompt.strip()
    
    def _load_system_prompt(self, agent_type: str) -> str:
        """Ładuje system prompt dla typu agenta."""
        path = f"{self.kb_path}/system_prompts/{agent_type}.md"
        return self._read_file(path)
    
    def _load_task_prompt(self, agent_type: str, task_type: str) -> str:
        """Ładuje task prompt dla konkretnego zadania."""
        path = f"{self.kb_path}/agent_prompts/{agent_type}/{task_type}.md"
        return self._read_file(path)
    
    def _format_context(self, context: dict) -> str:
        """Formatuje kontekst dynamiczny."""
        blocks = []
        
        if "company" in context:
            blocks.append(f"FIRMA:\n{self._format_company(context['company'])}")
            
        if "collected_data" in context:
            blocks.append(f"ZEBRANE DANE:\n{context['collected_data']}")
            
        if "user_brief" in context:
            blocks.append(f"BRIEF UŻYTKOWNIKA:\n{context['user_brief']}")
            
        if "previous_results" in context:
            blocks.append(f"WYNIKI POPRZEDNICH AGENTÓW:\n{context['previous_results']}")
            
        return "\n\n".join(blocks)
    
    def _load_output_template(self, task_type: str, format: str) -> str:
        """Ładuje szablon wyjścia."""
        path = f"{self.kb_path}/output_templates/{task_type}_{format}.md"
        if self._file_exists(path):
            return self._read_file(path)
        return self._default_output_template(format)
```

### 3.3 Przykład Składania Promptu

```python
# Przykład użycia

composer = PromptComposer()

# Kontekst dynamiczny
context = {
    "company": {
        "name": "FADO Sp. z o.o.",
        "nip": "9532648925",
        "krs": "0000123456"
    },
    "user_brief": "Interesuje mnie pozycja firmy na rynku armatury przemysłowej",
    "collected_data": {
        "krs_data": { ... },
        "website_data": { ... }
    }
}

# Złóż prompt
final_prompt = composer.compose(
    agent_type="company_intelligence",
    task_type="profile_analysis",
    context=context,
    output_format="json"
)

# Wyślij do LLM
response = llm_service.complete(final_prompt)
```

---

## 4. Rejestr Promptów (prompt_registry.yaml)

```yaml
# knowledge_base/config/prompt_registry.yaml

version: "1.0"
last_updated: "2025-01-13"

system_prompts:
  orchestrator:
    path: system_prompts/orchestrator.md
    version: "1.2"
    description: "Główny koordynator systemu"
    
  router:
    path: system_prompts/router.md
    version: "1.1"
    description: "Klasyfikator i dispatcher zadań"
    
  conversation:
    path: system_prompts/conversation.md
    version: "1.3"
    description: "Agent konwersacyjny w czacie"

agent_prompts:
  company_intelligence:
    profile_analysis:
      path: agent_prompts/company_intelligence/profile_analysis.md
      version: "2.1"
      tools_required: [krs_api, web_search, company_scraper]
      output_schema: schemas/company_profile.json
      estimated_tokens: 2000
      
    financial_analysis:
      path: agent_prompts/company_intelligence/financial_analysis.md
      version: "1.5"
      tools_required: [krs_api, financial_apis]
      output_schema: schemas/financial_analysis.json
      
    ownership_mapping:
      path: agent_prompts/company_intelligence/ownership_mapping.md
      version: "1.3"
      tools_required: [krs_api, graph_db]
      output_schema: schemas/ownership_structure.json
      
    digital_presence:
      path: agent_prompts/company_intelligence/digital_presence.md
      version: "1.4"
      tools_required: [web_search, similarweb_api, builtwith_api]
      output_schema: schemas/digital_presence.json

  market_intelligence:
    market_sizing:
      path: agent_prompts/market_intelligence/market_sizing.md
      version: "1.6"
      tools_required: [web_search, industry_reports]
      output_schema: schemas/market_sizing.json
      
    trend_analysis:
      path: agent_prompts/market_intelligence/trend_analysis.md
      version: "1.2"
      tools_required: [web_search, news_api]
      output_schema: schemas/trends.json

  competitive_intelligence:
    competitor_mapping:
      path: agent_prompts/competitive_intelligence/competitor_mapping.md
      version: "1.8"
      tools_required: [web_search, company_scraper]
      output_schema: schemas/competitor_map.json
      
    benchmarking:
      path: agent_prompts/competitive_intelligence/benchmarking.md
      version: "1.4"
      tools_required: [all_company_tools]
      output_schema: schemas/benchmark.json

  synthesis:
    fact_checking:
      path: agent_prompts/synthesis/fact_checking.md
      version: "1.1"
      tools_required: []
      
    insight_generation:
      path: agent_prompts/synthesis/insight_generation.md
      version: "1.3"
      tools_required: []
      
    report_composition:
      path: agent_prompts/synthesis/report_composition.md
      version: "2.0"
      tools_required: []

frameworks:
  swot:
    path: frameworks/strategic/swot.md
    use_cases: [company_analysis, market_entry, product_launch]
    
  pestle:
    path: frameworks/strategic/pestle.md
    use_cases: [market_entry, expansion, regulatory_review]
    
  porter:
    path: frameworks/strategic/porter_five_forces.md
    use_cases: [industry_analysis, competitive_strategy]
    
  bcg:
    path: frameworks/strategic/bcg_matrix.md
    use_cases: [portfolio_analysis, product_strategy]

output_templates:
  company_profile:
    json: output_templates/quick_outputs/company_snapshot.md
    full_report: output_templates/reports/full_company_report.md
    
  competitive_analysis:
    json: output_templates/quick_outputs/competitor_comparison.md
    full_report: output_templates/reports/competitive_analysis.md
```

---

## 5. Framework Selector (Automatyczny Wybór)

```yaml
# knowledge_base/config/framework_selector.yaml

# Reguły automatycznego wyboru frameworków na podstawie kontekstu

rules:
  - name: "company_swot"
    trigger:
      task_types: [company_analysis, competitive_analysis]
      keywords: [swot, mocne strony, słabe strony, szanse, zagrożenia]
    frameworks: [swot]
    
  - name: "market_entry"
    trigger:
      task_types: [market_analysis]
      keywords: [wejście na rynek, ekspansja, nowy rynek]
    frameworks: [pestle, porter, market_sizing]
    
  - name: "competitive_deep"
    trigger:
      task_types: [competitive_analysis]
      depth: [comprehensive, deep]
    frameworks: [porter, competitor_matrix, share_of_voice]
    
  - name: "strategic_planning"
    trigger:
      keywords: [strategia, plan strategiczny, kierunki rozwoju]
    frameworks: [swot, ansoff, bcg]
    
  - name: "financial_due_diligence"
    trigger:
      task_types: [due_diligence]
      keywords: [finanse, inwestycja, akwizycja]
    frameworks: [ratio_analysis, dcf_basics, break_even]
    
  - name: "product_analysis"
    trigger:
      keywords: [produkt, portfolio, oferta]
    frameworks: [bcg, value_chain, business_model_canvas]

default_frameworks:
  company_analysis: [swot]
  market_analysis: [market_sizing, pestle]
  competitive_analysis: [porter, competitor_matrix]
  
framework_combinations:
  full_strategic_review:
    - swot
    - pestle
    - porter
    - bcg
    
  market_entry_package:
    - pestle
    - porter
    - market_sizing
    - competitor_matrix
```

---

## 6. Wersjonowanie i Aktualizacje

### 6.1 Strategia Wersjonowania

```yaml
# Każdy prompt ma wersję semantic versioning

versioning:
  format: "MAJOR.MINOR"
  
  major_change:
    - Zmiana struktury outputu
    - Zmiana wymaganych narzędzi
    - Fundamentalna zmiana logiki
    
  minor_change:
    - Poprawki promptu
    - Dodanie przykładów
    - Ulepszenia jakościowe

# Historia zmian w _meta.yaml każdego katalogu
```

### 6.2 A/B Testing Promptów

```yaml
# config/ab_testing.yaml

experiments:
  - name: "profile_analysis_v2"
    control: "agent_prompts/company_intelligence/profile_analysis.md"
    variant: "agent_prompts/company_intelligence/profile_analysis_v2.md"
    traffic_split: 0.2  # 20% na variant
    metrics:
      - user_satisfaction
      - data_completeness
      - execution_time
    start_date: "2025-01-15"
    end_date: "2025-02-15"
```

---

## 7. Indeksowanie i Wyszukiwanie

### 7.1 Vector Embeddings dla Knowledge Base

```python
# Indeksowanie bazy wiedzy do vector store

class KnowledgeBaseIndexer:
    """
    Indeksuje bazę wiedzy do wyszukiwania semantycznego.
    Pozwala agentom znajdować relevantne fragmenty wiedzy.
    """
    
    def index_knowledge_base(self):
        """Indeksuje całą bazę wiedzy."""
        
        documents = []
        
        # Indeksuj industry knowledge
        for industry_doc in self._load_industry_docs():
            documents.append({
                "content": industry_doc.content,
                "metadata": {
                    "type": "industry_knowledge",
                    "industry": industry_doc.industry,
                    "topic": industry_doc.topic
                }
            })
            
        # Indeksuj frameworks
        for framework in self._load_frameworks():
            documents.append({
                "content": framework.content,
                "metadata": {
                    "type": "framework",
                    "name": framework.name,
                    "use_cases": framework.use_cases
                }
            })
            
        # Indeksuj examples
        for example in self._load_examples():
            documents.append({
                "content": example.content,
                "metadata": {
                    "type": "example",
                    "task_type": example.task_type
                }
            })
            
        # Zapisz do vector store
        self.vector_store.upsert(documents)
        
    def search(self, query: str, filter_type: str = None) -> list:
        """
        Wyszukuje relevantne fragmenty wiedzy.
        
        Używane przez agentów do:
        - Znajdowania branżowego kontekstu
        - Wyboru odpowiednich frameworków
        - Ładowania przykładów few-shot
        """
        filters = {"type": filter_type} if filter_type else None
        return self.vector_store.search(query, filters=filters, top_k=5)
```

---

## 8. Przykładowe Wpisy Knowledge Base

### 8.1 Industry Knowledge Entry

```markdown
# knowledge_base/industry_knowledge/manufacturing/injection_molding.md

# Wtryskiwanie Tworzyw Sztucznych - Kontekst Branżowy

## Definicja
Wtryskiwanie (injection molding) to proces formowania tworzyw sztucznych 
polegający na uplastycznieniu materiału i wtryśnięciu go pod ciśnieniem 
do formy wtryskowej.

## Kluczowe Parametry Procesu
- Temperatura stopu (melt temperature)
- Ciśnienie wtrysku (injection pressure)
- Czas cyklu (cycle time)
- Temperatura formy (mold temperature)

## Główni Gracze w Polsce
- FADO (Bydgoszcz) - armatura przemysłowa
- Splast (Kutno) - AGD, motoryzacja
- Grupa Azoty (różne lokalizacje) - surowce

## Typowe Wskaźniki
- Marża brutto: 15-25%
- Cykl produkcyjny: 15-60 sekund
- Koszt formy: 50,000-500,000 PLN

## Trendy
- Automatyzacja i Industry 4.0
- Tworzywa biodegradowalne
- Lightweight components (automotive)

## Źródła Danych
- Plastech.pl - portal branżowy
- PlasticsEurope - dane europejskie
- GUS - statystyki krajowe
```

### 8.2 Framework Entry

```markdown
# knowledge_base/frameworks/strategic/swot.md

# SWOT Analysis Framework

## Definicja
SWOT to framework strategiczny analizujący:
- **S**trengths (Mocne strony) - wewnętrzne
- **W**eaknesses (Słabe strony) - wewnętrzne
- **O**pportunities (Szanse) - zewnętrzne
- **T**hreats (Zagrożenia) - zewnętrzne

## Kiedy Stosować
- Analiza pozycji konkurencyjnej firmy
- Ocena nowego projektu/produktu
- Planowanie strategiczne
- Due diligence przed inwestycją

## Metodologia Wypełniania

### Strengths (Mocne Strony)
Pytania pomocnicze:
- Co firma robi lepiej niż konkurencja?
- Jakie unikalne zasoby posiada?
- Co klienci wskazują jako przewagę?

### Weaknesses (Słabe Strony)
Pytania pomocnicze:
- Gdzie firma przegrywa z konkurencją?
- Jakich zasobów/kompetencji brakuje?
- Co klienci krytykują?

### Opportunities (Szanse)
Pytania pomocnicze:
- Jakie trendy rynkowe sprzyjają firmie?
- Jakie nowe segmenty można zdobyć?
- Jakie zmiany regulacyjne tworzą szanse?

### Threats (Zagrożenia)
Pytania pomocnicze:
- Jakie trendy mogą zaszkodzić?
- Co robi konkurencja?
- Jakie ryzyka regulacyjne/makro istnieją?

## Format Wyjściowy

```json
{
  "swot_analysis": {
    "company": "...",
    "date": "...",
    "strengths": [
      {"factor": "...", "evidence": "...", "impact": "high|medium|low"}
    ],
    "weaknesses": [
      {"factor": "...", "evidence": "...", "impact": "high|medium|low"}
    ],
    "opportunities": [
      {"factor": "...", "evidence": "...", "timeline": "..."}
    ],
    "threats": [
      {"factor": "...", "evidence": "...", "probability": "high|medium|low"}
    ],
    "strategic_implications": ["..."],
    "recommended_actions": ["..."]
  }
}
```

## Przykład
[Zobacz: examples/framework_application_example.md]
```

---

*Następny dokument: 03_PROMPTS_L1_SYSTEM.md*
