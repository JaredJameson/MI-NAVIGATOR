# 07. Prompty Level 3 - Synthesis & Reports

## Przegląd

Agenci syntezy i raportowania:
1. **Fact Checker Agent** - weryfikacja i cross-reference
2. **Insight Generator Agent** - wyciąganie wniosków
3. **Framework Applier Agent** - aplikowanie frameworków strategicznych
4. **Report Composer Agent** - składanie raportów końcowych

---

## 1. FACT CHECKER AGENT

```markdown
# FACT CHECKING - Task Prompt

## ZADANIE
Weryfikuj zebrane dane, wykrywaj sprzeczności i określ poziom pewności.

## PROCEDURA WERYFIKACJI

### Krok 1: Cross-Reference Sources
```
Dla każdego kluczowego faktu:
1. Sprawdź ile źródeł go potwierdza
2. Oceń jakość źródeł
3. Wykryj rozbieżności

Poziomy pewności:
- HIGH: 3+ niezależne, wiarygodne źródła
- MEDIUM: 2 źródła lub 1 oficjalne
- LOW: 1 źródło nieoficjalne
- UNVERIFIED: brak możliwości weryfikacji
```

### Krok 2: Consistency Check
```
Sprawdź spójność wewnętrzną:
- Czy liczby się bilansują?
- Czy timeline jest logiczny?
- Czy fakty nie są sprzeczne?
```

### Krok 3: Freshness Assessment
```
Oceń aktualność:
- Data ostatniej aktualizacji
- Czy dane mogły się zmienić?
- Potencjalny wpływ na wnioski
```

### Krok 4: Flag Issues
```
Oznacz problemy:
- CONFLICT: sprzeczne informacje
- OUTDATED: dane przestarzałe
- SINGLE_SOURCE: tylko jedno źródło
- ESTIMATED: wartość szacunkowa
```

## FORMAT WYJŚCIOWY

```json
{
  "fact_check_report": {
    "subject": "FADO Sp. z o.o. - Company Profile",
    "check_date": "2025-01-13",
    "total_facts_checked": 45,
    
    "confidence_summary": {
      "high": 28,
      "medium": 12,
      "low": 3,
      "unverified": 2
    },
    
    "verified_facts": [
      {
        "fact": "FADO zatrudnia 250 osób",
        "sources": ["LinkedIn (245)", "Website (250+)", "GUS estimate (200-300)"],
        "confidence": "high",
        "verified_value": "~250",
        "notes": "Spójne across sources"
      },
      {
        "fact": "Przychody 2023: 50M PLN",
        "sources": ["Sprawozdanie finansowe KRS"],
        "confidence": "high",
        "verified_value": "50.2M PLN",
        "notes": "Oficjalne źródło"
      }
    ],
    
    "conflicts_detected": [
      {
        "fact": "Data założenia firmy",
        "source_1": {"source": "Website", "value": "1995"},
        "source_2": {"source": "KRS", "value": "1998"},
        "resolution": "KRS jest źródłem oficjalnym - przyjmujemy 1998 jako datę rejestracji sp. z o.o., 1995 to prawdopodobnie początek działalności",
        "recommended_value": "1998 (rejestracja), działalność od 1995"
      }
    ],
    
    "outdated_data": [
      {
        "fact": "Struktura zarządu",
        "source": "KRS",
        "data_date": "2024-06-15",
        "age_days": 212,
        "risk": "medium",
        "recommendation": "Zweryfikować w KRS online"
      }
    ],
    
    "unverifiable_claims": [
      {
        "claim": "FADO jest liderem rynku w Polsce",
        "source": "Website",
        "reason": "Brak niezależnych danych o udziałach rynkowych",
        "recommendation": "Oznaczyć jako 'deklarowane przez firmę'"
      }
    ],
    
    "data_quality_score": 82,
    
    "recommendations": [
      "Zaktualizować dane o zarządzie z KRS",
      "Oznaczyć estymaty market share jako niepewne",
      "Zweryfikować datę założenia w następnym kontakcie"
    ]
  }
}
```

## ZASADY WERYFIKACJI

### Hierarchia Źródeł (od najwyższej wiarygodności)
1. Oficjalne rejestry (KRS, CEIDG, GUS)
2. Sprawozdania finansowe audytowane
3. Komunikaty prasowe spółek giełdowych
4. Renomowane media branżowe
5. Strona firmowa
6. LinkedIn/social media
7. Fora, opinie, nieweryfikowalne

### Red Flags
- Dane znacząco różne między źródłami (>20%)
- Brak daty aktualizacji
- Jedyne źródło to sama firma
- Okrągłe liczby bez kontekstu
- Brak możliwości weryfikacji
```

---

## 2. INSIGHT GENERATOR AGENT

```markdown
# INSIGHT GENERATION - Task Prompt

## ZADANIE
Wyciągnij actionable insights z zebranych i zweryfikowanych danych.

## TYPY INSIGHTÓW

### 1. Observational Insights
```
Co widzimy w danych?
- Trendy (rosnące/malejące)
- Anomalie (odstępstwa od normy)
- Wzorce (powtarzające się elementy)
- Korelacje (powiązania)
```

### 2. Comparative Insights
```
Jak wyglądamy na tle?
- vs Konkurencja
- vs Branża
- vs Historia firmy
- vs Best practices
```

### 3. Predictive Insights
```
Co może się wydarzyć?
- Ekstrapolacje trendów
- Scenariusze (best/base/worst)
- Ryzyka i szanse
- Punkty krytyczne
```

### 4. Prescriptive Insights
```
Co powinniśmy zrobić?
- Rekomendacje strategiczne
- Quick wins
- Priorytety działań
- Zasoby potrzebne
```

## FRAMEWORK GENEROWANIA

### SOAR Framework dla Insightów
```
S - Signal: Co widzimy w danych?
O - Observation: Co to oznacza?
A - Analysis: Dlaczego tak jest?
R - Recommendation: Co z tym zrobić?
```

### Przykład:
```
Signal: Rentowność FADO (7.1%) wyższa niż konkurencja (śr. 5.5%)
Observation: Firma jest bardziej efektywna kosztowo
Analysis: Prawdopodobnie dzięki automatyzacji i skupieniu na premium
Recommendation: Utrzymać przewagę, rozważyć reinwestycję w R&D
```

## FORMAT WYJŚCIOWY

```json
{
  "insights_report": {
    "subject": "FADO Sp. z o.o. - Competitive Analysis",
    "generated_at": "2025-01-13",
    
    "executive_summary": {
      "headline": "FADO - silna pozycja z przestrzenią do wzrostu",
      "key_takeaways": [
        "Rentowność powyżej rynku (+30% vs średnia)",
        "Luka w skali vs lider ZETKAMA (-40% revenue)",
        "Przewaga cyfrowa - e-commerce i marketing",
        "Ryzyko: rosnąca konkurencja z zagranicy"
      ]
    },
    
    "detailed_insights": [
      {
        "id": "INS-001",
        "category": "competitive_position",
        "type": "comparative",
        "priority": "high",
        "insight": {
          "signal": "FADO #2 w benchmarku (6.65/10) za ZETKAMA (7.70/10)",
          "observation": "Solidna pozycja, ale wyraźna luka do lidera",
          "analysis": "Luka głównie w skali (revenue, employees) i zasięgu geograficznym. W wymiarach jakościowych (rentowność, digital) FADO dorównuje lub przewyższa.",
          "so_what": "Wzrost organiczny może być niewystarczający do zamknięcia luki. M&A lub partnerstwo strategiczne może być ścieżką przyspieszenia."
        },
        "supporting_data": [
          "FADO revenue: 50M vs ZETKAMA: 120M",
          "FADO countries: 5 vs ZETKAMA: 12"
        ],
        "confidence": "high",
        "actionability": "high"
      },
      {
        "id": "INS-002",
        "category": "competitive_advantage",
        "type": "observational",
        "priority": "high",
        "insight": {
          "signal": "Najwyższa rentowność w grupie (7.1% net margin)",
          "observation": "FADO operuje efektywniej niż konkurencja",
          "analysis": "Prawdopodobne przyczyny: fokus na mid-market/premium, automatyzacja, lean operations. Konkurenci większej skali mają wyższe koszty ogólne.",
          "so_what": "To sustainable competitive advantage. Należy chronić i wzmacniać, nie poświęcać dla wzrostu za wszelką cenę."
        },
        "supporting_data": [
          "FADO margin: 7.1%",
          "POLNA margin: 5.2%",
          "Industry average: 5.5%"
        ],
        "confidence": "high",
        "actionability": "medium"
      },
      {
        "id": "INS-003",
        "category": "market_opportunity",
        "type": "predictive",
        "priority": "medium",
        "insight": {
          "signal": "Brak silnego gracza w B2B e-commerce w branży",
          "observation": "Market gap - cyfrowa dystrybucja niedorozwinięta",
          "analysis": "FADO ma działający e-commerce, konkurencja słaba w digital. Rosnące oczekiwania klientów B2B (wpływ doświadczeń B2C).",
          "so_what": "Okno możliwości na zbudowanie pozycji digital leader. Inwestycja w platform i customer experience może dać sustainable advantage."
        },
        "supporting_data": [
          "FADO: aktywny e-commerce",
          "POLNA: brak e-commerce",
          "ZETKAMA: częściowy e-commerce"
        ],
        "confidence": "medium",
        "actionability": "high"
      },
      {
        "id": "INS-004",
        "category": "threat",
        "type": "predictive",
        "priority": "high",
        "insight": {
          "signal": "POLNA otwiera biuro w Niemczech, ZETKAMA nowy CEO z M&A background",
          "observation": "Konkurenci przyspieszają strategicznie",
          "analysis": "POLNA ekspanduje geograficznie, może zbudować zdolności eksportowe. ZETKAMA może szukać akwizycji - FADO może być celem lub zostać wyprzedzone przez konsolidatora.",
          "so_what": "Okno decyzyjne: rozważyć własną ekspansję, partnerstwo strategiczne, lub przygotowanie na potencjalną ofertę przejęcia."
        },
        "confidence": "medium",
        "actionability": "high"
      }
    ],
    
    "insight_matrix": {
      "headers": ["Insight", "Impact", "Urgency", "Actionability"],
      "data": [
        ["Gap do lidera", "High", "Medium", "High"],
        ["Przewaga rentowności", "High", "Low", "Medium"],
        ["E-commerce opportunity", "Medium", "High", "High"],
        ["Competitive threats", "High", "High", "High"]
      ]
    },
    
    "recommended_actions": {
      "immediate": [
        {
          "action": "Pogłębiona analiza ruchów ZETKAMA",
          "rationale": "Potencjalna aktywność M&A może wpłynąć na FADO",
          "resources": "1 tydzień, zespół strategii"
        }
      ],
      "short_term": [
        {
          "action": "Plan rozwoju e-commerce B2B",
          "rationale": "Okno możliwości na pozycję lidera cyfrowego",
          "resources": "3 miesiące, inwestycja ~200k PLN"
        }
      ],
      "medium_term": [
        {
          "action": "Analiza opcji strategicznych (organic vs M&A vs partnership)",
          "rationale": "Konieczność przyspieszenia wzrostu dla domknięcia luki",
          "resources": "6 miesięcy, potencjalnie doradca M&A"
        }
      ]
    },
    
    "questions_for_further_research": [
      "Jaka jest defensibility przewagi kosztowej FADO?",
      "Czy istnieją cele akwizycyjne pasujące do strategii?",
      "Jakie są bariery wejścia dla zagranicznych graczy?"
    ]
  }
}
```
```

---

## 3. FRAMEWORK APPLIER AGENT

```markdown
# FRAMEWORK APPLICATION - Task Prompt

## ZADANIE
Zastosuj odpowiednie frameworki strategiczne do zebranych danych.

## DOSTĘPNE FRAMEWORKI

### Analiza Firmy
- SWOT Analysis
- Business Model Canvas
- Value Chain Analysis

### Analiza Konkurencji
- Porter's Five Forces
- Competitive Positioning Map
- Strategic Group Analysis

### Analiza Rynku
- PESTLE Analysis
- Market Attractiveness Matrix
- Ansoff Matrix

### Analiza Portfolio
- BCG Matrix
- GE-McKinsey Matrix

## PROCEDURA APLIKACJI

### Krok 1: Wybór Frameworka
```
Na podstawie:
- Typu analizy (firma/rynek/konkurencja)
- Pytania użytkownika
- Dostępnych danych
- Głębokości analizy
```

### Krok 2: Mapowanie Danych
```
Dla każdego elementu frameworka:
1. Zidentyfikuj relevantne dane
2. Przypisz do odpowiednich kategorii
3. Oznacz braki danych
```

### Krok 3: Analiza
```
1. Wypełnij framework danymi
2. Zidentyfikuj wzorce
3. Wyciągnij wnioski
4. Sformułuj rekomendacje
```

## PRZYKŁAD: SWOT APPLICATION

### Input Data
```json
{
  "company_profile": {...},
  "financial_data": {...},
  "competitor_benchmark": {...},
  "market_trends": {...}
}
```

### Output

```json
{
  "framework_application": {
    "framework": "SWOT Analysis",
    "subject": "FADO Sp. z o.o.",
    "analysis_date": "2025-01-13",
    
    "swot_matrix": {
      "strengths": [
        {
          "factor": "Wysoka rentowność",
          "evidence": "Net margin 7.1% vs industry 5.5%",
          "source": "financial_analysis",
          "impact": "high",
          "sustainability": "medium-high"
        },
        {
          "factor": "Obecność e-commerce",
          "evidence": "Działający sklep online, konkurencja w tyle",
          "source": "digital_presence_analysis",
          "impact": "medium",
          "sustainability": "medium"
        },
        {
          "factor": "Doświadczony zespół",
          "evidence": "Średni staż w branży >15 lat",
          "source": "key_people_analysis",
          "impact": "medium",
          "sustainability": "high"
        },
        {
          "factor": "Elastyczność produkcji",
          "evidence": "Customizacja produktów, krótkie serie",
          "source": "company_profile",
          "impact": "medium",
          "sustainability": "high"
        }
      ],
      
      "weaknesses": [
        {
          "factor": "Mniejsza skala vs lider",
          "evidence": "Revenue 50M vs ZETKAMA 120M",
          "source": "benchmark_analysis",
          "impact": "high",
          "improvability": "medium"
        },
        {
          "factor": "Ograniczony zasięg geograficzny",
          "evidence": "5 krajów vs lider 12",
          "source": "benchmark_analysis",
          "impact": "medium",
          "improvability": "high"
        },
        {
          "factor": "Niższa rozpoznawalność marki",
          "evidence": "SOV 18% vs konkurenci 22-25%",
          "source": "share_of_voice",
          "impact": "medium",
          "improvability": "high"
        }
      ],
      
      "opportunities": [
        {
          "factor": "Digitalizacja B2B",
          "evidence": "Rosnące oczekiwania klientów, słaba konkurencja",
          "source": "market_trends",
          "potential": "high",
          "timeline": "2-3 lata",
          "investment_required": "medium"
        },
        {
          "factor": "Ekspansja eksportowa",
          "evidence": "Rosnący rynek EU, dobre relacje cena/jakość",
          "source": "market_analysis",
          "potential": "high",
          "timeline": "3-5 lat",
          "investment_required": "high"
        },
        {
          "factor": "Konsolidacja rynku",
          "evidence": "Fragmentaryczny rynek, możliwe przejęcia",
          "source": "competitive_landscape",
          "potential": "medium",
          "timeline": "1-3 lata",
          "investment_required": "high"
        }
      ],
      
      "threats": [
        {
          "factor": "Rosnąca konkurencja zagraniczna",
          "evidence": "Danfoss, Siemens zwiększają aktywność",
          "source": "competitor_mapping",
          "probability": "high",
          "timeline": "2-4 lata",
          "impact": "high"
        },
        {
          "factor": "Presja cenowa z Azji",
          "evidence": "Rosnący import tanich zaworów",
          "source": "market_trends",
          "probability": "high",
          "timeline": "ongoing",
          "impact": "medium"
        },
        {
          "factor": "Potencjalna konsolidacja przez konkurenta",
          "evidence": "ZETKAMA z nowym CEO od M&A",
          "source": "strategic_moves",
          "probability": "medium",
          "timeline": "1-2 lata",
          "impact": "high"
        }
      ]
    },
    
    "strategic_implications": {
      "so_strategies": [
        {
          "name": "Digital Leadership",
          "leverage": "E-commerce capability + Customer expectation trend",
          "action": "Agresywna inwestycja w digital customer experience"
        },
        {
          "name": "Premium Export",
          "leverage": "Profitability + EU market growth",
          "action": "Selektywna ekspansja na rynki o wysokich marżach"
        }
      ],
      "wo_strategies": [
        {
          "name": "Scale through Partnership",
          "overcome": "Limited scale",
          "using": "Konsolidacja/partnerstwo",
          "action": "Identyfikacja celów M&A lub partnerów strategicznych"
        }
      ],
      "st_strategies": [
        {
          "name": "Differentiation Defense",
          "use": "Elastyczność, customizacja",
          "against": "Foreign competition + Price pressure",
          "action": "Wzmocnienie value proposition dla segmentu premium"
        }
      ],
      "wt_strategies": [
        {
          "name": "Strategic Options Review",
          "address": "Scale limitation + Consolidation threat",
          "action": "Przygotowanie scenariuszy: grow, partner, or exit"
        }
      ]
    },
    
    "priority_actions": [
      {
        "priority": 1,
        "action": "Wzmocnienie digital competitive advantage",
        "rationale": "Quick win, builds on strength, addresses opportunity"
      },
      {
        "priority": 2,
        "action": "Strategic options analysis",
        "rationale": "Proactive response to consolidation threat"
      },
      {
        "priority": 3,
        "action": "Export market selection",
        "rationale": "Growth opportunity, leverage strengths"
      }
    ]
  }
}
```
```

---

## 4. REPORT COMPOSER AGENT

```markdown
# REPORT COMPOSITION - Task Prompt

## ZADANIE
Skomponuj spójny raport końcowy z zebranych analiz.

## STRUKTURY RAPORTÓW

### Executive Summary (Quick)
```
- Kluczowe wnioski (3-5 bullet points)
- Najważniejsze liczby
- Rekomendowany next step
Długość: 1 strona
```

### Company Profile Report
```
1. Executive Summary
2. Company Overview
3. Financial Highlights
4. Ownership Structure
5. Digital Presence
6. Key People
7. Recent News
8. Sources & Confidence
Długość: 5-10 stron
```

### Competitive Analysis Report
```
1. Executive Summary
2. Subject Company Overview
3. Competitive Landscape
4. Detailed Competitor Profiles
5. Benchmarking Results
6. SWOT Analysis
7. Strategic Implications
8. Recommended Actions
9. Appendix: Data & Sources
Długość: 15-25 stron
```

### Full Market Research Report
```
1. Executive Summary
2. Objectives & Methodology
3. Market Overview
   - Size & Growth
   - Segmentation
   - Value Chain
4. Competitive Landscape
   - Key Players
   - Market Shares
   - Positioning
5. Trend Analysis
   - Drivers & Restraints
   - Technology Trends
   - Regulatory Environment
6. Company Deep Dive (if applicable)
7. Strategic Frameworks
8. Opportunities & Threats
9. Recommendations
10. Appendices
Długość: 30-50 stron
```

## ZASADY KOMPOZYCJI

### Struktura Narracyjna
```
1. Start with "so what" (executive summary)
2. Provide context (background)
3. Present findings (data & analysis)
4. Derive implications (insights)
5. End with actions (recommendations)
```

### Tone & Style
```
- Profesjonalny ale przystępny
- Bezpośredni (unikaj żargonu)
- Oparty na danych (cytuj źródła)
- Zbalansowany (przedstaw różne perspektywy)
- Actionable (konkretne rekomendacje)
```

### Elementy Wizualne
```
- Key metrics w callout boxes
- Tabele dla porównań
- Wykresy dla trendów
- Mapy dla geografii
- Timelines dla historii
```

## FORMAT WYJŚCIOWY

```json
{
  "report": {
    "metadata": {
      "title": "Analiza Konkurencyjna - FADO Sp. z o.o.",
      "type": "competitive_analysis",
      "date": "2025-01-13",
      "version": "1.0",
      "confidentiality": "client_confidential"
    },
    
    "sections": [
      {
        "id": "exec_summary",
        "title": "Podsumowanie Wykonawcze",
        "content_type": "structured",
        "content": {
          "headline": "FADO - solidna pozycja #2 z potencjałem wzrostu",
          "key_findings": [
            "FADO plasuje się jako #2 na rynku z score 6.65/10",
            "Przewaga konkurencyjna: rentowność i digital",
            "Główna luka: skala i zasięg geograficzny"
          ],
          "key_metrics": {
            "benchmark_score": "6.65/10 (#2 of 4)",
            "revenue_rank": "#3 of 4",
            "profitability_rank": "#1 of 4",
            "digital_rank": "#2 of 4"
          },
          "recommended_actions": [
            "Wzmocnić przewagę cyfrową",
            "Rozważyć opcje przyspieszenia wzrostu",
            "Monitorować aktywność M&A konkurentów"
          ]
        }
      },
      {
        "id": "company_overview",
        "title": "1. Profil FADO Sp. z o.o.",
        "content_type": "markdown",
        "content": "## 1. Profil FADO Sp. z o.o.\n\n### 1.1 Dane podstawowe\n\n| Parametr | Wartość |\n|----------|--------|\n| Nazwa | FADO Sp. z o.o. |\n..."
      },
      {
        "id": "competitive_landscape",
        "title": "2. Krajobraz Konkurencyjny",
        "content_type": "markdown",
        "content": "..."
      }
    ],
    
    "visualizations": [
      {
        "id": "viz_001",
        "type": "radar_chart",
        "title": "Porównanie Konkurencyjne",
        "data": {...},
        "placement": "section:benchmark_results"
      },
      {
        "id": "viz_002",
        "type": "bar_chart",
        "title": "Przychody vs Konkurencja",
        "data": {...}
      }
    ],
    
    "sources": {
      "primary": [
        {"name": "KRS", "accessed": "2025-01-13", "reliability": "high"},
        {"name": "Sprawozdania finansowe", "period": "2021-2023", "reliability": "high"}
      ],
      "secondary": [
        {"name": "SimilarWeb", "accessed": "2025-01-10", "reliability": "medium"},
        {"name": "LinkedIn", "accessed": "2025-01-12", "reliability": "medium"}
      ],
      "limitations": [
        "Brak danych finansowych za 2024",
        "Estymacje udziałów rynkowych"
      ]
    },
    
    "export_formats": {
      "pdf": true,
      "docx": true,
      "pptx": true,
      "html": true
    }
  }
}
```

## TEMPLATY EKSPORTU

### DOCX Template Structure
```
[Cover Page]
[Table of Contents]
[Executive Summary - 1 page]
[Main Content - sections]
[Appendices]
[Sources & Methodology]
[Disclaimer]
```

### PPTX Template Structure
```
Slide 1: Title
Slide 2: Executive Summary
Slide 3: Key Metrics Dashboard
Slides 4-N: Main Content (1 topic per slide)
Slide N+1: SWOT Matrix
Slide N+2: Recommendations
Slide N+3: Next Steps
Slide N+4: Q&A / Contact
```
```

---

*Następny dokument: 08_FRAMEWORKS_STRATEGIC.md*
