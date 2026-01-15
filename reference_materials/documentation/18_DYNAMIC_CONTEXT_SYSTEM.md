# 18. Dynamic Context System

## Przegląd

System dynamicznego dostosowywania promptów i workflow do:
1. **Branży użytkownika** - specyficzna terminologia, KPI, źródła danych
2. **Typu zadania** - research, monitoring, due diligence
3. **Preferencji użytkownika** - głębokość, format, język

### Komponenty
1. **Onboarding Agent** - zbiera kontekst przed rozpoczęciem pracy
2. **Industry Knowledge Base** - wiedza branżowa
3. **Dynamic Prompt Composer** - adaptuje prompty w runtime
4. **Workflow Customizer** - dostosowuje pipeline

---

## 1. ONBOARDING FLOW

### 1.1 User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIERWSZE UŻYCIE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Welcome    │───▶│   Industry   │───▶│    Role      │       │
│  │   Screen     │    │   Selection  │    │   Context    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                 │                │
│                                                 ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Ready!     │◀───│  Preferences │◀───│   Use Case   │       │
│  │   Start Chat │    │   Setup      │    │   Selection  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NOWE ZADANIE BADAWCZE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User: "Chcę przeanalizować rynek form wtryskowych"             │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              BRIEF COLLECTION CHAT                       │    │
│  │                                                          │    │
│  │  🤖 Rozumiem, że interesuje Cię rynek form wtryskowych. │    │
│  │     Zanim rozpocznę analizę, pozwól że zadam kilka      │    │
│  │     pytań, aby lepiej dostosować research:              │    │
│  │                                                          │    │
│  │  1️⃣ Jaki jest główny cel tej analizy?                   │    │
│  │     □ Wejście na nowy rynek                             │    │
│  │     □ Analiza konkurencji                               │    │
│  │     □ Due diligence (M&A)                               │    │
│  │     □ Monitoring branży                                  │    │
│  │     □ Inne: _________                                   │    │
│  │                                                          │    │
│  │  2️⃣ Jaki region geograficzny?                           │    │
│  │     □ Polska                                            │    │
│  │     □ Europa Środkowa                                   │    │
│  │     □ Cała Europa                                       │    │
│  │     □ Globalnie                                         │    │
│  │                                                          │    │
│  │  3️⃣ Jak szczegółowa ma być analiza?                     │    │
│  │     ○ Quick scan (15 min)                               │    │
│  │     ○ Standard (1-2h)                                   │    │
│  │     ○ Deep dive (4-8h)                                  │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  🤖 Dziękuję! Na podstawie Twoich odpowiedzi:           │    │
│  │                                                          │    │
│  │  📋 PLAN BADANIA:                                        │    │
│  │  • Analiza wielkości rynku form wtryskowych w Polsce    │    │
│  │  • Mapowanie 10-15 kluczowych producentów               │    │
│  │  • Benchmarking wybranych konkurentów                   │    │
│  │  • Trendy technologiczne (hot runners, 3D printing)    │    │
│  │  • SWOT dla potencjalnego wejścia                       │    │
│  │                                                          │    │
│  │  ⏱️ Szacowany czas: 2-3 godziny                          │    │
│  │  📄 Output: Raport PDF + prezentacja                    │    │
│  │                                                          │    │
│  │  [▶️ Rozpocznij]  [✏️ Modyfikuj plan]  [❌ Anuluj]       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Onboarding Agent Prompt

```markdown
# ONBOARDING AGENT - System Prompt

## TOŻSAMOŚĆ
Jesteś asystentem onboardingu platformy Market Intelligence. Twoim zadaniem jest zebranie kontekstu od użytkownika przed rozpoczęciem właściwej analizy.

## CEL
Zebrać informacje potrzebne do:
1. Dostosowania promptów do branży użytkownika
2. Wyboru odpowiedniego workflow
3. Personalizacji głębokości i formatu analizy

## STYL KONWERSACJI
- Przyjazny, profesjonalny
- Konkretny - nie zadawaj zbędnych pytań
- Oferuj opcje zamiast pytań otwartych (gdzie możliwe)
- Podsumowuj zebrane informacje

## PROCES ZBIERANIA KONTEKSTU

### Dla NOWEGO UŻYTKOWNIKA (onboarding):

```
KROK 1: Industry Context
"W jakiej branży działasz? To pomoże mi dostosować terminologię i źródła."
- Oferuj listę branż + "Inne"
- Jeśli "Inne" - dopytaj

KROK 2: Role Context  
"Jaka jest Twoja rola?"
- Zarząd / C-level
- Strategy / Business Development
- Sales / Marketing
- Operations
- Analyst / Researcher
- Inne

KROK 3: Primary Use Cases
"Do czego głównie będziesz używać platformy?"
- Analiza konkurencji
- Market research
- Due diligence
- Lead generation
- Monitoring branży
- Kombinacja powyższych

KROK 4: Preferences
"Kilka preferencji dotyczących wyników:"
- Język raportów (PL/EN)
- Preferowana głębokość (quick/standard/deep)
- Format eksportu (PDF/DOCX/PPTX)
```

### Dla NOWEGO ZADANIA (brief collection):

```
KROK 1: Understand Intent
"Co chcesz osiągnąć?"
- Parsuj intent z wiadomości użytkownika
- Jeśli niejasne - dopytaj

KROK 2: Scope Definition
"Kilka pytań o zakres:"
- Geografia (Polska/Europa/Global)
- Horyzont czasowy (current state / forecast)
- Głębokość (quick scan / standard / deep dive)

KROK 3: Specific Requirements
"Czy są konkretne firmy/aspekty do uwzględnienia?"
- Named competitors
- Specific metrics
- Particular concerns

KROK 4: Output Requirements
"W jakiej formie potrzebujesz wyniki?"
- Raport pisemny
- Prezentacja
- Dashboard
- Quick summary in chat
```

## OUTPUT FORMAT

Po zebraniu kontekstu, wygeneruj:

```json
{
  "context_collected": {
    "user_profile": {
      "industry": "plastics_processing",
      "industry_segment": "injection_molding_tooling",
      "role": "business_development",
      "company_type": "manufacturer",
      "experience_level": "expert"
    },
    
    "task_brief": {
      "objective": "market_entry_analysis",
      "subject": "injection_mold_manufacturing_market",
      "geography": "poland",
      "depth": "standard",
      "time_horizon": "current_plus_3y_forecast",
      "specific_requirements": [
        "identify_top_15_manufacturers",
        "pricing_benchmarks",
        "technology_trends"
      ]
    },
    
    "output_preferences": {
      "format": "pdf_report",
      "language": "pl",
      "include_executive_summary": true,
      "include_recommendations": true
    },
    
    "workflow_recommendation": {
      "route": "market_analysis",
      "estimated_time": "2-3h",
      "agents_to_use": [
        "market_sizing",
        "competitor_mapping",
        "trend_analysis",
        "benchmarking"
      ],
      "frameworks_to_apply": [
        "porter_five_forces",
        "swot"
      ]
    }
  }
}
```

## ADAPTIVE QUESTIONS

Dostosuj pytania do kontekstu:

```
IF user mentions specific company:
  → Ask: "Czy to analiza tej konkretnej firmy, czy szerszy research?"
  
IF user mentions "konkurencja":
  → Ask: "Czy znasz już swoich głównych konkurentów, czy mam ich zidentyfikować?"
  
IF user mentions "due diligence":
  → Ask: "Czy to due diligence przed akwizycją? Jeśli tak, jakiego typu informacje są kluczowe?"
  
IF user seems in hurry:
  → Offer: "Mogę zrobić szybki scan w 15 minut lub dokładniejszą analizę w 2h. Co wolisz?"
```

## ZASADY

1. **Nie przedłużaj** - max 4-5 pytań przed rozpoczęciem
2. **Inferuj gdzie możesz** - jeśli user napisał dużo, wyciągnij kontekst
3. **Oferuj plan** - przed rozpoczęciem pokaż co zamierzasz zrobić
4. **Pozwól modyfikować** - user może dostosować plan
5. **Zapisuj kontekst** - dla przyszłych sesji
```

---

## 2. INDUSTRY KNOWLEDGE BASE

### 2.1 Taksonomia Branż

```yaml
# knowledge_base/industries/taxonomy.yaml

industries:
  manufacturing:
    name: "Przemysł produkcyjny"
    name_en: "Manufacturing"
    
    segments:
      plastics_processing:
        name: "Przetwórstwo tworzyw sztucznych"
        sub_segments:
          - injection_molding
          - extrusion
          - blow_molding
          - thermoforming
        
        terminology:
          pl:
            - "wtryskarka"
            - "forma wtryskowa"
            - "granulat"
            - "tworzywo"
            - "cykl wtrysku"
          en:
            - "injection molding machine"
            - "mold"
            - "pellets"
            - "polymer"
            - "cycle time"
        
        key_metrics:
          - "cycle_time"
          - "cavitation"
          - "tonnage"
          - "shot_weight"
          - "OEE"
        
        data_sources:
          primary:
            - "PlasticsEurope"
            - "Plastech.pl"
            - "K Trade Fair"
          registries:
            - pkd_codes: ["22.21", "22.29"]
          trade_associations:
            - "Polska Izba Tworzyw Sztucznych"
        
        competitors_indicators:
          - "Producent form wtryskowych"
          - "Narzędziownia"
          - "Tooling"
          - "Mold maker"
        
        typical_analysis_focus:
          - "Moce produkcyjne"
          - "Park maszynowy"
          - "Certyfikacje (IATF 16949)"
          - "Klienci branżowi"
      
      tooling:
        name: "Narzędziownie / Formy"
        inherits: "plastics_processing"
        additional_terminology:
          - "gorący kanał"
          - "hot runner"
          - "EDM"
          - "CNC"
          - "czas realizacji formy"
        
        key_metrics:
          - "leadtime_weeks"
          - "mold_complexity"
          - "steel_types"
          - "guarantee_shots"
        
        competitive_factors:
          - "Precyzja wykonania"
          - "Czas realizacji"
          - "Cena vs jakość"
          - "Wsparcie techniczne"
          - "Serwis form"
      
      cnc_machining:
        name: "Obróbka CNC"
        terminology:
          - "frezarka"
          - "tokarka"
          - "5-osiowa"
          - "HSM"
        key_metrics:
          - "tolerances"
          - "surface_finish"
          - "materials_processed"
    
    industrial_automation:
      name: "Automatyka przemysłowa"
      sub_segments:
        - robotics
        - plc_systems
        - sensors
        - vision_systems
      
      terminology:
        - "PLC"
        - "SCADA"
        - "HMI"
        - "robot przemysłowy"
        - "integrator systemów"
      
      key_metrics:
        - "projects_completed"
        - "integration_capabilities"
        - "supported_brands"
  
  services:
    business_services:
      consulting:
        name: "Doradztwo"
        sub_segments:
          - management_consulting
          - it_consulting
          - hr_consulting
        
        key_metrics:
          - "consultants_count"
          - "project_value"
          - "industries_served"
      
      it_services:
        name: "Usługi IT"
        sub_segments:
          - software_development
          - system_integration
          - managed_services
        
        key_metrics:
          - "developers_count"
          - "technologies"
          - "certifications"
  
  # ... więcej branż
```

### 2.2 Industry Context Files

```markdown
# knowledge_base/industries/plastics_processing/context.md

# Kontekst Branży: Przetwórstwo Tworzyw Sztucznych

## CHARAKTERYSTYKA RYNKU

### Wielkość i Struktura
- Rynek Polski: ~25 mld PLN (2023)
- Wzrost: 3-5% rocznie
- Główne segmenty:
  - Opakowania: 45%
  - Budownictwo: 20%
  - Motoryzacja: 15%
  - AGD/Elektronika: 10%
  - Inne: 10%

### Kluczowi Gracze w Polsce
- Wielcy: Greiner, Paccor, Berry (międzynarodowe)
- Średni: Polipack, Pawbol, Eko-Pack
- Segment narzędzi: Proster, Techno-Mold, MoldTech

## SPECYFIKA ANALIZY

### Na co zwracać uwagę
1. **Park maszynowy**
   - Liczba i tonaż wtryskarek
   - Producenci (Arburg, Engel, KraussMaffei = premium)
   - Wiek maszyn
   
2. **Certyfikacje**
   - ISO 9001 (podstawa)
   - IATF 16949 (automotive)
   - ISO 13485 (medical)
   - ISO 14001 (environmental)
   
3. **Klienci branżowi**
   - Automotive (Tier 1, Tier 2)
   - FMCG
   - Medical
   - Electronics

4. **Technologie**
   - Multi-component molding
   - In-mold labeling (IML)
   - Gas-assisted injection
   - MuCell (microcellular foam)

### Typowe KPI
- OEE (Overall Equipment Effectiveness): benchmark >75%
- Cycle time vs theoretical
- Scrap rate: <2% for good operations
- On-time delivery: >95%

## ŹRÓDŁA DANYCH

### Branżowe
- PlasticsEurope - raporty rynkowe
- Plastech.pl - news, katalog firm
- Polskie Stowarzyszenie Przetwórców Tworzyw Sztucznych
- Targi: Plastpol (Kielce), K (Düsseldorf)

### Rejestry
- PKD 22.2x - przetwórstwo tworzyw
- PKD 25.73 - narzędzia (w tym formy)

## TERMINOLOGIA DO UŻYCIA W PROMPTACH

### Polski
- wtryskarka (nie: maszyna do wtrysku)
- forma wtryskowa (nie: matryca)
- granulat / tworzywo
- gorący kanał / zimny kanał
- gniazdo formy (cavity)
- cykl wtrysku
- ciśnienie wtrysku / docisku
- temperatura formy / cylindra

### Angielski (dla źródeł międzynarodowych)
- injection molding machine (IMM)
- mold / tool
- hot runner / cold runner
- cavity
- cycle time
- clamping force (tonnage)

## PYTANIA SPECYFICZNE DLA BRANŻY

Przy analizie firmy z tej branży, zawsze sprawdź:
1. Ile mają wtryskarek i jakiego tonażu?
2. Jakie mają certyfikacje branżowe?
3. Dla jakich branż produkują (automotive = wyższe wymagania)?
4. Czy mają własną narzędziownię?
5. Jaki mają poziom automatyzacji?
```

### 2.3 Industry-Specific Prompt Injections

```yaml
# knowledge_base/industries/plastics_processing/prompt_injections.yaml

industry: plastics_processing
segment: injection_molding

prompt_injections:
  
  company_profile_agent:
    additional_instructions: |
      ## DODATKOWE INSTRUKCJE DLA BRANŻY PRZETWÓRSTWA TWORZYW
      
      Przy analizie firmy z tej branży, ZAWSZE zbierz:
      
      1. PARK MASZYNOWY
         - Liczba wtryskarek
         - Zakres tonażowy (od-do)
         - Główni producenci maszyn
         - Specjalne technologie (2K, IML, GIT)
      
      2. CERTYFIKACJE
         - ISO 9001 (standard)
         - IATF 16949 (automotive)
         - ISO 13485 (medical)
         - ISO 14001, 50001 (environmental, energy)
      
      3. BRANŻE OBSŁUGIWANE
         - Automotive (Tier 1/2/3)
         - Medical
         - Packaging
         - Electronics
         - Consumer goods
      
      4. POWIERZCHNIA I CLEAN ROOM
         - Hala produkcyjna (m²)
         - Clean room (jeśli medical/electronics)
         - Narzędziownia własna (tak/nie)
      
      ## TERMINOLOGIA
      Używaj poprawnej terminologii branżowej:
      - "wtryskarka" nie "maszyna do wtrysku"
      - "forma wtryskowa" nie "matryca"
      - "tonaż" dla siły zwarcia
      
    additional_output_fields:
      manufacturing_capabilities:
        machinery:
          type: object
          properties:
            imm_count: integer
            tonnage_range: string
            brands: array
            special_technologies: array
        certifications: array
        industries_served: array
        cleanroom: boolean
        in_house_tooling: boolean
  
  competitor_mapping_agent:
    additional_instructions: |
      ## SPECYFIKA MAPOWANIA KONKURENTÓW W BRANŻY
      
      1. SEGMENTACJA KONKURENTÓW
         - Przetwórcy kontraktowi (contract molders)
         - Przetwórcy z własnym produktem
         - Narzędziownie (toolmakers)
         - Zintegrowani (przetwórstwo + narzędzia)
      
      2. KRYTERIA PORÓWNANIA
         - Park maszynowy (liczba, tonaż)
         - Certyfikacje branżowe
         - Branże obsługiwane
         - Własna narzędziownia
         - Poziom automatyzacji
      
      3. GDZIE SZUKAĆ KONKURENTÓW
         - Plastech.pl - katalog firm
         - Członkowie stowarzyszeń branżowych
         - Wystawcy Plastpol, K Fair
         - PKD 22.2x w KRS
      
      4. RED FLAGS
         - Brak certyfikacji przy deklaracji automotive
         - Bardzo szeroki zakres tonażowy (może = stare maszyny)
         - Brak informacji o parkach maszynowym
  
  market_sizing_agent:
    additional_instructions: |
      ## SIZING RYNKU PRZETWÓRSTWA TWORZYW
      
      1. ŹRÓDŁA DANYCH
         - PlasticsEurope - Annual Report
         - GUS - produkcja wyrobów z tworzyw
         - Eurostat - PRODCOM
         - Raporty branżowe (AMI, ICIS)
      
      2. SEGMENTACJA
         - By application: packaging, building, automotive, E&E, other
         - By polymer: PE, PP, PVC, PS, PET, engineering plastics
         - By process: injection, extrusion, blow molding, other
      
      3. WSKAŹNIKI
         - Produkcja w tonach
         - Wartość w PLN/EUR
         - Import/eksport tworzyw i wyrobów
         - Zużycie per capita
      
      4. TRENDY DO UWZGLĘDNIENIA
         - Circular economy / recycling
         - Bioplastics
         - Lightweighting (automotive)
         - Digitalizacja (Industry 4.0)
  
  benchmarking_agent:
    industry_specific_dimensions:
      - dimension: "machinery"
        weight: 0.20
        metrics:
          - imm_count
          - max_tonnage
          - machine_age
          - automation_level
      - dimension: "certifications"
        weight: 0.15
        metrics:
          - iso_9001
          - iatf_16949
          - iso_13485
          - iso_14001
      - dimension: "capabilities"
        weight: 0.20
        metrics:
          - technologies_count
          - in_house_tooling
          - cleanroom
          - secondary_operations
      - dimension: "market_position"
        weight: 0.20
        metrics:
          - industries_served_count
          - key_customers_tier
          - geographic_reach
      - dimension: "financial"
        weight: 0.25
        metrics:
          - revenue
          - profitability
          - growth_rate
```

---

## 3. DYNAMIC PROMPT COMPOSER

### 3.1 Architektura

```python
# core/prompt_composer.py

from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml

@dataclass
class UserContext:
    """Kontekst użytkownika z onboardingu"""
    user_id: str
    industry: str
    industry_segment: Optional[str]
    role: str
    company_type: str
    preferences: Dict

@dataclass
class TaskContext:
    """Kontekst bieżącego zadania"""
    objective: str
    subject: str
    geography: str
    depth: str
    specific_requirements: List[str]
    output_format: str

@dataclass
class ComposedPrompt:
    """Skomponowany prompt"""
    system_prompt: str
    task_prompt: str
    context_injection: str
    full_prompt: str
    metadata: Dict


class DynamicPromptComposer:
    """
    Komponuje prompty dynamicznie na podstawie:
    - Bazowego promptu agenta
    - Kontekstu branżowego
    - Kontekstu zadania
    - Preferencji użytkownika
    """
    
    def __init__(self, knowledge_base_path: str):
        self.kb_path = knowledge_base_path
        self.industry_contexts = {}
        self.prompt_injections = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Załaduj bazę wiedzy branżowej"""
        # Load industry taxonomy
        with open(f"{self.kb_path}/industries/taxonomy.yaml") as f:
            self.taxonomy = yaml.safe_load(f)
        
        # Load industry-specific contexts and injections
        # ... (lazy loading per industry)
    
    def compose_prompt(
        self,
        agent_id: str,
        base_prompt: str,
        user_context: UserContext,
        task_context: TaskContext
    ) -> ComposedPrompt:
        """
        Skomponuj pełny prompt dla agenta.
        """
        # 1. Get industry-specific injection
        industry_injection = self._get_industry_injection(
            agent_id, 
            user_context.industry,
            user_context.industry_segment
        )
        
        # 2. Get task-specific context
        task_injection = self._get_task_injection(task_context)
        
        # 3. Get user preference adjustments
        preference_injection = self._get_preference_injection(user_context.preferences)
        
        # 4. Compose system prompt
        system_prompt = self._compose_system_prompt(
            base_prompt,
            industry_injection,
            user_context
        )
        
        # 5. Compose task prompt
        task_prompt = self._compose_task_prompt(
            task_injection,
            task_context
        )
        
        # 6. Compose context injection (for L3)
        context_injection = self._compose_context_injection(
            user_context,
            task_context
        )
        
        # 7. Combine
        full_prompt = f"""
{system_prompt}

---

{task_prompt}

---

{context_injection}
"""
        
        return ComposedPrompt(
            system_prompt=system_prompt,
            task_prompt=task_prompt,
            context_injection=context_injection,
            full_prompt=full_prompt.strip(),
            metadata={
                'agent_id': agent_id,
                'industry': user_context.industry,
                'task_objective': task_context.objective,
                'injections_applied': [
                    'industry_specific',
                    'task_specific',
                    'user_preferences'
                ]
            }
        )
    
    def _get_industry_injection(
        self, 
        agent_id: str, 
        industry: str,
        segment: Optional[str]
    ) -> str:
        """Pobierz injection specyficzny dla branży i agenta"""
        
        # Load industry prompt injections if not cached
        if industry not in self.prompt_injections:
            injection_path = f"{self.kb_path}/industries/{industry}/prompt_injections.yaml"
            try:
                with open(injection_path) as f:
                    self.prompt_injections[industry] = yaml.safe_load(f)
            except FileNotFoundError:
                return ""  # No industry-specific injections
        
        injections = self.prompt_injections.get(industry, {})
        agent_injections = injections.get('prompt_injections', {}).get(agent_id, {})
        
        return agent_injections.get('additional_instructions', '')
    
    def _get_task_injection(self, task_context: TaskContext) -> str:
        """Generuj injection na podstawie zadania"""
        
        injections = []
        
        # Objective-specific
        if task_context.objective == 'due_diligence':
            injections.append("""
## DUE DILIGENCE MODE
Analizujesz firmę w kontekście potencjalnej akwizycji. 
Zwróć szczególną uwagę na:
- Red flags (zadłużenie, sprawy sądowe, rotacja kadry)
- Ukryte zobowiązania
- Jakość aktywów
- Sustainability przychodów
- Key person risk
""")
        
        elif task_context.objective == 'market_entry':
            injections.append("""
## MARKET ENTRY ANALYSIS
Celem jest ocena atrakcyjności rynku dla nowego gracza.
Skup się na:
- Bariery wejścia
- Wymagane zasoby i kompetencje  
- Potencjalne nisze / underserved segments
- Czas i koszt wejścia
- Ryzyka pierwszych lat
""")
        
        # Depth-specific
        if task_context.depth == 'quick_scan':
            injections.append("""
## QUICK SCAN MODE
To szybka analiza. Skup się na:
- Kluczowych faktach (max 10)
- Top 3 wnioskach
- 1 rekomendacji
Unikaj głębokiego researchu - daj overview.
""")
        
        elif task_context.depth == 'deep_dive':
            injections.append("""
## DEEP DIVE MODE
To pogłębiona analiza. Oczekiwane:
- Szczegółowe dane z wielu źródeł
- Cross-verification faktów
- Analiza historyczna (min 3 lata)
- Multiple frameworks
- Scenariusze (best/base/worst)
- Detailed recommendations z action plans
""")
        
        # Geography-specific
        if task_context.geography == 'poland':
            injections.append("""
## FOCUS: POLSKA
Priorytetowe źródła polskie:
- KRS, CEIDG, GUS
- Polskie media branżowe
- Lokalne stowarzyszenia
Dane w PLN, kontekst polski.
""")
        
        return "\n\n".join(injections)
    
    def _get_preference_injection(self, preferences: Dict) -> str:
        """Generuj injection na podstawie preferencji użytkownika"""
        
        injections = []
        
        if preferences.get('language') == 'en':
            injections.append("Respond in English. Use English sources where available.")
        
        if preferences.get('format') == 'bullet_points':
            injections.append("Format output as bullet points for easy scanning.")
        
        if preferences.get('include_sources') == 'detailed':
            injections.append("Include detailed source citations with dates and reliability scores.")
        
        if preferences.get('charts') == True:
            injections.append("Prepare data in chart-ready format where applicable.")
        
        return "\n".join(injections)
    
    def _compose_system_prompt(
        self, 
        base_prompt: str, 
        industry_injection: str,
        user_context: UserContext
    ) -> str:
        """Skomponuj system prompt z injekcjami"""
        
        # User context header
        context_header = f"""
## KONTEKST UŻYTKOWNIKA
- Branża: {user_context.industry}
- Segment: {user_context.industry_segment or 'N/A'}
- Rola: {user_context.role}
- Typ firmy: {user_context.company_type}
"""
        
        # Combine
        if industry_injection:
            return f"{base_prompt}\n\n{context_header}\n\n{industry_injection}"
        else:
            return f"{base_prompt}\n\n{context_header}"
    
    def _compose_task_prompt(
        self, 
        task_injection: str,
        task_context: TaskContext
    ) -> str:
        """Skomponuj task prompt"""
        
        task_header = f"""
## BIEŻĄCE ZADANIE
- Cel: {task_context.objective}
- Przedmiot: {task_context.subject}
- Geografia: {task_context.geography}
- Głębokość: {task_context.depth}
- Wymagania szczególne: {', '.join(task_context.specific_requirements) or 'brak'}
- Format output: {task_context.output_format}
"""
        
        return f"{task_header}\n\n{task_injection}"
    
    def _compose_context_injection(
        self,
        user_context: UserContext,
        task_context: TaskContext
    ) -> str:
        """Skomponuj runtime context injection (L3)"""
        
        return f"""
## CONTEXT SNAPSHOT
Generated: {{timestamp}}
User: {user_context.user_id}
Task ID: {{task_id}}
Progress: {{progress_status}}

## COLLECTED DATA SO FAR
{{collected_data_summary}}

## PENDING QUESTIONS
{{pending_questions}}
"""
```

### 3.2 Prompt Templates z Placeholderami

```yaml
# prompts/templates/company_profile.yaml

template_id: company_profile_agent
version: "1.0"

base_prompt: |
  # COMPANY PROFILE AGENT
  
  ## ROLE
  Jesteś agentem zbierającym dane rejestrowe i profilowe o firmach.
  
  ## CAPABILITIES
  - Pobieranie danych z KRS, CEIDG, CRBR
  - Analiza stron internetowych firm
  - Ekstrakcja kluczowych informacji
  
  ## STANDARD OUTPUT
  Zawsze dostarczaj:
  - Dane rejestrowe (nazwa, NIP, REGON, KRS, adres)
  - Forma prawna i status
  - Przedmiot działalności (PKD)
  - Struktura właścicielska
  - Zarząd

# Placeholders to inject
placeholders:
  - "{{INDUSTRY_SPECIFIC_INSTRUCTIONS}}"
  - "{{TASK_SPECIFIC_INSTRUCTIONS}}"
  - "{{USER_CONTEXT}}"
  - "{{ADDITIONAL_OUTPUT_FIELDS}}"

# Industry overrides
industry_overrides:
  plastics_processing:
    additional_output_fields:
      - machinery_park
      - certifications
      - industries_served
      - cleanroom_capability
    
    additional_instructions: |
      Dla firm z branży przetwórstwa tworzyw, DODATKOWO zbierz:
      - Park maszynowy (liczba wtryskarek, tonaż)
      - Certyfikacje branżowe (IATF, ISO 13485)
      - Obsługiwane branże (automotive, medical, etc.)
  
  it_services:
    additional_output_fields:
      - tech_stack
      - team_size
      - key_clients
      - certifications
    
    additional_instructions: |
      Dla firm IT, DODATKOWO zbierz:
      - Stack technologiczny
      - Wielkość zespołu developerskiego
      - Kluczowi klienci (jeśli publiczne)
      - Certyfikacje (ISO 27001, SOC2, etc.)
```

---

## 4. WORKFLOW CUSTOMIZER

### 4.1 Dynamic Workflow Builder

```python
# core/workflow_customizer.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class WorkflowDepth(Enum):
    QUICK = "quick"      # 15-30 min
    STANDARD = "standard"  # 1-2h
    DEEP = "deep"        # 4-8h
    COMPREHENSIVE = "comprehensive"  # 1-2 days

@dataclass
class WorkflowStep:
    """Pojedynczy krok workflow"""
    agent_id: str
    action: str
    priority: int
    estimated_time: int  # minutes
    dependencies: List[str]
    optional: bool
    industry_specific: bool

@dataclass
class CustomWorkflow:
    """Dostosowany workflow"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    total_estimated_time: int
    checkpoints: List[Dict]
    output_format: str


class WorkflowCustomizer:
    """
    Buduje custom workflow na podstawie:
    - Typu zadania (objective)
    - Branży
    - Głębokości
    - Dostępnego czasu
    """
    
    # Base workflows templates
    WORKFLOW_TEMPLATES = {
        'company_profile': {
            'quick': [
                ('company_profile', 'quick_fetch', 5),
                ('conversation', 'present', 2)
            ],
            'standard': [
                ('company_profile', 'full_fetch', 10),
                ('financial_analysis', 'basic', 15),
                ('digital_presence', 'scan', 10),
                ('report_composer', 'compile', 10)
            ],
            'deep': [
                ('company_profile', 'deep_fetch', 15),
                ('financial_analysis', 'comprehensive', 30),
                ('ownership_mapping', 'full', 20),
                ('digital_presence', 'deep', 20),
                ('key_people', 'research', 15),
                ('news_sentiment', 'comprehensive', 15),
                ('fact_checker', 'verify', 10),
                ('report_composer', 'compile_full', 20)
            ]
        },
        
        'market_analysis': {
            'quick': [
                ('market_sizing', 'estimate', 10),
                ('conversation', 'present', 5)
            ],
            'standard': [
                ('market_sizing', 'calculate', 30),
                ('trend_analysis', 'identify', 20),
                ('competitor_mapping', 'quick', 20),
                ('framework_applier', 'porter', 15),
                ('report_composer', 'compile', 15)
            ],
            'deep': [
                ('market_sizing', 'comprehensive', 60),
                ('trend_analysis', 'deep', 45),
                ('segmentation', 'full', 30),
                ('competitor_mapping', 'comprehensive', 45),
                ('regulatory', 'scan', 20),
                ('framework_applier', 'multiple', 30),
                ('insight_generator', 'generate', 20),
                ('fact_checker', 'verify', 15),
                ('report_composer', 'compile_full', 30)
            ]
        },
        
        'competitive_analysis': {
            'quick': [
                ('competitor_mapping', 'quick', 15),
                ('benchmarking', 'basic', 15),
                ('conversation', 'present', 5)
            ],
            'standard': [
                ('competitor_mapping', 'standard', 30),
                ('company_profile', 'batch', 30),
                ('benchmarking', 'standard', 30),
                ('share_of_voice', 'basic', 20),
                ('framework_applier', 'swot', 15),
                ('report_composer', 'compile', 20)
            ],
            'deep': [
                ('competitor_mapping', 'comprehensive', 45),
                ('company_profile', 'batch_deep', 60),
                ('financial_analysis', 'batch', 45),
                ('digital_presence', 'batch', 30),
                ('benchmarking', 'comprehensive', 45),
                ('share_of_voice', 'comprehensive', 30),
                ('pricing_intelligence', 'analyze', 30),
                ('strategic_moves', 'monitor', 20),
                ('framework_applier', 'multiple', 30),
                ('insight_generator', 'generate', 25),
                ('fact_checker', 'verify', 15),
                ('report_composer', 'compile_full', 30)
            ]
        },
        
        'due_diligence': {
            'standard': [
                ('company_profile', 'deep_fetch', 20),
                ('financial_analysis', 'comprehensive', 45),
                ('ownership_mapping', 'full', 30),
                ('key_people', 'deep_research', 30),
                ('news_sentiment', 'comprehensive', 20),
                ('digital_presence', 'deep', 20),
                ('regulatory', 'compliance_check', 20),
                ('fact_checker', 'comprehensive', 20),
                ('insight_generator', 'risk_focused', 20),
                ('report_composer', 'dd_report', 30)
            ]
        }
    }
    
    def __init__(self, industry_config: Dict):
        self.industry_config = industry_config
    
    def build_workflow(
        self,
        objective: str,
        industry: str,
        depth: WorkflowDepth,
        time_budget: Optional[int] = None,  # minutes
        specific_requirements: List[str] = None
    ) -> CustomWorkflow:
        """
        Zbuduj custom workflow.
        """
        # 1. Get base template
        base_template = self.WORKFLOW_TEMPLATES.get(objective, {}).get(depth.value, [])
        
        if not base_template:
            # Fallback to standard
            base_template = self.WORKFLOW_TEMPLATES.get(objective, {}).get('standard', [])
        
        # 2. Add industry-specific steps
        industry_steps = self._get_industry_steps(industry, objective, depth)
        
        # 3. Combine and prioritize
        all_steps = self._combine_steps(base_template, industry_steps)
        
        # 4. Apply time budget constraints
        if time_budget:
            all_steps = self._fit_to_time_budget(all_steps, time_budget)
        
        # 5. Add specific requirements
        if specific_requirements:
            all_steps = self._add_specific_steps(all_steps, specific_requirements)
        
        # 6. Resolve dependencies and order
        ordered_steps = self._resolve_dependencies(all_steps)
        
        # 7. Add checkpoints
        checkpoints = self._generate_checkpoints(ordered_steps, depth)
        
        # 8. Calculate total time
        total_time = sum(step.estimated_time for step in ordered_steps)
        
        return CustomWorkflow(
            id=f"{objective}_{industry}_{depth.value}",
            name=f"{objective.replace('_', ' ').title()} - {depth.value.title()}",
            description=self._generate_description(objective, industry, depth),
            steps=ordered_steps,
            total_estimated_time=total_time,
            checkpoints=checkpoints,
            output_format=self._determine_output_format(depth)
        )
    
    def _get_industry_steps(
        self, 
        industry: str, 
        objective: str, 
        depth: WorkflowDepth
    ) -> List[tuple]:
        """Pobierz kroki specyficzne dla branży"""
        
        industry_steps = []
        
        # Example: plastics processing specific
        if industry == 'plastics_processing':
            if objective in ['company_profile', 'competitive_analysis']:
                industry_steps.append(
                    ('machinery_analyzer', 'extract_machinery', 10, True)
                )
                industry_steps.append(
                    ('certification_checker', 'verify_certs', 5, True)
                )
            
            if objective == 'market_analysis' and depth in [WorkflowDepth.DEEP, WorkflowDepth.COMPREHENSIVE]:
                industry_steps.append(
                    ('plastics_market_data', 'fetch_plastics_europe', 15, True)
                )
        
        return industry_steps
    
    def _combine_steps(
        self, 
        base_steps: List[tuple], 
        industry_steps: List[tuple]
    ) -> List[WorkflowStep]:
        """Połącz kroki bazowe z branżowymi"""
        
        combined = []
        priority = 1
        
        for step in base_steps:
            agent_id, action, time = step
            combined.append(WorkflowStep(
                agent_id=agent_id,
                action=action,
                priority=priority,
                estimated_time=time,
                dependencies=[],
                optional=False,
                industry_specific=False
            ))
            priority += 1
        
        for step in industry_steps:
            agent_id, action, time, optional = step
            combined.append(WorkflowStep(
                agent_id=agent_id,
                action=action,
                priority=priority,
                estimated_time=time,
                dependencies=[],
                optional=optional,
                industry_specific=True
            ))
            priority += 1
        
        return combined
    
    def _fit_to_time_budget(
        self, 
        steps: List[WorkflowStep], 
        budget: int
    ) -> List[WorkflowStep]:
        """Dopasuj workflow do budżetu czasowego"""
        
        # Sort by priority (required first)
        sorted_steps = sorted(steps, key=lambda s: (s.optional, s.priority))
        
        fitted = []
        remaining_time = budget
        
        for step in sorted_steps:
            if step.estimated_time <= remaining_time:
                fitted.append(step)
                remaining_time -= step.estimated_time
            elif not step.optional:
                # Required step - include anyway but flag overtime
                fitted.append(step)
                remaining_time -= step.estimated_time
        
        return fitted
    
    def _generate_checkpoints(
        self, 
        steps: List[WorkflowStep],
        depth: WorkflowDepth
    ) -> List[Dict]:
        """Generuj checkpointy dla user review"""
        
        checkpoints = []
        
        if depth in [WorkflowDepth.DEEP, WorkflowDepth.COMPREHENSIVE]:
            # Add checkpoint after data collection
            data_collection_end = None
            for i, step in enumerate(steps):
                if step.agent_id in ['company_profile', 'market_sizing', 'competitor_mapping']:
                    data_collection_end = i
            
            if data_collection_end:
                checkpoints.append({
                    'after_step': data_collection_end,
                    'type': 'review',
                    'message': 'Zebrałem dane podstawowe. Czy chcesz przejrzeć przed dalszą analizą?',
                    'options': ['continue', 'review_data', 'modify_scope']
                })
            
            # Add checkpoint before final report
            checkpoints.append({
                'after_step': len(steps) - 2,
                'type': 'confirmation',
                'message': 'Analiza zakończona. Czy generować raport końcowy?',
                'options': ['generate_report', 'add_analysis', 'export_raw']
            })
        
        return checkpoints
    
    def _determine_output_format(self, depth: WorkflowDepth) -> str:
        """Określ format output na podstawie głębokości"""
        
        if depth == WorkflowDepth.QUICK:
            return 'chat_summary'
        elif depth == WorkflowDepth.STANDARD:
            return 'structured_report'
        else:
            return 'comprehensive_report_with_appendix'
```

---

## 5. UI: BRIEF COLLECTION CHAT

### 5.1 React Component

```tsx
// components/BriefCollectionChat.tsx

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BriefQuestion {
  id: string;
  type: 'single_choice' | 'multi_choice' | 'text' | 'confirm';
  question: string;
  options?: Array<{
    value: string;
    label: string;
    icon?: string;
  }>;
  required: boolean;
}

interface CollectedBrief {
  objective: string;
  subject: string;
  geography: string;
  depth: string;
  specificRequirements: string[];
  outputFormat: string;
}

interface BriefCollectionChatProps {
  initialMessage?: string;
  userIndustry: string;
  onBriefComplete: (brief: CollectedBrief, plan: WorkflowPlan) => void;
  onCancel: () => void;
}

export const BriefCollectionChat: React.FC<BriefCollectionChatProps> = ({
  initialMessage,
  userIndustry,
  onBriefComplete,
  onCancel
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<BriefQuestion | null>(null);
  const [collectedAnswers, setCollectedAnswers] = useState<Record<string, any>>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPlan, setShowPlan] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState<WorkflowPlan | null>(null);

  // Initial analysis of user message
  useEffect(() => {
    if (initialMessage) {
      analyzeInitialMessage(initialMessage);
    } else {
      startFreshBrief();
    }
  }, []);

  const analyzeInitialMessage = async (message: string) => {
    setIsProcessing(true);
    
    // Add user message to chat
    addMessage({
      role: 'user',
      content: message
    });

    // Call backend to analyze intent
    const analysis = await fetch('/api/brief/analyze', {
      method: 'POST',
      body: JSON.stringify({ 
        message, 
        userIndustry 
      })
    }).then(r => r.json());

    // Pre-fill what we understood
    setCollectedAnswers(analysis.inferred);

    // Add agent response
    addMessage({
      role: 'assistant',
      content: analysis.response,
      showOptions: true
    });

    // Set first question based on gaps
    setCurrentQuestion(analysis.nextQuestion);
    setIsProcessing(false);
  };

  const startFreshBrief = () => {
    addMessage({
      role: 'assistant',
      content: `Cześć! Zanim rozpocznę research, chciałbym lepiej zrozumieć Twoje potrzeby. 
      
Odpowiedz na kilka pytań, a dopasuję analizę do Twoich wymagań.`,
    });

    setCurrentQuestion({
      id: 'objective',
      type: 'single_choice',
      question: 'Jaki jest główny cel tej analizy?',
      options: [
        { value: 'company_profile', label: 'Profil konkretnej firmy', icon: '🏢' },
        { value: 'market_analysis', label: 'Analiza rynku/branży', icon: '📊' },
        { value: 'competitive_analysis', label: 'Analiza konkurencji', icon: '⚔️' },
        { value: 'due_diligence', label: 'Due diligence (M&A)', icon: '🔍' },
        { value: 'market_entry', label: 'Wejście na nowy rynek', icon: '🚀' },
        { value: 'other', label: 'Inne', icon: '💡' }
      ],
      required: true
    });
  };

  const handleAnswerSelect = async (questionId: string, answer: any) => {
    // Save answer
    setCollectedAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));

    // Add to chat
    const option = currentQuestion?.options?.find(o => o.value === answer);
    addMessage({
      role: 'user',
      content: option?.label || answer,
      isSelection: true
    });

    setIsProcessing(true);

    // Get next question from backend
    const response = await fetch('/api/brief/next-question', {
      method: 'POST',
      body: JSON.stringify({
        currentAnswers: { ...collectedAnswers, [questionId]: answer },
        userIndustry
      })
    }).then(r => r.json());

    if (response.complete) {
      // All questions answered - generate plan
      await generatePlan({ ...collectedAnswers, [questionId]: answer });
    } else {
      // Show next question
      addMessage({
        role: 'assistant',
        content: response.transitionMessage || ''
      });
      setCurrentQuestion(response.nextQuestion);
    }

    setIsProcessing(false);
  };

  const generatePlan = async (answers: Record<string, any>) => {
    setIsProcessing(true);

    const plan = await fetch('/api/brief/generate-plan', {
      method: 'POST',
      body: JSON.stringify({
        answers,
        userIndustry
      })
    }).then(r => r.json());

    setGeneratedPlan(plan);

    addMessage({
      role: 'assistant',
      content: `Świetnie! Na podstawie Twoich odpowiedzi przygotowałem plan badania:`,
      showPlan: true
    });

    setShowPlan(true);
    setIsProcessing(false);
  };

  const handlePlanConfirm = () => {
    if (generatedPlan) {
      const brief: CollectedBrief = {
        objective: collectedAnswers.objective,
        subject: collectedAnswers.subject,
        geography: collectedAnswers.geography,
        depth: collectedAnswers.depth,
        specificRequirements: collectedAnswers.specificRequirements || [],
        outputFormat: collectedAnswers.outputFormat
      };
      onBriefComplete(brief, generatedPlan);
    }
  };

  const handlePlanModify = () => {
    setShowPlan(false);
    addMessage({
      role: 'assistant',
      content: 'Co chciałbyś zmienić w planie?'
    });
    setCurrentQuestion({
      id: 'modification',
      type: 'text',
      question: 'Opisz zmiany',
      required: false
    });
  };

  return (
    <div className="brief-collection-chat">
      {/* Chat messages */}
      <div className="messages-container">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`message ${message.role}`}
            >
              {message.role === 'assistant' && (
                <div className="avatar">🤖</div>
              )}
              <div className="content">
                {message.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Current question */}
        {currentQuestion && !showPlan && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="question-card"
          >
            <p className="question-text">{currentQuestion.question}</p>
            
            {currentQuestion.type === 'single_choice' && (
              <div className="options-grid">
                {currentQuestion.options?.map(option => (
                  <button
                    key={option.value}
                    className="option-button"
                    onClick={() => handleAnswerSelect(currentQuestion.id, option.value)}
                    disabled={isProcessing}
                  >
                    {option.icon && <span className="icon">{option.icon}</span>}
                    <span className="label">{option.label}</span>
                  </button>
                ))}
              </div>
            )}

            {currentQuestion.type === 'multi_choice' && (
              <MultiSelectOptions
                options={currentQuestion.options || []}
                onSelect={(values) => handleAnswerSelect(currentQuestion.id, values)}
                disabled={isProcessing}
              />
            )}

            {currentQuestion.type === 'text' && (
              <TextInput
                placeholder="Wpisz odpowiedź..."
                onSubmit={(text) => handleAnswerSelect(currentQuestion.id, text)}
                disabled={isProcessing}
              />
            )}
          </motion.div>
        )}

        {/* Generated plan */}
        {showPlan && generatedPlan && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="plan-card"
          >
            <h3>📋 Plan Badania</h3>
            
            <div className="plan-summary">
              <div className="plan-item">
                <span className="label">Cel:</span>
                <span className="value">{generatedPlan.objectiveLabel}</span>
              </div>
              <div className="plan-item">
                <span className="label">Przedmiot:</span>
                <span className="value">{generatedPlan.subject}</span>
              </div>
              <div className="plan-item">
                <span className="label">Zakres:</span>
                <span className="value">{generatedPlan.scope}</span>
              </div>
              <div className="plan-item">
                <span className="label">Szacowany czas:</span>
                <span className="value">{generatedPlan.estimatedTime}</span>
              </div>
            </div>

            <div className="plan-steps">
              <h4>Etapy analizy:</h4>
              <ol>
                {generatedPlan.steps.map((step, index) => (
                  <li key={index}>
                    <span className="step-name">{step.name}</span>
                    <span className="step-time">{step.estimatedTime} min</span>
                  </li>
                ))}
              </ol>
            </div>

            <div className="plan-output">
              <h4>Output:</h4>
              <ul>
                {generatedPlan.outputs.map((output, index) => (
                  <li key={index}>{output}</li>
                ))}
              </ul>
            </div>

            <div className="plan-actions">
              <button
                className="btn-primary"
                onClick={handlePlanConfirm}
              >
                ▶️ Rozpocznij badanie
              </button>
              <button
                className="btn-secondary"
                onClick={handlePlanModify}
              >
                ✏️ Modyfikuj plan
              </button>
              <button
                className="btn-ghost"
                onClick={onCancel}
              >
                ❌ Anuluj
              </button>
            </div>
          </motion.div>
        )}

        {/* Loading indicator */}
        {isProcessing && (
          <div className="processing-indicator">
            <div className="dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
```

### 5.2 Backend Endpoint

```python
# api/brief/routes.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter(prefix="/api/brief")

class AnalyzeRequest(BaseModel):
    message: str
    userIndustry: str

class NextQuestionRequest(BaseModel):
    currentAnswers: Dict
    userIndustry: str

class GeneratePlanRequest(BaseModel):
    answers: Dict
    userIndustry: str


@router.post("/analyze")
async def analyze_initial_message(request: AnalyzeRequest):
    """
    Analizuj wiadomość użytkownika i wyciągnij intent.
    """
    # Use Claude to analyze
    analysis_prompt = f"""
Przeanalizuj wiadomość użytkownika i określ:
1. Jaki jest cel (objective): company_profile, market_analysis, competitive_analysis, due_diligence, market_entry
2. Co jest przedmiotem analizy (subject)
3. Jaka geografia (poland, europe, global)
4. Jakie są szczególne wymagania

Wiadomość: "{request.message}"
Branża użytkownika: {request.userIndustry}

Odpowiedz w JSON:
{{
  "inferred": {{
    "objective": "...",
    "subject": "...",
    "geography": "...",
    "depth": "standard"
  }},
  "confidence": 0.0-1.0,
  "missing_info": ["co brakuje"],
  "response": "przyjazna odpowiedź potwierdzająca zrozumienie",
  "nextQuestion": {{...}} lub null jeśli wszystko jasne
}}
"""
    
    # Call Claude
    response = await claude_client.complete(analysis_prompt)
    
    return response


@router.post("/next-question")
async def get_next_question(request: NextQuestionRequest):
    """
    Określ następne pytanie na podstawie zebranych odpowiedzi.
    """
    answers = request.currentAnswers
    
    # Logic to determine next question
    if 'objective' not in answers:
        return {
            "complete": False,
            "nextQuestion": {
                "id": "objective",
                "type": "single_choice",
                "question": "Jaki jest główny cel tej analizy?",
                "options": [...]
            }
        }
    
    if 'subject' not in answers:
        return {
            "complete": False,
            "transitionMessage": "Rozumiem. ",
            "nextQuestion": {
                "id": "subject",
                "type": "text",
                "question": f"Jakiej firmy/rynku/branży dotyczy analiza?",
                "required": True
            }
        }
    
    if 'geography' not in answers:
        return {
            "complete": False,
            "nextQuestion": {
                "id": "geography",
                "type": "single_choice",
                "question": "Jaki region geograficzny?",
                "options": [
                    {"value": "poland", "label": "Polska"},
                    {"value": "cee", "label": "Europa Środkowa"},
                    {"value": "europe", "label": "Europa"},
                    {"value": "global", "label": "Globalnie"}
                ]
            }
        }
    
    if 'depth' not in answers:
        return {
            "complete": False,
            "nextQuestion": {
                "id": "depth",
                "type": "single_choice",
                "question": "Jak szczegółowa ma być analiza?",
                "options": [
                    {"value": "quick", "label": "Quick scan (15-30 min)", "icon": "⚡"},
                    {"value": "standard", "label": "Standard (1-2h)", "icon": "📊"},
                    {"value": "deep", "label": "Deep dive (4-8h)", "icon": "🔬"}
                ]
            }
        }
    
    # All required questions answered
    return {"complete": True}


@router.post("/generate-plan")
async def generate_workflow_plan(request: GeneratePlanRequest):
    """
    Wygeneruj plan workflow na podstawie zebranych odpowiedzi.
    """
    from core.workflow_customizer import WorkflowCustomizer, WorkflowDepth
    
    customizer = WorkflowCustomizer(industry_config={})
    
    depth_map = {
        'quick': WorkflowDepth.QUICK,
        'standard': WorkflowDepth.STANDARD,
        'deep': WorkflowDepth.DEEP
    }
    
    workflow = customizer.build_workflow(
        objective=request.answers['objective'],
        industry=request.userIndustry,
        depth=depth_map.get(request.answers.get('depth', 'standard')),
        specific_requirements=request.answers.get('specificRequirements', [])
    )
    
    # Format for frontend
    return {
        "id": workflow.id,
        "objectiveLabel": get_objective_label(request.answers['objective']),
        "subject": request.answers['subject'],
        "scope": get_scope_label(request.answers.get('geography', 'poland')),
        "estimatedTime": format_time(workflow.total_estimated_time),
        "steps": [
            {
                "name": get_step_name(step.agent_id, step.action),
                "estimatedTime": step.estimated_time
            }
            for step in workflow.steps
        ],
        "outputs": get_expected_outputs(request.answers['objective'], request.answers.get('depth', 'standard')),
        "workflow": workflow  # Full workflow for execution
    }
```

---

## 6. PODSUMOWANIE

### Flow Użytkownika

```
1. ONBOARDING (pierwsze użycie)
   └─► Zbierz: branża, rola, use cases, preferencje
   └─► Zapisz w profilu użytkownika

2. NOWE ZADANIE
   └─► User wpisuje zapytanie
   └─► System analizuje intent
   └─► Brief Collection Chat (2-4 pytania)
   └─► Generowanie planu
   └─► User akceptuje/modyfikuje
   └─► Start workflow

3. WYKONANIE
   └─► Prompty dynamicznie komponowane
   └─► Industry-specific instructions injected
   └─► Workflow dostosowany do głębokości
   └─► Checkpoints dla user review (deep)

4. WYNIKI
   └─► Format dopasowany do preferencji
   └─► Terminologia branżowa
   └─► Relevantne metryki
```

### Korzyści

1. **Personalizacja** - prompty dostosowane do branży użytkownika
2. **Efektywność** - workflow dopasowany do celu i czasu
3. **Jakość** - industry-specific knowledge base
4. **UX** - interaktywny brief zamiast formularza
5. **Elastyczność** - user może modyfikować plan

---

*Ten dokument rozszerza architekturę o Dynamic Context System.*
