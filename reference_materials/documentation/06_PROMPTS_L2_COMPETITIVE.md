# 06. Prompty Level 2 - Competitive Intelligence

## Przegląd

Agenci wywiadu konkurencyjnego:
1. **Competitor Mapping Agent** - identyfikacja konkurentów
2. **Benchmarking Agent** - porównania wielowymiarowe
3. **Share of Voice Agent** - udział w dyskusji/widoczność
4. **Pricing Intelligence Agent** - wywiad cenowy
5. **Strategic Moves Agent** - monitorowanie ruchów konkurencji

---

## 1. COMPETITOR MAPPING AGENT

```markdown
# COMPETITOR MAPPING - Task Prompt

## ZADANIE
Zidentyfikuj i skategoryzuj konkurentów firmy, tworząc mapę konkurencyjną.

## TYPY KONKURENTÓW

### Bezpośredni (Direct)
Firmy oferujące te same/bardzo podobne produkty/usługi do tych samych klientów.
- Ten sam segment
- Ta sama geografia
- Podobna oferta

### Pośredni (Indirect)
Firmy oferujące alternatywne rozwiązania tego samego problemu.
- Substytucyjne produkty
- Inne podejście do tego samego need'u

### Potencjalni (Potential)
Firmy mogące wejść na rynek w przyszłości.
- Gracze z sąsiednich rynków
- Startupy w branży
- Międzynarodowi gracze planujący ekspansję

### Aspiracyjni (Aspirational)
Liderzy rynkowi, benchmark dla rozwoju.
- Best-in-class w branży
- Globalni liderzy

## PROCEDURA IDENTYFIKACJI

### Krok 1: Analiza Kontekstu
```
1. Określ główne produkty/usługi firmy
2. Zidentyfikuj segment klientów
3. Określ geografię działania
4. Wylistuj kody PKD
```

### Krok 2: Wyszukiwanie Konkurentów
```
Źródła:
1. Web Search: "[produkt] + [lokalizacja] + producent/dostawca"
2. KRS: Firmy z tym samym PKD w regionie
3. LinkedIn: "Similar companies"
4. SimilarWeb: "Competitors" dla strony firmowej
5. Industry reports: wymienieni gracze
6. Katalogi branżowe: np. Panorama Firm, PKT.pl
```

### Krok 3: Kategoryzacja
```
Dla każdego znalezionego konkurenta określ:
- Typ: direct/indirect/potential/aspirational
- Poziom zagrożenia: high/medium/low
- Nakładanie się: % overlapping w ofercie
- Skala: większy/podobny/mniejszy
```

### Krok 4: Priorytetyzacja
```
TOP konkurenci do głębszej analizy (max 5-7):
1. Bezpośredni + wysokie zagrożenie
2. Bezpośredni + podobna skala
3. Pośredni + dynamiczny wzrost
```

## FORMAT WYJŚCIOWY

```json
{
  "competitor_mapping": {
    "subject_company": {
      "name": "FADO Sp. z o.o.",
      "industry": "Armatura przemysłowa",
      "main_products": ["Zawory kulowe", "Armatura do instalacji"],
      "geography": "Polska",
      "target_segment": "B2B przemysł"
    },
    
    "search_methodology": {
      "sources_used": [
        "Web search (Google)",
        "KRS database (PKD 28.14)",
        "SimilarWeb competitors",
        "LinkedIn similar companies",
        "Industry portal plastech.pl"
      ],
      "search_queries": [
        "producent armatury przemysłowej Polska",
        "zawory kulowe producent",
        "armatura instalacyjna hurtownia"
      ],
      "competitors_found": 18,
      "competitors_analyzed": 8
    },
    
    "competitor_categories": {
      "direct": [
        {
          "rank": 1,
          "name": "POLNA S.A.",
          "location": "Przemyśl",
          "website": "polna.com.pl",
          "krs": "0000012345",
          "overlap_percent": 85,
          "threat_level": "high",
          "estimated_revenue": "80M PLN",
          "employees": "300-500",
          "key_products": ["Zawory regulacyjne", "Armatura przemysłowa"],
          "strengths": ["Duża skala", "Marka rozpoznawalna"],
          "weaknesses": ["Przestarzała technologia", "Słaba obecność online"],
          "notes": "Główny konkurent w segmencie przemysłowym"
        },
        {
          "rank": 2,
          "name": "ARMAGOR Sp. z o.o.",
          "location": "Gorzów Wielkopolski",
          "website": "armagor.pl",
          "overlap_percent": 75,
          "threat_level": "high",
          "estimated_revenue": "45M PLN",
          "employees": "100-200",
          "key_products": ["Zawory kulowe", "Przepustnice"],
          "strengths": ["Innowacyjność", "Szybka dostawa"],
          "weaknesses": ["Mniejsza skala", "Ograniczona dystrybucja"]
        }
      ],
      
      "indirect": [
        {
          "name": "WIKA Polska",
          "type": "indirect",
          "relationship": "Komplementarny - pomiary ciśnienia",
          "overlap_percent": 25,
          "threat_level": "low",
          "notes": "Potencjalny partner lub konkurent przy rozszerzeniu oferty"
        }
      ],
      
      "potential": [
        {
          "name": "Danfoss (DK)",
          "type": "potential",
          "current_presence": "Ograniczona w Polsce",
          "entry_likelihood": "medium",
          "threat_timeline": "2-3 lata",
          "trigger_events": ["Akwizycja lokalnego gracza", "Budowa fabryki"],
          "notes": "Globalny gracz, obserwować aktywność M&A"
        }
      ],
      
      "aspirational": [
        {
          "name": "Siemens AG",
          "type": "aspirational",
          "why": "Best-in-class w automatyzacji przemysłowej",
          "learnings": ["Digital integration", "Service model", "Brand building"]
        }
      ]
    },
    
    "competitive_landscape_summary": {
      "market_structure": "Fragmentaryczny z kilkoma dużymi graczami",
      "concentration": {
        "top_3_share": "35%",
        "top_10_share": "55%"
      },
      "competition_intensity": "high",
      "key_battlegrounds": [
        "Cena w segmencie commodity",
        "Jakość i certyfikaty w premium",
        "Dostępność i czas dostawy"
      ],
      "market_gaps": [
        "Brak silnego gracza w e-commerce B2B",
        "Niedostateczna obsługa małych firm"
      ]
    },
    
    "competitor_matrix": {
      "dimensions": ["Revenue", "Growth", "Digital Presence", "Innovation"],
      "data": [
        {"company": "FADO", "revenue": 6, "growth": 7, "digital": 6, "innovation": 7},
        {"company": "POLNA", "revenue": 8, "growth": 4, "digital": 4, "innovation": 5},
        {"company": "ARMAGOR", "revenue": 5, "growth": 8, "digital": 7, "innovation": 8}
      ]
    },
    
    "recommendations": {
      "monitor_closely": ["POLNA S.A.", "ARMAGOR Sp. z o.o."],
      "watch": ["Danfoss", "Emerson"],
      "potential_partners": ["WIKA Polska"],
      "deep_dive_suggested": ["POLNA S.A.", "ARMAGOR Sp. z o.o."]
    },
    
    "metadata": {
      "analysis_date": "2025-01-13",
      "data_freshness": "mixed (1-6 months)",
      "confidence": "medium-high",
      "limitations": [
        "Brak dokładnych danych finansowych dla niektórych firm",
        "Estymacje udziałów rynkowych"
      ]
    }
  }
}
```

## WIZUALIZACJE DO WYGENEROWANIA

1. **Mapa konkurencji** (2x2 matrix)
   - Oś X: Nakładanie się oferty
   - Oś Y: Poziom zagrożenia

2. **Strategic Group Map**
   - Oś X: Zakres oferty (wąski → szeroki)
   - Oś Y: Pozycja cenowa (economy → premium)

3. **Competitor Radar**
   - Wielokątny wykres porównawczy
```

---

## 2. BENCHMARKING AGENT

```markdown
# COMPETITIVE BENCHMARKING - Task Prompt

## ZADANIE
Przeprowadź wielowymiarowe porównanie firmy z konkurentami.

## WYMIARY BENCHMARKINGU

### 1. Profil Podstawowy
| Metryka | Opis |
|---------|------|
| Przychody | Roczne obroty |
| Pracownicy | Liczba zatrudnionych |
| Lokalizacje | Siedziby, oddziały |
| Historia | Lata na rynku |
| Forma prawna | Sp. z o.o., S.A., etc. |

### 2. Oferta Produktowa
| Metryka | Opis |
|---------|------|
| Szerokość | Liczba kategorii |
| Głębokość | Warianty w kategorii |
| Innowacyjność | Nowe produkty/rok |
| Jakość | Certyfikaty, standardy |
| Customizacja | Możliwość personalizacji |

### 3. Obecność Rynkowa
| Metryka | Opis |
|---------|------|
| Zasięg geograficzny | Regiony/kraje |
| Kanały dystrybucji | Direct/Distributor/Online |
| Baza klientów | Estymata liczby |
| Market share | Udział w rynku |
| Brand awareness | Rozpoznawalność |

### 4. Siła Cyfrowa
| Metryka | Opis |
|---------|------|
| Website traffic | Miesięczne wizyty |
| SEO position | Pozycje kluczowych fraz |
| Social following | Followers łącznie |
| E-commerce | Sprzedaż online |
| Content marketing | Blog, materiały |

### 5. Siła Finansowa
| Metryka | Opis |
|---------|------|
| Rentowność | Net margin % |
| Wzrost | Revenue CAGR |
| Płynność | Current ratio |
| Zadłużenie | Debt ratio |
| Kapitał | Equity/Assets |

## METODOLOGIA SCORINGU

### Skala 1-10
```
1-2: Znacząco poniżej rynku
3-4: Poniżej średniej
5-6: Średnia rynkowa
7-8: Powyżej średniej
9-10: Best-in-class
```

### Wagi Domyślne
```
Profil podstawowy: 15%
Oferta produktowa: 25%
Obecność rynkowa: 25%
Siła cyfrowa: 15%
Siła finansowa: 20%
```

## FORMAT WYJŚCIOWY

```json
{
  "competitive_benchmark": {
    "subject": "FADO Sp. z o.o.",
    "competitors": ["POLNA S.A.", "ARMAGOR Sp. z o.o.", "ZETKAMA S.A."],
    "analysis_date": "2025-01-13",
    
    "detailed_comparison": {
      "basic_profile": {
        "metrics": ["Revenue (M PLN)", "Employees", "Years in business", "Locations"],
        "FADO": [50, 250, 30, 2],
        "POLNA": [80, 400, 55, 3],
        "ARMAGOR": [45, 150, 18, 1],
        "ZETKAMA": [120, 600, 40, 5]
      },
      
      "product_offering": {
        "metrics": ["Product lines", "SKUs", "New products/year", "Certifications", "Custom options"],
        "FADO": [8, 1200, 15, 5, "High"],
        "POLNA": [12, 2500, 8, 7, "Medium"],
        "ARMAGOR": [6, 800, 20, 4, "High"],
        "ZETKAMA": [15, 3500, 12, 8, "Low"]
      },
      
      "market_presence": {
        "metrics": ["Countries", "Distribution channels", "Est. customers", "Market share %"],
        "FADO": [5, 3, 2000, 8],
        "POLNA": [8, 2, 3500, 12],
        "ARMAGOR": [3, 3, 1200, 6],
        "ZETKAMA": [12, 3, 5000, 15]
      },
      
      "digital_strength": {
        "metrics": ["Monthly visits", "Domain Authority", "LinkedIn followers", "E-commerce"],
        "FADO": [45000, 35, 2500, "Yes"],
        "POLNA": [28000, 38, 1800, "No"],
        "ARMAGOR": [32000, 32, 3200, "Yes"],
        "ZETKAMA": [55000, 42, 4500, "Partial"]
      },
      
      "financial_strength": {
        "metrics": ["Net margin %", "Revenue CAGR 3Y", "Current ratio", "Debt ratio %"],
        "FADO": [7.1, 8.5, 2.0, 46],
        "POLNA": [5.2, 3.2, 1.8, 52],
        "ARMAGOR": [8.5, 12.0, 1.5, 58],
        "ZETKAMA": [6.8, 6.5, 2.2, 42]
      }
    },
    
    "scoring": {
      "dimensions": ["Basic Profile", "Product Offering", "Market Presence", "Digital Strength", "Financial Strength"],
      "weights": [0.15, 0.25, 0.25, 0.15, 0.20],
      
      "scores": {
        "FADO": {
          "basic_profile": 6,
          "product_offering": 7,
          "market_presence": 6,
          "digital_strength": 7,
          "financial_strength": 7,
          "weighted_total": 6.65
        },
        "POLNA": {
          "basic_profile": 8,
          "product_offering": 7,
          "market_presence": 7,
          "digital_strength": 5,
          "financial_strength": 5,
          "weighted_total": 6.45
        },
        "ARMAGOR": {
          "basic_profile": 5,
          "product_offering": 7,
          "market_presence": 5,
          "digital_strength": 7,
          "financial_strength": 6,
          "weighted_total": 6.00
        },
        "ZETKAMA": {
          "basic_profile": 9,
          "product_offering": 8,
          "market_presence": 8,
          "digital_strength": 7,
          "financial_strength": 7,
          "weighted_total": 7.70
        }
      },
      
      "ranking": [
        {"rank": 1, "company": "ZETKAMA", "score": 7.70},
        {"rank": 2, "company": "FADO", "score": 6.65},
        {"rank": 3, "company": "POLNA", "score": 6.45},
        {"rank": 4, "company": "ARMAGOR", "score": 6.00}
      ]
    },
    
    "gap_analysis": {
      "FADO_vs_leader": {
        "leader": "ZETKAMA",
        "gaps": [
          {
            "dimension": "Basic Profile",
            "gap": -3,
            "specifics": "Mniejsza skala, mniej lokalizacji",
            "closeable": "medium-term (3-5 years)"
          },
          {
            "dimension": "Market Presence",
            "gap": -2,
            "specifics": "Mniejszy zasięg geograficzny",
            "closeable": "medium-term"
          }
        ],
        "advantages": [
          {
            "dimension": "Digital Strength",
            "advantage": 0,
            "specifics": "Porównywalna siła cyfrowa"
          }
        ]
      }
    },
    
    "competitive_advantages": {
      "FADO": [
        "Dobra rentowność (najwyższa w grupie)",
        "Silna customizacja",
        "E-commerce aktywny"
      ],
      "vs_POLNA": [
        "Lepsza siła cyfrowa",
        "Wyższa rentowność",
        "Szybszy wzrost"
      ],
      "vs_ARMAGOR": [
        "Większa skala",
        "Więcej certyfikatów",
        "Stabilniejsze finanse"
      ]
    },
    
    "strategic_implications": [
      "FADO plasuje się jako solidny #2 w grupie",
      "Przewaga konkurencyjna w digitalu i rentowności",
      "Główna luka: skala i zasięg geograficzny",
      "Potencjał: ekspansja zagraniczna, M&A"
    ],
    
    "radar_chart_data": {
      "labels": ["Profile", "Product", "Market", "Digital", "Financial"],
      "datasets": [
        {"label": "FADO", "data": [6, 7, 6, 7, 7]},
        {"label": "POLNA", "data": [8, 7, 7, 5, 5]},
        {"label": "ARMAGOR", "data": [5, 7, 5, 7, 6]},
        {"label": "ZETKAMA", "data": [9, 8, 8, 7, 7]}
      ]
    }
  }
}
```
```

---

## 3. SHARE OF VOICE AGENT

```markdown
# SHARE OF VOICE ANALYSIS - Task Prompt

## ZADANIE
Zmierz udział firmy w dyskusji branżowej vs konkurencja.

## METRYKI SOV

### Online Share of Voice
- Wzmianki w mediach
- Pozycje SEO
- Social media mentions
- Backlinks

### Offline Share of Voice
- Udział w targach
- Sponsoringi
- Publikacje branżowe
- Wypowiedzi ekspertów

## ŹRÓDŁA DANYCH

1. **Google Alerts** - wzmianki online
2. **Mention/Brand24** - social listening
3. **Ahrefs/SEMrush** - SEO share
4. **News aggregators** - media mentions

## FORMAT WYJŚCIOWY

```json
{
  "share_of_voice": {
    "analysis_period": "ostatnie 90 dni",
    "market": "Armatura przemysłowa Polska",
    
    "overall_sov": {
      "FADO": 18,
      "POLNA": 25,
      "ARMAGOR": 12,
      "ZETKAMA": 22,
      "Others": 23
    },
    
    "sov_by_channel": {
      "organic_search": {
        "methodology": "Top 50 keywords visibility",
        "FADO": 15,
        "POLNA": 22,
        "ZETKAMA": 28
      },
      "news_media": {
        "methodology": "Article mentions count",
        "FADO": 8,
        "POLNA": 15,
        "ZETKAMA": 12
      },
      "social_media": {
        "methodology": "Mentions + engagement",
        "FADO": 22,
        "POLNA": 10,
        "ARMAGOR": 25
      },
      "industry_portals": {
        "methodology": "Mentions on key portals",
        "FADO": 12,
        "POLNA": 18,
        "ZETKAMA": 20
      }
    },
    
    "sentiment_breakdown": {
      "FADO": {"positive": 65, "neutral": 30, "negative": 5},
      "POLNA": {"positive": 45, "neutral": 45, "negative": 10},
      "ARMAGOR": {"positive": 70, "neutral": 25, "negative": 5}
    },
    
    "trending_topics": [
      {"topic": "Automatyzacja", "FADO_mentions": 5, "competitor_avg": 3},
      {"topic": "Jakość", "FADO_mentions": 12, "competitor_avg": 8}
    ],
    
    "recommendations": [
      "Zwiększyć obecność w mediach branżowych",
      "Wzmocnić SEO dla kluczowych fraz",
      "Utrzymać przewagę w social media"
    ]
  }
}
```
```

---

## 4. PRICING INTELLIGENCE AGENT

```markdown
# PRICING INTELLIGENCE - Task Prompt

## ZADANIE
Zbierz i przeanalizuj informacje cenowe konkurencji.

## ŹRÓDŁA CEN

1. **Strony internetowe** - cenniki publiczne
2. **E-commerce** - ceny produktów
3. **Zapytania ofertowe** - mystery shopping
4. **Dystrybutorzy** - ceny półkowe
5. **Przetargi publiczne** - oferty archiwalne

## ANALIZA

### Poziomy Cenowe
- Premium tier
- Mid-market
- Economy

### Struktura Cen
- Cena bazowa
- Rabaty wolumenowe
- Warunki płatności
- Koszty dostawy

## FORMAT WYJŚCIOWY

```json
{
  "pricing_intelligence": {
    "category": "Zawory kulowe DN50",
    "analysis_date": "2025-01-13",
    
    "price_comparison": {
      "products": [
        {
          "company": "FADO",
          "product": "Zawór kulowy DN50 PN40",
          "list_price": 450,
          "currency": "PLN",
          "price_tier": "mid-market",
          "source": "website",
          "date_collected": "2025-01-10"
        },
        {
          "company": "POLNA",
          "product": "ZK50-40",
          "list_price": 520,
          "price_tier": "premium",
          "source": "distributor"
        },
        {
          "company": "ARMAGOR",
          "product": "BV-50-40",
          "list_price": 380,
          "price_tier": "economy",
          "source": "e-commerce"
        }
      ]
    },
    
    "price_positioning": {
      "market_average": 450,
      "FADO_vs_avg": "0%",
      "FADO_vs_premium": "-13%",
      "FADO_vs_economy": "+18%"
    },
    
    "discount_structures": {
      "FADO": {
        "volume_10plus": "5%",
        "volume_50plus": "12%",
        "annual_contract": "15%"
      },
      "POLNA": {
        "volume_10plus": "3%",
        "volume_50plus": "8%"
      }
    },
    
    "price_trends": {
      "last_12_months": "+4.5%",
      "competitor_avg_change": "+6.2%",
      "inflation": "+5.1%"
    },
    
    "strategic_insights": [
      "FADO pozycjonowane w mid-market",
      "Przestrzeń do podwyżki 5-8% bez utraty pozycji",
      "ARMAGOR agresywnie cenowo - war cenowa ryzykowna"
    ]
  }
}
```
```

---

## 5. STRATEGIC MOVES AGENT

```markdown
# STRATEGIC MOVES MONITORING - Task Prompt

## ZADANIE
Śledź i analizuj strategiczne ruchy konkurencji.

## TYPY RUCHÓW DO MONITOROWANIA

### Ekspansja
- Nowe rynki geograficzne
- Nowe segmenty klientów
- Nowe kanały dystrybucji

### Produkt
- Nowe produkty
- Zmiany w ofercie
- Innowacje technologiczne

### Korporacyjne
- Fuzje i przejęcia
- Partnerstwa strategiczne
- Zmiany w zarządzie

### Operacyjne
- Inwestycje w moce produkcyjne
- Zmiany cenowe
- Kampanie marketingowe

## ŹRÓDŁA INFORMACJI

1. **KRS** - zmiany w spółkach
2. **Komunikaty prasowe** - oficjalne ogłoszenia
3. **News** - artykuły branżowe
4. **LinkedIn** - zmiany kadrowe
5. **Job postings** - plany rekrutacyjne
6. **Przetargi** - aktywność sprzedażowa

## FORMAT WYJŚCIOWY

```json
{
  "strategic_moves": {
    "monitoring_period": "ostatnie 6 miesięcy",
    
    "moves_detected": [
      {
        "competitor": "POLNA S.A.",
        "move_type": "expansion",
        "date": "2024-11-15",
        "description": "Otwarcie biura handlowego w Niemczech",
        "source": "Komunikat prasowy",
        "significance": "high",
        "implications_for_subject": [
          "Potencjalna konkurencja na rynku DE",
          "Sygnał ambicji eksportowych"
        ],
        "recommended_response": "Monitor + rozważyć własną ekspansję"
      },
      {
        "competitor": "ARMAGOR",
        "move_type": "product",
        "date": "2024-12-01",
        "description": "Wprowadzenie linii zaworów smart z IoT",
        "source": "Strona internetowa",
        "significance": "high",
        "implications_for_subject": [
          "Innowacja w segmencie",
          "Potencjalna presja na modernizację oferty"
        ],
        "recommended_response": "Analiza produktu + R&D assessment"
      },
      {
        "competitor": "ZETKAMA",
        "move_type": "corporate",
        "date": "2025-01-05",
        "description": "Zmiana CEO - nowy prezes z doświadczeniem M&A",
        "source": "KRS + LinkedIn",
        "significance": "medium",
        "implications_for_subject": [
          "Możliwe przyspieszenie konsolidacji",
          "Obserwować aktywność akwizycyjną"
        ]
      }
    ],
    
    "signal_strength_summary": {
      "POLNA": {
        "expansion_signals": "strong",
        "innovation_signals": "weak",
        "consolidation_signals": "medium"
      },
      "ARMAGOR": {
        "expansion_signals": "medium",
        "innovation_signals": "strong",
        "consolidation_signals": "weak"
      },
      "ZETKAMA": {
        "expansion_signals": "medium",
        "innovation_signals": "medium",
        "consolidation_signals": "strong"
      }
    },
    
    "early_warning_indicators": [
      {
        "indicator": "POLNA job postings for DE sales",
        "signal": "Agresywna ekspansja na DE",
        "watch_level": "high"
      },
      {
        "indicator": "ZETKAMA due diligence activity",
        "signal": "Potencjalna akwizycja",
        "watch_level": "high"
      }
    ],
    
    "recommended_actions": [
      {
        "priority": 1,
        "action": "Głębsza analiza produktów IoT ARMAGOR",
        "timeline": "2 tygodnie"
      },
      {
        "priority": 2,
        "action": "Monitoring aktywności ZETKAMA M&A",
        "timeline": "ongoing"
      }
    ]
  }
}
```
```

---

*Następny dokument: 07_PROMPTS_L3_SYNTHESIS.md*
