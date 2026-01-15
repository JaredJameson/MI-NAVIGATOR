# 05. Prompty Level 2 - Market Intelligence

## Przegląd

Agenci analizy rynkowej:
1. **Market Sizing Agent** - wielkość rynku TAM/SAM/SOM
2. **Trend Analysis Agent** - trendy i prognozy
3. **Segmentation Agent** - segmentacja rynku
4. **Value Chain Agent** - łańcuch wartości
5. **Regulatory Agent** - otoczenie regulacyjne

---

## 1. MARKET SIZING AGENT

```markdown
# MARKET SIZING ANALYSIS - Task Prompt

## ZADANIE
Oszacuj wielkość rynku używając metodologii TAM/SAM/SOM z pełną 
transparentnością założeń i źródeł.

## DEFINICJE

**TAM (Total Addressable Market)**
Całkowity teoretyczny rynek - wszyscy potencjalni klienci globalnie/regionalnie 
gdyby nie było żadnych ograniczeń.

**SAM (Serviceable Addressable Market)**
Osiągalny rynek - część TAM którą firma może realnie obsłużyć 
uwzględniając geografię, segment, kanał dystrybucji.

**SOM (Serviceable Obtainable Market)**
Realistycznie osiągalny rynek w określonym horyzoncie czasowym 
przy obecnych zasobach i pozycji konkurencyjnej.

## METODOLOGIE ESTYMACJI

### 1. Top-Down Approach
```
Krok 1: Znajdź dane makro
- Raporty branżowe (Statista, IBISWorld, Euromonitor)
- Dane GUS/Eurostat
- Raporty izb branżowych

Krok 2: Zastosuj filtry
- Geografia: Świat → Europa → Polska → Region
- Segment: Cały rynek → B2B → Premium
- Produkt: Kategoria → Podkategoria

Krok 3: Ekstrapoluj
- Użyj współczynników (np. Polska = 2.5% EU)
- Uwzględnij lokalne specyfiki

PRZYKŁAD:
Rynek zaworów przemysłowych EU = €15B
Polska ≈ 2.5% EU PKB przemysłowego
TAM Polska = €15B × 2.5% = €375M
```

### 2. Bottom-Up Approach
```
Krok 1: Zidentyfikuj klientów
- Liczba firm w segmencie docelowym
- Dane GUS (liczba podmiotów wg PKD)

Krok 2: Oszacuj wartość klienta
- Średni budżet na kategorię
- Częstotliwość zakupów

Krok 3: Pomnóż
- TAM = Liczba klientów × Średnia wartość × Częstotliwość

PRZYKŁAD:
Firmy produkcyjne w Polsce: 45,000
Średni zakup armatury/rok: €5,000
TAM = 45,000 × €5,000 = €225M
```

### 3. Analogia Rynkowa
```
Krok 1: Znajdź porównywalny rynek
- Inny kraj o podobnej strukturze
- Pokrewna branża

Krok 2: Określ współczynniki
- Różnica w PKB per capita
- Różnica w uprzemysłowieniu
- Różnica w adopcji technologii

Krok 3: Przelicz
- Rynek A × Współczynnik = Estymata dla B

PRZYKŁAD:
Rynek UK = €500M
PKB per capita PL/UK = 0.45
Uprzemysłowienie PL/UK = 1.2
TAM PL = €500M × 0.45 × 1.2 = €270M
```

## ŹRÓDŁA DANYCH

### Darmowe
| Źródło | Dane | Wiarygodność |
|--------|------|--------------|
| GUS | Produkcja przemysłowa, PKD | Wysoka |
| Eurostat | Dane EU, porównania | Wysoka |
| PARP | Raporty sektorowe PL | Średnia |
| Izby branżowe | Dane członków | Średnia |
| Google Trends | Zainteresowanie | Niska |

### Płatne
| Źródło | Dane | Koszt |
|--------|------|-------|
| Statista | Raporty globalne | $$$ |
| IBISWorld | Industry reports | $$$$ |
| Euromonitor | Consumer markets | $$$$ |
| Grand View Research | Niche markets | $$$ |

## PROCEDURA

### Input
```json
{
  "market_definition": "Rynek armatury przemysłowej",
  "geography": "Polska",
  "segment": "B2B przemysł",
  "time_horizon": "2025-2028",
  "currency": "EUR"
}
```

### Krok 1: Research
```
1. Wyszukaj raporty branżowe
2. Sprawdź dane GUS/Eurostat
3. Znajdź benchmarki zagraniczne
4. Zbierz min. 3 źródła dla TAM
```

### Krok 2: Kalkulacja
```
1. Zastosuj 2+ metodologie
2. Porównaj wyniki
3. Uzasadnij różnice
4. Wybierz najbardziej wiarygodną estymację
```

### Krok 3: Dokumentacja
```
1. Wylistuj wszystkie założenia
2. Podaj źródła dla każdej liczby
3. Określ przedział ufności
4. Opisz ograniczenia
```

## FORMAT WYJŚCIOWY

```json
{
  "market_sizing": {
    "market_definition": {
      "name": "Rynek armatury przemysłowej",
      "scope": "Zawory, kurki, armatura do instalacji przemysłowych",
      "geography": "Polska",
      "base_year": 2024,
      "currency": "EUR"
    },
    
    "tam": {
      "value": 350000000,
      "range": {
        "low": 280000000,
        "high": 420000000
      },
      "methodology": "hybrid (top-down + bottom-up)",
      "calculation": {
        "top_down": {
          "eu_market": 14000000000,
          "poland_share": "2.5%",
          "result": 350000000
        },
        "bottom_up": {
          "target_companies": 38000,
          "avg_annual_spend": 8500,
          "result": 323000000
        },
        "reconciliation": "Przyjęto średnią ważoną, priorytet top-down"
      },
      "sources": [
        {
          "name": "Euromonitor Industrial Valves Report 2024",
          "data_point": "EU market size €14B",
          "reliability": "high"
        },
        {
          "name": "GUS - Podmioty wg PKD 28.14",
          "data_point": "38,000 firm produkcyjnych",
          "reliability": "high"
        }
      ],
      "confidence": "medium-high"
    },
    
    "sam": {
      "value": 180000000,
      "filters_applied": [
        {
          "filter": "B2B only (exclude retail)",
          "reduction": "15%"
        },
        {
          "filter": "Industrial segment (exclude residential)",
          "reduction": "25%"
        },
        {
          "filter": "Premium & mid-market (exclude budget)",
          "reduction": "20%"
        }
      ],
      "calculation": "TAM × 0.85 × 0.75 × 0.80 = €180M",
      "confidence": "medium"
    },
    
    "som": {
      "value": 12000000,
      "timeline": "3 years",
      "assumptions": [
        "Current market share: ~2%",
        "Achievable share with expansion: 6-7%",
        "Conservative estimate: 5%"
      ],
      "calculation": "SAM × 5% realistic penetration = €12M",
      "growth_path": {
        "year_1": 5000000,
        "year_2": 8000000,
        "year_3": 12000000
      },
      "confidence": "medium"
    },
    
    "growth_projections": {
      "historical_cagr": "4.2% (2019-2024)",
      "projected_cagr": "5.5% (2024-2029)",
      "drivers": [
        "Modernizacja przemysłu (Industry 4.0)",
        "Regulacje środowiskowe",
        "Infrastruktura energetyczna"
      ],
      "constraints": [
        "Spowolnienie gospodarcze",
        "Import z Azji",
        "Niedobór wykwalifikowanych kadr"
      ]
    },
    
    "market_forecast": {
      "2024": 350000000,
      "2025": 369000000,
      "2026": 389000000,
      "2027": 410000000,
      "2028": 433000000,
      "2029": 457000000
    },
    
    "methodology_notes": {
      "data_quality": "Dane oparte głównie na raportach branżowych i GUS",
      "limitations": [
        "Brak granularnych danych dla subsegmentów",
        "Estymacje importu/eksportu niepewne",
        "Rynek szarej strefy nie uwzględniony"
      ],
      "recommendations": [
        "Zweryfikować z danymi izby branżowej",
        "Przeprowadzić badanie pierwotne wśród dystrybutorów"
      ]
    },
    
    "metadata": {
      "analysis_date": "2025-01-13",
      "analyst_confidence": "medium-high",
      "next_update_recommended": "2025-07"
    }
  }
}
```

## KONTROLA JAKOŚCI

Przed zwróceniem, zweryfikuj:
- [ ] TAM > SAM > SOM (logiczna hierarchia)
- [ ] Źródła dla każdej kluczowej liczby
- [ ] Założenia są jawne i uzasadnione
- [ ] Przedziały ufności określone
- [ ] Metodologia jest transparentna
- [ ] Ograniczenia są opisane
```

---

## 2. TREND ANALYSIS AGENT

```markdown
# TREND ANALYSIS - Task Prompt

## ZADANIE
Zidentyfikuj i przeanalizuj trendy kształtujące rynek.

## KATEGORIE TRENDÓW

### 1. Trendy Technologiczne
- Nowe technologie produkcji
- Digitalizacja
- Automatyzacja
- Materiały/surowce

### 2. Trendy Rynkowe
- Zmiana preferencji klientów
- Nowe modele biznesowe
- Konsolidacja rynku
- Globalizacja/lokalizacja

### 3. Trendy Regulacyjne
- Nowe przepisy
- Standardy jakości
- Wymogi środowiskowe
- Polityka handlowa

### 4. Trendy Społeczne
- Zmiany demograficzne
- Zrównoważony rozwój
- Praca zdalna/hybrydowa
- CSR/ESG

## ŹRÓDŁA

1. **Raporty trendów** - McKinsey, BCG, Deloitte
2. **Publikacje branżowe** - trade journals
3. **Konferencje** - wystąpienia, keynotes
4. **Startupy** - na co idzie funding
5. **Patenty** - nowe technologie
6. **Google Trends** - zainteresowanie

## FORMAT WYJŚCIOWY

```json
{
  "trend_analysis": {
    "market": "Przetwórstwo tworzyw sztucznych",
    "analysis_period": "2025-2030",
    
    "macro_trends": [
      {
        "name": "Circular Economy",
        "category": "regulatory_social",
        "impact": "transformational",
        "timeline": "ongoing",
        "description": "Przejście na gospodarkę o obiegu zamkniętym...",
        "implications": [
          "Wzrost popytu na recyklaty",
          "Nowe wymogi projektowania produktów",
          "Systemy zwrotu opakowań"
        ],
        "opportunity_score": 8,
        "threat_score": 6,
        "evidence": [
          "EU Plastic Strategy 2030",
          "Wzrost cen virgin plastics o 40%"
        ]
      },
      {
        "name": "Industry 4.0 w produkcji",
        "category": "technological",
        "impact": "high",
        "timeline": "3-5 years",
        "description": "Automatyzacja i cyfryzacja procesów...",
        "implications": [...],
        "opportunity_score": 9,
        "threat_score": 4
      }
    ],
    
    "emerging_trends": [
      {
        "name": "Bioplastiki",
        "maturity": "early",
        "watch_indicators": [
          "Wolumen produkcji",
          "Koszty vs tradycyjne"
        ]
      }
    ],
    
    "declining_trends": [
      {
        "name": "Jednorazowe opakowania plastikowe",
        "reason": "Regulacje + presja społeczna",
        "timeline": "2-3 years"
      }
    ],
    
    "trend_matrix": {
      "headers": ["Trend", "Impact", "Probability", "Timeline", "Action"],
      "data": [
        ["Circular Economy", "High", "Certain", "Now", "Adapt"],
        ["Industry 4.0", "High", "High", "3Y", "Invest"],
        ["Bioplastiki", "Medium", "Medium", "5Y", "Monitor"]
      ]
    },
    
    "strategic_implications": [
      "Priorytet: inwestycje w recykling",
      "Rozważyć: partnerstwa technologiczne",
      "Monitorować: regulacje EU"
    ]
  }
}
```
```

---

## 3. SEGMENTATION AGENT

```markdown
# MARKET SEGMENTATION - Task Prompt

## ZADANIE
Podziel rynek na segmenty i scharakteryzuj każdy z nich.

## KRYTERIA SEGMENTACJI

### B2B Markets
- **Wielkość firmy** - mikro/małe/średnie/duże
- **Branża** - produkcja/budownictwo/energetyka
- **Geografia** - regiony, urbanizacja
- **Zastosowanie** - use case produktu
- **Kanał zakupu** - bezpośrednio/dystrybutor

### B2C Markets
- **Demografia** - wiek, płeć, dochód
- **Psychografia** - styl życia, wartości
- **Zachowania** - częstotliwość zakupu, lojalność
- **Geografia** - miasto/wieś, region

## FORMAT WYJŚCIOWY

```json
{
  "segmentation": {
    "market": "Armatura przemysłowa Polska",
    "segmentation_approach": "by industry + size",
    
    "segments": [
      {
        "name": "Przemysł ciężki",
        "size_eur": 120000000,
        "share_percent": 34,
        "growth_rate": "3%",
        "characteristics": {
          "typical_customer": "Duże zakłady produkcyjne",
          "purchase_drivers": ["Niezawodność", "Serwis", "Certyfikaty"],
          "price_sensitivity": "low",
          "purchase_cycle": "long-term contracts"
        },
        "key_players": ["Duże hurtownie", "Bezpośrednia sprzedaż"],
        "attractiveness_score": 8,
        "competition_intensity": "high"
      },
      {
        "name": "Instalatorzy/Wykonawcy",
        "size_eur": 85000000,
        "share_percent": 24,
        "growth_rate": "5%",
        "characteristics": {
          "typical_customer": "Firmy instalacyjne 5-50 osób",
          "purchase_drivers": ["Cena", "Dostępność", "Relacje"],
          "price_sensitivity": "high",
          "purchase_cycle": "project-based"
        },
        "attractiveness_score": 6,
        "competition_intensity": "very high"
      }
    ],
    
    "segment_map": {
      "axes": {
        "x": "Size (revenue potential)",
        "y": "Growth rate"
      },
      "positions": [
        {"segment": "Przemysł ciężki", "x": 0.8, "y": 0.3},
        {"segment": "Instalatorzy", "x": 0.6, "y": 0.5}
      ]
    },
    
    "white_spaces": [
      {
        "description": "Małe firmy produkcyjne - niedoobsłużone",
        "potential": "€25M",
        "barriers": "Rozproszenie, niskie marże"
      }
    ],
    
    "recommendations": {
      "focus_segments": ["Przemysł ciężki", "Energetyka"],
      "avoid_segments": ["DIY retail"],
      "watch_segments": ["Renewable energy installers"]
    }
  }
}
```
```

---

## 4. VALUE CHAIN AGENT

```markdown
# VALUE CHAIN ANALYSIS - Task Prompt

## ZADANIE
Zmapuj łańcuch wartości w branży i określ marże na każdym etapie.

## ELEMENTY ŁAŃCUCHA

### Typowy łańcuch B2B Industrial
```
Surowce → Przetwórstwo → Produkcja → Dystrybucja → Użytkownik końcowy
   ↓           ↓            ↓            ↓               ↓
 10-15%      20-30%       25-40%       15-25%           N/A
  marża       marża        marża        marża
```

## FORMAT WYJŚCIOWY

```json
{
  "value_chain": {
    "industry": "Armatura przemysłowa",
    
    "stages": [
      {
        "stage": 1,
        "name": "Surowce (metal, polimery)",
        "players": ["Huty", "Producenci granulatu"],
        "value_add": "10-15%",
        "gross_margin": "8-12%",
        "key_cost_drivers": ["Energia", "Surowce naturalne"],
        "consolidation": "high",
        "power": "medium"
      },
      {
        "stage": 2,
        "name": "Komponenty",
        "players": ["Odlewnie", "Producenci uszczelek"],
        "value_add": "15-20%",
        "gross_margin": "12-18%",
        "key_cost_drivers": ["Praca", "Narzędzia"],
        "consolidation": "medium",
        "power": "low"
      },
      {
        "stage": 3,
        "name": "Producenci armatury",
        "players": ["FADO", "Konkurenci"],
        "value_add": "25-35%",
        "gross_margin": "20-30%",
        "key_cost_drivers": ["Montaż", "QC", "R&D"],
        "consolidation": "medium",
        "power": "medium-high"
      },
      {
        "stage": 4,
        "name": "Dystrybucja",
        "players": ["Hurtownie", "Sieci instalacyjne"],
        "value_add": "15-25%",
        "gross_margin": "12-20%",
        "key_cost_drivers": ["Logistyka", "Zapasy", "Sprzedaż"],
        "consolidation": "low",
        "power": "medium"
      }
    ],
    
    "value_flow_diagram": {
      "total_end_value": 100,
      "distribution": {
        "raw_materials": 25,
        "components": 15,
        "manufacturing": 35,
        "distribution": 20,
        "end_user_surplus": 5
      }
    },
    
    "strategic_insights": {
      "highest_margin_stage": "Produkcja",
      "most_fragmented": "Dystrybucja",
      "integration_opportunities": [
        "Forward integration into distribution",
        "Backward integration into components"
      ],
      "disruption_risks": [
        "Direct-to-customer by manufacturers",
        "Platform aggregators"
      ]
    }
  }
}
```
```

---

## 5. REGULATORY AGENT

```markdown
# REGULATORY LANDSCAPE - Task Prompt

## ZADANIE
Zmapuj otoczenie regulacyjne wpływające na rynek/branżę.

## KATEGORIE REGULACJI

### EU Level
- Dyrektywy i rozporządzenia
- Standardy (EN, ISO)
- Green Deal, Fit for 55

### Krajowe (PL)
- Ustawy
- Rozporządzenia ministerialne
- Normy PN

### Branżowe
- Certyfikacje
- Standardy branżowe
- Best practices

## FORMAT WYJŚCIOWY

```json
{
  "regulatory_landscape": {
    "market": "Armatura przemysłowa, Polska",
    "analysis_date": "2025-01-13",
    
    "current_regulations": [
      {
        "name": "PED - Pressure Equipment Directive",
        "jurisdiction": "EU",
        "reference": "2014/68/EU",
        "impact": "high",
        "requirements": [
          "Certyfikacja CE dla urządzeń ciśnieniowych",
          "Dokumentacja techniczna",
          "Testy wytrzymałościowe"
        ],
        "compliance_cost": "medium",
        "affected_products": ["Zawory ciśnieniowe", "Zbiorniki"]
      },
      {
        "name": "REACH",
        "jurisdiction": "EU",
        "impact": "medium",
        "requirements": [
          "Rejestracja substancji chemicznych",
          "Brak substancji zakazanych"
        ]
      }
    ],
    
    "upcoming_changes": [
      {
        "name": "EU Ecodesign for Sustainable Products Regulation",
        "expected": "2025-2026",
        "impact": "high",
        "key_changes": [
          "Digital Product Passport",
          "Wymogi recyklowalności",
          "Ślad węglowy produktu"
        ],
        "preparation_needed": [
          "Systemy śledzenia komponentów",
          "LCA analysis",
          "Redesign produktów"
        ]
      }
    ],
    
    "certification_requirements": [
      {
        "name": "CE Marking",
        "mandatory": true,
        "cost": "€5,000-20,000 per product line"
      },
      {
        "name": "ISO 9001",
        "mandatory": false,
        "market_expectation": "high",
        "cost": "€10,000-30,000 annually"
      }
    ],
    
    "regulatory_risk_assessment": {
      "risk_level": "medium",
      "key_risks": [
        "Zaostrzenie wymogów środowiskowych",
        "Koszty certyfikacji nowych produktów"
      ],
      "opportunities": [
        "Bariery wejścia dla konkurentów",
        "Premium za certified products"
      ]
    },
    
    "recommendations": [
      "Monitorować prace nad Ecodesign Regulation",
      "Rozpocząć przygotowania do Digital Product Passport",
      "Rozważyć certyfikację ISO 14001 (środowiskową)"
    ]
  }
}
```
```

---

*Następny dokument: 06_PROMPTS_L2_COMPETITIVE.md*
