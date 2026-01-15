# 09. Frameworki Operacyjne

## Przegląd

Frameworki do analizy operacji, modeli biznesowych i propozycji wartości:
1. **Value Chain Analysis** - Łańcuch wartości firmy
2. **Business Model Canvas** - Model biznesowy
3. **Lean Canvas** - Canvas dla startupów
4. **Jobs to Be Done** - Analiza potrzeb klientów

---

## 1. VALUE CHAIN ANALYSIS (Porter)

```markdown
# VALUE CHAIN FRAMEWORK

## KIEDY STOSOWAĆ
- Identyfikacja źródeł przewagi konkurencyjnej
- Analiza kosztów i marż
- Optymalizacja procesów
- Outsourcing decisions
- Benchmarking operacyjny

## STRUKTURA ŁAŃCUCHA WARTOŚCI

### DZIAŁANIA PODSTAWOWE (Primary Activities)

#### 1. Logistyka Wewnętrzna (Inbound Logistics)
- Przyjmowanie surowców i materiałów
- Magazynowanie
- Zarządzanie zapasami
- Harmonogramowanie dostaw
- Zwroty do dostawców

Pytania diagnostyczne:
- Jak efektywny jest proces przyjęcia materiałów?
- Jaki jest poziom zapasów vs optymalne?
- Jak wyglądają relacje z dostawcami?

#### 2. Operacje (Operations)
- Procesy produkcyjne
- Montaż
- Pakowanie
- Utrzymanie ruchu
- Kontrola jakości
- Zarządzanie mocami produkcyjnymi

Pytania diagnostyczne:
- Jakie jest wykorzystanie mocy produkcyjnych?
- Jaki jest OEE (Overall Equipment Effectiveness)?
- Jak wygląda jakość (% braków)?

#### 3. Logistyka Zewnętrzna (Outbound Logistics)
- Magazynowanie wyrobów gotowych
- Dystrybucja
- Transport
- Realizacja zamówień
- Zarządzanie dostawami

Pytania diagnostyczne:
- Jaki jest czas realizacji zamówienia?
- Jaki jest % terminowych dostaw (OTIF)?
- Jakie są koszty logistyczne jako % przychodów?

#### 4. Marketing i Sprzedaż (Marketing & Sales)
- Reklama i promocja
- Zarządzanie cenami
- Zarządzanie kanałami
- Sprzedaż bezpośrednia
- Budowanie relacji z klientami

Pytania diagnostyczne:
- Jaki jest koszt pozyskania klienta (CAC)?
- Jak wygląda efektywność kanałów?
- Jakie są marże po rabatach?

#### 5. Serwis (Service)
- Wsparcie posprzedażowe
- Naprawy i gwarancje
- Szkolenia klientów
- Części zamienne
- Obsługa reklamacji

Pytania diagnostyczne:
- Jaki jest poziom satysfakcji klienta?
- Jaki jest koszt serwisu vs przychody serwisowe?
- Jak szybki jest czas reakcji?

### DZIAŁANIA WSPIERAJĄCE (Support Activities)

#### 1. Infrastruktura Firmy
- Zarządzanie ogólne
- Planowanie strategiczne
- Finanse i kontroling
- Prawo i compliance
- Zarządzanie jakością

#### 2. Zarządzanie Zasobami Ludzkimi
- Rekrutacja
- Szkolenia i rozwój
- Wynagrodzenia
- Kultura organizacyjna

#### 3. Rozwój Technologii
- R&D
- Automatyzacja procesów
- Rozwój produktów
- Doskonalenie procesów

#### 4. Zaopatrzenie
- Zakupy strategiczne
- Negocjacje z dostawcami
- Kwalifikacja dostawców
- Zarządzanie kontraktami

## FORMAT WYJŚCIOWY

```json
{
  "value_chain_analysis": {
    "company": "FADO Sp. z o.o.",
    "date": "2025-01-13",
    "industry_benchmark": "Armatura przemysłowa",
    
    "primary_activities": {
      "inbound_logistics": {
        "description": "Zakup i magazynowanie surowców (stal, komponenty)",
        "cost_percent_of_revenue": 8,
        "value_added_percent": 5,
        
        "key_processes": [
          {
            "process": "Zarządzanie zapasami",
            "performance": "Średnie - 45 dni rotacji",
            "benchmark": "35 dni",
            "improvement_potential": "high"
          },
          {
            "process": "Relacje z dostawcami",
            "performance": "Dobre - długoterminowe kontrakty",
            "competitive_advantage": "medium"
          }
        ],
        
        "strengths": ["Stabilni dostawcy", "Dobre warunki płatności"],
        "weaknesses": ["Zbyt wysokie zapasy", "Mała elastyczność"],
        "improvement_opportunities": [
          "Wdrożenie VMI z kluczowymi dostawcami",
          "Redukcja zapasów o 20%"
        ]
      },
      
      "operations": {
        "description": "Produkcja armatury - obróbka, montaż, testowanie",
        "cost_percent_of_revenue": 35,
        "value_added_percent": 40,
        
        "key_processes": [
          {
            "process": "Obróbka CNC",
            "performance": "Dobra - OEE 72%",
            "benchmark": "OEE 80%",
            "improvement_potential": "medium"
          },
          {
            "process": "Montaż",
            "performance": "Dobra - wysoka jakość",
            "competitive_advantage": "high"
          },
          {
            "process": "Kontrola jakości",
            "performance": "Bardzo dobra - 0.5% braków",
            "benchmark": "1%",
            "competitive_advantage": "high"
          }
        ],
        
        "strengths": [
          "Wysoka jakość produkcji",
          "Doświadczona kadra",
          "Nowoczesny park maszynowy"
        ],
        "weaknesses": [
          "Ograniczona automatyzacja montażu",
          "Przestoje na przezbrojenia"
        ],
        "improvement_opportunities": [
          "Automatyzacja montażu - ROI 18 mies.",
          "SMED dla szybszych przezbrojeń"
        ]
      },
      
      "outbound_logistics": {
        "description": "Magazynowanie, pakowanie, wysyłka do klientów",
        "cost_percent_of_revenue": 6,
        "value_added_percent": 3,
        
        "key_processes": [
          {
            "process": "Kompletacja zamówień",
            "performance": "Dobra - 99% accuracy",
            "competitive_advantage": "medium"
          },
          {
            "process": "Dostawa",
            "performance": "OTIF 94%",
            "benchmark": "OTIF 97%",
            "improvement_potential": "medium"
          }
        ],
        
        "strengths": ["Szeroka sieć dystrybucji", "Elastyczność dostaw"],
        "weaknesses": ["Koszty transportu rosnące", "Brak śledzenia przesyłek online"],
        "improvement_opportunities": [
          "Track & Trace dla klientów",
          "Optymalizacja tras"
        ]
      },
      
      "marketing_sales": {
        "description": "Sprzedaż B2B, marketing techniczny, zarządzanie klientami",
        "cost_percent_of_revenue": 12,
        "value_added_percent": 25,
        
        "key_processes": [
          {
            "process": "Sprzedaż techniczna",
            "performance": "Dobra - wysoka konwersja",
            "competitive_advantage": "high"
          },
          {
            "process": "Marketing digitalowy",
            "performance": "Słaba - niedoinwestowany",
            "improvement_potential": "high"
          },
          {
            "process": "Key Account Management",
            "performance": "Bardzo dobra - retencja 95%",
            "competitive_advantage": "high"
          }
        ],
        
        "strengths": [
          "Silne relacje z dystrybutorami",
          "Kompetentny zespół sprzedaży",
          "Wysoka retencja klientów"
        ],
        "weaknesses": [
          "Słaba obecność online",
          "Brak e-commerce B2B",
          "Ograniczony marketing"
        ],
        "improvement_opportunities": [
          "Platforma B2B e-commerce",
          "Content marketing techniczny",
          "Automation marketingu"
        ]
      },
      
      "service": {
        "description": "Wsparcie techniczne, serwis gwarancyjny, szkolenia",
        "cost_percent_of_revenue": 4,
        "value_added_percent": 8,
        
        "key_processes": [
          {
            "process": "Wsparcie techniczne",
            "performance": "Dobra - szybka reakcja",
            "competitive_advantage": "high"
          },
          {
            "process": "Szkolenia klientów",
            "performance": "Średnia - sporadyczne",
            "improvement_potential": "medium"
          }
        ],
        
        "strengths": ["Kompetentny zespół", "Szybki czas reakcji"],
        "weaknesses": ["Brak serwisu online", "Ograniczone części zamienne na miejscu"],
        "improvement_opportunities": [
          "Portal self-service",
          "Baza wiedzy online",
          "Regularny program szkoleń"
        ]
      }
    },
    
    "support_activities": {
      "infrastructure": {
        "description": "Zarządzanie, finanse, IT, prawo",
        "cost_percent_of_revenue": 8,
        "assessment": "Adekwatne do skali",
        "strengths": ["Stabilne zarządzanie", "Zdrowe finanse"],
        "weaknesses": ["Ograniczona digitalizacja", "Legacy IT systems"]
      },
      
      "human_resources": {
        "description": "HR, szkolenia, rekrutacja",
        "cost_percent_of_revenue": 3,
        "assessment": "Wymaga wzmocnienia",
        "strengths": ["Niska rotacja", "Doświadczenie"],
        "weaknesses": ["Starzejąca się kadra", "Trudności rekrutacyjne"],
        "improvement_opportunities": [
          "Employer branding",
          "Program sukcesji",
          "Akademia wewnętrzna"
        ]
      },
      
      "technology_development": {
        "description": "R&D, rozwój produktów, innowacje",
        "cost_percent_of_revenue": 4,
        "assessment": "Poniżej potencjału",
        "strengths": ["Know-how techniczne", "Elastyczność"],
        "weaknesses": ["Ograniczony budżet R&D", "Brak systematycznego procesu"],
        "improvement_opportunities": [
          "Stage-gate dla NPD",
          "Współpraca z uczelniami",
          "Zwiększenie budżetu do 6%"
        ]
      },
      
      "procurement": {
        "description": "Zakupy strategiczne, zarządzanie dostawcami",
        "cost_percent_of_revenue": 2,
        "assessment": "Dobra",
        "strengths": ["Dobre relacje z dostawcami", "Stabilność dostaw"],
        "weaknesses": ["Koncentracja dostawców", "Brak alternatyw dla części komponentów"]
      }
    },
    
    "margin_analysis": {
      "total_costs_percent": 82,
      "margin_percent": 18,
      "industry_benchmark_margin": 15,
      "position": "Above average",
      
      "cost_breakdown": {
        "materials": 45,
        "direct_labor": 18,
        "overhead": 12,
        "sales_marketing": 12,
        "admin": 8,
        "r_and_d": 4,
        "service": 4
      },
      
      "margin_by_activity": {
        "operations": "Highest value-add",
        "marketing_sales": "High value-add",
        "service": "Undermonetized",
        "logistics": "Cost center - optimize"
      }
    },
    
    "competitive_advantage_sources": {
      "primary_sources": [
        {
          "activity": "Operations - Quality",
          "advantage_type": "Differentiation",
          "sustainability": "Medium-high",
          "evidence": "Najniższy % braków w branży"
        },
        {
          "activity": "Sales - Technical expertise",
          "advantage_type": "Differentiation",
          "sustainability": "High",
          "evidence": "95% retencja, wysoki NPS"
        }
      ],
      
      "potential_sources": [
        {
          "activity": "Service",
          "opportunity": "Monetyzacja poprzez premium support",
          "investment_required": "Medium"
        },
        {
          "activity": "Technology Development",
          "opportunity": "Innowacje produktowe",
          "investment_required": "High"
        }
      ]
    },
    
    "strategic_recommendations": {
      "strengthen": [
        "Operacje - utrzymać przewagę jakościową",
        "Sprzedaż - rozwijać ekspertyzę techniczną"
      ],
      "improve": [
        "Marketing digital - znaczące inwestycje",
        "R&D - zwiększyć budżet i systematyzować",
        "Logistyka - optymalizacja kosztów"
      ],
      "consider_outsourcing": [
        "Niektóre funkcje IT",
        "Logistyka ostatniej mili"
      ],
      "priority_investments": [
        {
          "area": "Automatyzacja montażu",
          "investment": 2000000,
          "roi_months": 18,
          "priority": 1
        },
        {
          "area": "Platforma e-commerce B2B",
          "investment": 500000,
          "roi_months": 24,
          "priority": 2
        },
        {
          "area": "System track & trace",
          "investment": 200000,
          "roi_months": 12,
          "priority": 3
        }
      ]
    }
  }
}
```
```

---

## 2. BUSINESS MODEL CANVAS

```markdown
# BUSINESS MODEL CANVAS (Osterwalder)

## KIEDY STOSOWAĆ
- Projektowanie nowego modelu biznesowego
- Analiza istniejącego modelu
- Porównanie z konkurencją
- Planowanie pivot'u
- Komunikacja modelu inwestorom

## 9 BLOKÓW CANVASU

### 1. Customer Segments (Segmenty Klientów)
Kogo obsługujemy?
- Mass market
- Niche market
- Segmented
- Diversified
- Multi-sided platforms

### 2. Value Propositions (Propozycja Wartości)
Co dostarczamy klientom?
- Nowość
- Wydajność
- Customizacja
- "Getting the job done"
- Design
- Marka/Status
- Cena
- Redukcja kosztów
- Redukcja ryzyka
- Dostępność
- Wygoda

### 3. Channels (Kanały)
Jak docieramy do klientów?
- Fazy: Awareness → Evaluation → Purchase → Delivery → After-sales
- Typy: Direct (sales force, web) vs Indirect (partners, wholesale)

### 4. Customer Relationships (Relacje z Klientami)
Jakie relacje budujemy?
- Personal assistance
- Dedicated personal assistance
- Self-service
- Automated services
- Communities
- Co-creation

### 5. Revenue Streams (Strumienie Przychodów)
Jak zarabiamy?
- Asset sale
- Usage fee
- Subscription
- Lending/Renting/Leasing
- Licensing
- Brokerage fees
- Advertising

### 6. Key Resources (Kluczowe Zasoby)
Czego potrzebujemy?
- Physical (fabryki, pojazdy, IT)
- Intellectual (patenty, marki, know-how)
- Human (ludzie, ekspertyza)
- Financial (gotówka, kredyty)

### 7. Key Activities (Kluczowe Działania)
Co musimy robić?
- Production
- Problem solving
- Platform/Network

### 8. Key Partnerships (Kluczowi Partnerzy)
Kto nam pomaga?
- Optimization alliances
- Reduction of risk
- Acquisition of resources

### 9. Cost Structure (Struktura Kosztów)
Główne koszty?
- Cost-driven vs Value-driven
- Fixed costs
- Variable costs
- Economies of scale
- Economies of scope

## FORMAT WYJŚCIOWY

```json
{
  "business_model_canvas": {
    "company": "FADO Sp. z o.o.",
    "version": "1.0",
    "date": "2025-01-13",
    
    "customer_segments": {
      "primary_segments": [
        {
          "segment": "Hurtownie instalacyjne",
          "share_of_revenue": 45,
          "characteristics": "Duże wolumeny, niskie marże, lojalność",
          "needs": ["Szeroki asortyment", "Terminowość", "Konkurencyjna cena"],
          "size": "~200 firm w Polsce"
        },
        {
          "segment": "Przemysł (OEM)",
          "share_of_revenue": 30,
          "characteristics": "Specyfikacje, certyfikaty, długie kontrakty",
          "needs": ["Jakość", "Customizacja", "Wsparcie techniczne"],
          "size": "~500 potencjalnych klientów"
        },
        {
          "segment": "Wykonawcy instalacji",
          "share_of_revenue": 20,
          "characteristics": "Projektowy, wrażliwy cenowo",
          "needs": ["Dostępność", "Cena", "Wsparcie"],
          "size": "~5000 firm"
        },
        {
          "segment": "Eksport",
          "share_of_revenue": 5,
          "characteristics": "Rosnący, wymagający",
          "needs": ["Certyfikaty EU", "Konkurencyjność"],
          "size": "Potencjał wzrostu"
        }
      ],
      
      "segment_strategy": "Segmented B2B with differentiated approach"
    },
    
    "value_propositions": {
      "core_value": "Niezawodna armatura przemysłowa polskiej produkcji",
      
      "by_segment": {
        "hurtownie": [
          {
            "value": "Szeroki asortyment 'one-stop-shop'",
            "importance": "critical"
          },
          {
            "value": "Szybka realizacja zamówień",
            "importance": "high"
          },
          {
            "value": "Programy partnerskie i rabatowe",
            "importance": "high"
          }
        ],
        "przemysl": [
          {
            "value": "Customizacja według specyfikacji",
            "importance": "critical"
          },
          {
            "value": "Certyfikaty i dokumentacja",
            "importance": "critical"
          },
          {
            "value": "Wsparcie techniczne inżynierów",
            "importance": "high"
          }
        ],
        "wykonawcy": [
          {
            "value": "Konkurencyjna cena",
            "importance": "critical"
          },
          {
            "value": "Dostępność w dystrybucji",
            "importance": "high"
          },
          {
            "value": "Szkolenia produktowe",
            "importance": "medium"
          }
        ]
      },
      
      "differentiators": [
        "Polska produkcja (lokalna dostępność, wsparcie)",
        "Wysoka jakość (0.5% braków)",
        "Elastyczność (customizacja, małe serie)"
      ],
      
      "pain_relievers": [
        "Redukcja ryzyka przestojów (niezawodność)",
        "Uproszczenie zakupów (szeroki asortyment)",
        "Minimalizacja reklamacji (jakość)"
      ],
      
      "gain_creators": [
        "Wsparcie techniczne zwiększające efektywność instalacji",
        "Programy lojalnościowe poprawiające marżę dystrybutora"
      ]
    },
    
    "channels": {
      "awareness": [
        {"channel": "Targi branżowe", "effectiveness": "high"},
        {"channel": "Publikacje techniczne", "effectiveness": "medium"},
        {"channel": "Strona internetowa", "effectiveness": "medium"},
        {"channel": "Rekomendacje", "effectiveness": "high"}
      ],
      "evaluation": [
        {"channel": "Spotkania techniczne", "effectiveness": "high"},
        {"channel": "Próbki produktów", "effectiveness": "high"},
        {"channel": "Katalogi techniczne", "effectiveness": "medium"}
      ],
      "purchase": [
        {"channel": "Sprzedaż bezpośrednia (60%)", "type": "direct"},
        {"channel": "Dystrybutorzy (35%)", "type": "indirect"},
        {"channel": "E-commerce (5%)", "type": "direct"}
      ],
      "delivery": [
        {"channel": "Własna logistyka", "coverage": "Polska"},
        {"channel": "Spedycja", "coverage": "Eksport"}
      ],
      "after_sales": [
        {"channel": "Dział techniczny", "type": "direct"},
        {"channel": "Serwis terenowy", "type": "direct"}
      ],
      
      "channel_gaps": [
        "Słaba obecność online",
        "Brak platformy B2B",
        "Ograniczony marketing digitalowy"
      ]
    },
    
    "customer_relationships": {
      "relationship_types": [
        {
          "segment": "Key accounts",
          "type": "Dedicated personal assistance",
          "description": "Dedykowany opiekun klienta",
          "cost": "high",
          "value": "very high"
        },
        {
          "segment": "Dystrybutorzy",
          "type": "Personal assistance + programs",
          "description": "Account manager + programy partnerskie",
          "cost": "medium",
          "value": "high"
        },
        {
          "segment": "Mniejsi klienci",
          "type": "Self-service + support",
          "description": "Katalog + wsparcie na żądanie",
          "cost": "low",
          "value": "medium"
        }
      ],
      
      "retention_strategy": "Relacje długoterminowe, programy lojalnościowe",
      "acquisition_strategy": "Referencje, targi, cold calling techniczny",
      
      "metrics": {
        "customer_retention_rate": 95,
        "nps": 72,
        "customer_lifetime_value_avg": 150000
      }
    },
    
    "revenue_streams": {
      "primary_streams": [
        {
          "stream": "Sprzedaż produktów (asset sale)",
          "share": 92,
          "pricing_model": "Cennik + rabaty wolumenowe",
          "payment_terms": "30-60 dni"
        },
        {
          "stream": "Customizacja i projekty specjalne",
          "share": 5,
          "pricing_model": "Cost-plus",
          "payment_terms": "50% advance, 50% delivery"
        },
        {
          "stream": "Serwis i części zamienne",
          "share": 3,
          "pricing_model": "Cennik serwisowy",
          "payment_terms": "14 dni"
        }
      ],
      
      "revenue_characteristics": {
        "model": "Transaction-based (non-recurring)",
        "predictability": "Medium - zależność od projektów",
        "margins": {
          "products_standard": "18-22%",
          "products_custom": "25-35%",
          "service": "40-50%"
        }
      },
      
      "growth_opportunities": [
        "Subscription na serwis premium",
        "Licencjonowanie designów",
        "Usługi doradcze / engineering"
      ]
    },
    
    "key_resources": {
      "physical": [
        {
          "resource": "Zakład produkcyjny 8000m²",
          "importance": "critical",
          "owned": true
        },
        {
          "resource": "Park maszynowy CNC (25 maszyn)",
          "importance": "critical",
          "owned": true,
          "value": 15000000
        },
        {
          "resource": "Magazyn wyrobów gotowych",
          "importance": "high",
          "owned": true
        }
      ],
      "intellectual": [
        {
          "resource": "Know-how produkcyjny",
          "importance": "critical",
          "protected": "trade_secret"
        },
        {
          "resource": "Certyfikaty (CE, ISO 9001)",
          "importance": "critical",
          "protected": "certification"
        },
        {
          "resource": "Baza danych klientów i historia",
          "importance": "high",
          "protected": "internal"
        }
      ],
      "human": [
        {
          "resource": "Zespół produkcyjny (120 osób)",
          "importance": "critical",
          "key_competencies": ["CNC", "Montaż", "QC"]
        },
        {
          "resource": "Inżynierowie (15 osób)",
          "importance": "high",
          "key_competencies": ["R&D", "Wsparcie techniczne"]
        },
        {
          "resource": "Sprzedaż techniczna (8 osób)",
          "importance": "high",
          "key_competencies": ["Relacje", "Technika"]
        }
      ],
      "financial": [
        {
          "resource": "Kapitał obrotowy",
          "importance": "high",
          "status": "Adequate"
        },
        {
          "resource": "Linie kredytowe",
          "importance": "medium",
          "available": 5000000
        }
      ]
    },
    
    "key_activities": {
      "production": {
        "activities": [
          "Obróbka CNC komponentów",
          "Montaż zaworów",
          "Testowanie i kontrola jakości",
          "Pakowanie i wysyłka"
        ],
        "critical_success_factors": [
          "Jakość",
          "Efektywność",
          "Elastyczność"
        ]
      },
      "sales_marketing": {
        "activities": [
          "Zarządzanie relacjami z klientami",
          "Ofertowanie i negocjacje",
          "Udział w targach",
          "Wsparcie techniczne"
        ]
      },
      "development": {
        "activities": [
          "Rozwój nowych produktów",
          "Customizacja na zamówienie",
          "Optymalizacja procesów"
        ]
      }
    },
    
    "key_partnerships": {
      "strategic_partners": [
        {
          "partner_type": "Dostawcy strategiczni (stal, odlewy)",
          "purpose": "Zapewnienie dostaw i jakości",
          "relationship": "Long-term contracts",
          "dependency": "high"
        },
        {
          "partner_type": "Dystrybutorzy krajowi",
          "purpose": "Dostęp do rynku",
          "relationship": "Partnership agreements",
          "dependency": "medium-high"
        },
        {
          "partner_type": "Jednostki certyfikujące",
          "purpose": "Certyfikaty wymagane przez rynek",
          "relationship": "Contractual",
          "dependency": "medium"
        }
      ],
      
      "potential_partnerships": [
        "Uczelnie techniczne (R&D)",
        "Firmy IT (digitalizacja)",
        "Partnerzy eksportowi"
      ]
    },
    
    "cost_structure": {
      "model": "Value-driven (jakość > cena)",
      
      "major_costs": [
        {
          "category": "Materiały i komponenty",
          "share": 45,
          "type": "variable",
          "trend": "rising"
        },
        {
          "category": "Koszty pracy produkcyjnej",
          "share": 18,
          "type": "semi-variable",
          "trend": "rising"
        },
        {
          "category": "Koszty ogólne produkcji",
          "share": 12,
          "type": "fixed",
          "trend": "stable"
        },
        {
          "category": "Sprzedaż i marketing",
          "share": 12,
          "type": "semi-variable",
          "trend": "stable"
        },
        {
          "category": "Administracja",
          "share": 8,
          "type": "fixed",
          "trend": "stable"
        },
        {
          "category": "R&D",
          "share": 4,
          "type": "fixed",
          "trend": "should increase"
        }
      ],
      
      "cost_characteristics": {
        "fixed_variable_ratio": "35:65",
        "breakeven_utilization": "60%",
        "economies_of_scale": "Moderate"
      }
    },
    
    "canvas_assessment": {
      "strengths": [
        "Silna propozycja wartości (jakość, customizacja)",
        "Efektywne operacje",
        "Lojalna baza klientów"
      ],
      "weaknesses": [
        "Słabe kanały digitalne",
        "Ograniczone R&D",
        "Koncentracja na jednym rynku"
      ],
      "opportunities": [
        "E-commerce B2B",
        "Serwis jako revenue stream",
        "Ekspansja geograficzna"
      ],
      "threats": [
        "Import niskokosztowy",
        "Konsolidacja dystrybutorów",
        "Presja na marże"
      ]
    }
  }
}
```
```

---

## 3. LEAN CANVAS

```markdown
# LEAN CANVAS (Ash Maurya)

## KIEDY STOSOWAĆ
- Startupy i nowe ventures
- Szybka walidacja pomysłu
- Iteracja modelu biznesowego
- Pitch deck preparation

## RÓŻNICE VS BUSINESS MODEL CANVAS
- Problem zamiast Key Partners
- Solution zamiast Key Activities
- Key Metrics zamiast Key Resources
- Unfair Advantage zamiast Customer Relationships

## FORMAT WYJŚCIOWY

```json
{
  "lean_canvas": {
    "product": "MI Platform - Market Intelligence",
    "version": "1.0",
    "date": "2025-01-13",
    "iteration": 3,
    
    "problem": {
      "top_3_problems": [
        {
          "problem": "Czasochłonne ręczne zbieranie informacji o firmach i rynkach",
          "pain_level": "high",
          "current_solution": "Ręczny research, Excel, różne źródła"
        },
        {
          "problem": "Brak ustrukturyzowanych analiz - dane są rozproszone",
          "pain_level": "high",
          "current_solution": "Kupowanie raportów, konsultanci"
        },
        {
          "problem": "Trudność w śledzeniu konkurencji na bieżąco",
          "pain_level": "medium",
          "current_solution": "Ad-hoc monitoring, Google Alerts"
        }
      ],
      
      "existing_alternatives": [
        "Ręczny research (Google, KRS, LinkedIn)",
        "Raporty branżowe (Statista, IBISWorld) - drogie",
        "Konsultanci strategiczni - bardzo drodzy",
        "Narzędzia punktowe (SimilarWeb, etc.)"
      ]
    },
    
    "customer_segments": {
      "target_customers": [
        {
          "segment": "Business Development w firmach produkcyjnych",
          "size": "10,000+ w Polsce",
          "urgency": "high",
          "accessibility": "medium"
        },
        {
          "segment": "Firmy konsultingowe / doradcze",
          "size": "500+",
          "urgency": "high",
          "accessibility": "high"
        },
        {
          "segment": "Fundusze PE/VC - due diligence",
          "size": "100+",
          "urgency": "medium",
          "accessibility": "low"
        }
      ],
      
      "early_adopters": {
        "description": "Business Development Managers w średnich firmach produkcyjnych, którzy regularnie analizują nowe rynki i konkurencję",
        "characteristics": [
          "Technologicznie biegli",
          "Budżet na narzędzia",
          "Ból jest palący",
          "Decyzyjność"
        ]
      }
    },
    
    "unique_value_proposition": {
      "headline": "Wywiad rynkowy w minuty, nie dni",
      "sub_headline": "AI-powered platforma do kompleksowej analizy firm, rynków i konkurencji",
      
      "high_level_concept": "Jak ChatGPT, ale dla business intelligence z dostępem do polskich źródeł danych",
      
      "key_differentiators": [
        "Lokalne źródła danych (KRS, CEIDG, polskie portale)",
        "Wielopoziomowa analiza, nie tylko dane surowe",
        "Konwersacyjny interfejs - pytaj jak człowieka"
      ]
    },
    
    "solution": {
      "top_3_features": [
        {
          "feature": "Konwersacyjny agent do zadawania pytań o firmy i rynki",
          "addresses_problem": 1,
          "mvp_scope": "full"
        },
        {
          "feature": "Automatyczne raporty z frameworkami (SWOT, Porter, etc.)",
          "addresses_problem": 2,
          "mvp_scope": "simplified"
        },
        {
          "feature": "Monitoring konkurencji i alerty",
          "addresses_problem": 3,
          "mvp_scope": "basic"
        }
      ],
      
      "mvp_definition": {
        "scope": "Chat + Company Profile + Basic SWOT",
        "build_time": "3 months",
        "features_out_of_scope": [
          "Full market sizing",
          "Real-time monitoring",
          "API access"
        ]
      }
    },
    
    "channels": {
      "primary_channels": [
        {
          "channel": "Content marketing (LinkedIn, blog)",
          "cost": "low",
          "scalability": "high"
        },
        {
          "channel": "Webinary i workshops",
          "cost": "medium",
          "scalability": "medium"
        },
        {
          "channel": "Referral / word of mouth",
          "cost": "low",
          "scalability": "medium"
        }
      ],
      
      "customer_acquisition_path": "Content → Lead magnet (free analysis) → Demo → Trial → Paid"
    },
    
    "revenue_streams": {
      "primary_model": "SaaS subscription",
      
      "pricing_tiers": [
        {
          "tier": "Starter",
          "price": "299 PLN/mies",
          "features": "10 analiz/mies, basic reports",
          "target": "Freelancers, small teams"
        },
        {
          "tier": "Professional",
          "price": "999 PLN/mies",
          "features": "50 analiz, all frameworks, export",
          "target": "SMB BD teams"
        },
        {
          "tier": "Enterprise",
          "price": "Custom",
          "features": "Unlimited, API, custom integrations",
          "target": "Large organizations"
        }
      ],
      
      "revenue_projections": {
        "year_1": 200000,
        "year_2": 800000,
        "year_3": 2500000
      }
    },
    
    "cost_structure": {
      "fixed_costs": [
        {"item": "Team (3 FTE)", "monthly": 45000},
        {"item": "Infrastructure", "monthly": 5000},
        {"item": "Tools & APIs", "monthly": 8000}
      ],
      
      "variable_costs": [
        {"item": "LLM API costs", "per_analysis": 5},
        {"item": "Data APIs", "per_analysis": 2}
      ],
      
      "monthly_burn": 60000,
      "runway_needed": "18 months"
    },
    
    "key_metrics": {
      "acquisition": [
        {"metric": "Website visitors", "target": "5000/mies"},
        {"metric": "Trial signups", "target": "100/mies"},
        {"metric": "CAC", "target": "<500 PLN"}
      ],
      "activation": [
        {"metric": "First analysis completed", "target": ">80%"},
        {"metric": "Time to first value", "target": "<10 min"}
      ],
      "retention": [
        {"metric": "Monthly churn", "target": "<5%"},
        {"metric": "NPS", "target": ">50"}
      ],
      "revenue": [
        {"metric": "MRR", "target_12m": "50,000 PLN"},
        {"metric": "LTV/CAC", "target": ">3"}
      ],
      "referral": [
        {"metric": "Referral rate", "target": ">20%"}
      ]
    },
    
    "unfair_advantage": {
      "advantages": [
        {
          "advantage": "Deep domain expertise in Polish manufacturing sector",
          "copyability": "hard",
          "duration": "long-term"
        },
        {
          "advantage": "Curated Polish data sources integrations",
          "copyability": "medium",
          "duration": "medium-term"
        },
        {
          "advantage": "Industry-specific prompt engineering and frameworks",
          "copyability": "hard",
          "duration": "medium-term"
        }
      ],
      
      "moat_building": [
        "Accumulate proprietary industry data",
        "Build network effects through shared insights",
        "Deep integration with client workflows"
      ]
    },
    
    "risks_and_assumptions": {
      "riskiest_assumptions": [
        {
          "assumption": "Users will pay 300+ PLN/mies for automated analysis",
          "validation_method": "Landing page + pricing test",
          "validated": false
        },
        {
          "assumption": "AI quality will be sufficient for business decisions",
          "validation_method": "Expert review of outputs",
          "validated": "partially"
        },
        {
          "assumption": "Polish data sources are accessible and integrable",
          "validation_method": "Technical spike",
          "validated": true
        }
      ],
      
      "next_experiments": [
        "Landing page z pricing - measure conversion",
        "10 interviews z target personas",
        "MVP z 5 beta users"
      ]
    }
  }
}
```
```

---

## 4. JOBS TO BE DONE (JTBD)

```markdown
# JOBS TO BE DONE FRAMEWORK

## KIEDY STOSOWAĆ
- Zrozumienie głębokich potrzeb klientów
- Rozwój produktu
- Pozycjonowanie i messaging
- Innowacje przełomowe

## KONCEPCJA
Klienci nie kupują produktów - "zatrudniają" je do wykonania pewnej pracy (job).

## TYPY JOBS

### Functional Jobs
Co klient chce osiągnąć funkcjonalnie?
- Wykonać zadanie
- Rozwiązać problem
- Osiągnąć cel

### Emotional Jobs
Jak klient chce się czuć?
- Pewny siebie
- W kontroli
- Kompetentny

### Social Jobs
Jak klient chce być postrzegany?
- Jako ekspert
- Jako innowator
- Jako skuteczny

## FORMAT WYJŚCIOWY

```json
{
  "jtbd_analysis": {
    "product": "Market Intelligence Platform",
    "target_persona": "Business Development Manager w firmie produkcyjnej",
    "date": "2025-01-13",
    
    "main_job": {
      "job_statement": "Kiedy [ekspanduję działalność na nowy rynek], chcę [szybko zrozumieć landscape konkurencyjny i potencjał], żebym mógł [podjąć świadomą decyzję i przekonać zarząd]",
      
      "context": {
        "situation": "Firma rozważa wejście na nowy rynek lub segment",
        "trigger": "Decyzja zarządu o ekspansji, request od CEO",
        "constraints": [
          "Ograniczony czas (tydzień-dwa)",
          "Ograniczony budżet na zewnętrzne raporty",
          "Brak dedykowanego zespołu research"
        ]
      }
    },
    
    "job_map": {
      "stages": [
        {
          "stage": "1. Definiowanie potrzeby",
          "jobs": [
            {
              "job": "Określić zakres i cel badania",
              "importance": 7,
              "satisfaction_current": 5,
              "opportunity_score": 9
            },
            {
              "job": "Zidentyfikować kluczowe pytania do odpowiedzi",
              "importance": 8,
              "satisfaction_current": 4,
              "opportunity_score": 12
            }
          ]
        },
        {
          "stage": "2. Zbieranie informacji",
          "jobs": [
            {
              "job": "Znaleźć wiarygodne źródła danych o rynku",
              "importance": 9,
              "satisfaction_current": 3,
              "opportunity_score": 15
            },
            {
              "job": "Zebrać dane o konkurentach",
              "importance": 9,
              "satisfaction_current": 4,
              "opportunity_score": 14
            },
            {
              "job": "Zdobyć dane finansowe i strukturalne firm",
              "importance": 8,
              "satisfaction_current": 5,
              "opportunity_score": 11
            }
          ]
        },
        {
          "stage": "3. Analiza i synteza",
          "jobs": [
            {
              "job": "Porównać konkurentów w ustrukturyzowany sposób",
              "importance": 9,
              "satisfaction_current": 3,
              "opportunity_score": 15
            },
            {
              "job": "Oszacować wielkość i potencjał rynku",
              "importance": 8,
              "satisfaction_current": 4,
              "opportunity_score": 12
            },
            {
              "job": "Zidentyfikować szanse i zagrożenia",
              "importance": 9,
              "satisfaction_current": 4,
              "opportunity_score": 14
            }
          ]
        },
        {
          "stage": "4. Komunikacja wyników",
          "jobs": [
            {
              "job": "Przygotować przekonujący raport dla zarządu",
              "importance": 9,
              "satisfaction_current": 5,
              "opportunity_score": 13
            },
            {
              "job": "Odpowiedzieć na pytania i wątpliwości",
              "importance": 8,
              "satisfaction_current": 6,
              "opportunity_score": 10
            }
          ]
        },
        {
          "stage": "5. Monitoring i aktualizacja",
          "jobs": [
            {
              "job": "Śledzić zmiany na rynku i u konkurencji",
              "importance": 7,
              "satisfaction_current": 2,
              "opportunity_score": 12
            }
          ]
        }
      ]
    },
    
    "emotional_jobs": [
      {
        "job": "Czuć się pewnie prezentując rekomendacje",
        "importance": 9,
        "current_pain": "Niepewność czy dane są kompletne i aktualne"
      },
      {
        "job": "Być postrzeganym jako kompetentny strateg",
        "importance": 8,
        "current_pain": "Ryzyko pominięcia ważnych informacji"
      },
      {
        "job": "Nie tracić czasu na żmudny research",
        "importance": 8,
        "current_pain": "Ręczne zbieranie danych zajmuje dni"
      }
    ],
    
    "social_jobs": [
      {
        "job": "Być postrzeganym jako ktoś kto 'ma dane'",
        "importance": 7,
        "context": "W dyskusjach z zarządem i współpracownikami"
      },
      {
        "job": "Wyróżniać się profesjonalizmem analiz",
        "importance": 6,
        "context": "Vs konkurencyjne projekty/działy"
      }
    ],
    
    "pains": {
      "functional_pains": [
        {
          "pain": "Ręczne zbieranie danych zajmuje 2-5 dni",
          "severity": "high",
          "frequency": "every_project"
        },
        {
          "pain": "Dane z różnych źródeł są niespójne",
          "severity": "medium",
          "frequency": "often"
        },
        {
          "pain": "Brak dostępu do niektórych źródeł (płatne raporty)",
          "severity": "high",
          "frequency": "often"
        },
        {
          "pain": "Trudność w porównywaniu firm 'jabłka do jabłek'",
          "severity": "medium",
          "frequency": "always"
        }
      ],
      "emotional_pains": [
        {
          "pain": "Stres przed prezentacją - czy niczego nie pominąłem?",
          "severity": "high"
        },
        {
          "pain": "Frustracja przy powtarzalnych taskach research",
          "severity": "medium"
        }
      ]
    },
    
    "gains": {
      "required_gains": [
        "Kompletne dane o firmach (rejestrowe, finansowe)",
        "Aktualne informacje (nie starsze niż miesiąc)",
        "Wiarygodne źródła"
      ],
      "expected_gains": [
        "Ustrukturyzowana analiza konkurencji",
        "Estymacja wielkości rynku",
        "Export do PowerPoint/Word"
      ],
      "desired_gains": [
        "Automatyczne aktualizacje",
        "Benchmarking w czasie",
        "Alerty o zmianach"
      ],
      "unexpected_gains": [
        "Odkrycie nieoczywistych konkurentów",
        "Insight'y strategiczne AI",
        "Network mapping firm"
      ]
    },
    
    "opportunity_prioritization": {
      "method": "ODI (Outcome-Driven Innovation)",
      "formula": "Opportunity = Importance + max(Importance - Satisfaction, 0)",
      
      "top_opportunities": [
        {
          "job": "Znaleźć wiarygodne źródła danych o rynku",
          "opportunity_score": 15,
          "priority": 1,
          "solution_direction": "Integracja z KRS, GUS, portalami branżowymi"
        },
        {
          "job": "Porównać konkurentów w ustrukturyzowany sposób",
          "opportunity_score": 15,
          "priority": 2,
          "solution_direction": "Automatyczne competitive matrix z frameworkami"
        },
        {
          "job": "Zebrać dane o konkurentach",
          "opportunity_score": 14,
          "priority": 3,
          "solution_direction": "Multi-source aggregation w jednym miejscu"
        },
        {
          "job": "Zidentyfikować szanse i zagrożenia",
          "opportunity_score": 14,
          "priority": 4,
          "solution_direction": "AI-driven SWOT generation"
        }
      ],
      
      "underserved_jobs": [
        "Śledzenie zmian na rynku (opportunity: 12, satisfaction: 2)",
        "Definiowanie kluczowych pytań (opportunity: 12, satisfaction: 4)"
      ]
    },
    
    "product_implications": {
      "must_have_features": [
        "Integracja z polskimi rejestrami (KRS, CEIDG)",
        "Automatyczne tworzenie profili firm",
        "Competitive comparison matrix",
        "Export do PPT/DOCX"
      ],
      "should_have_features": [
        "AI-generated SWOT analysis",
        "Market sizing estimation",
        "Source citation and confidence levels"
      ],
      "nice_to_have_features": [
        "Real-time monitoring",
        "Network/relationship mapping",
        "Custom frameworks"
      ],
      
      "positioning_statement": "Dla Business Development Managerów w firmach produkcyjnych, którzy potrzebują szybko przygotować analizę rynku i konkurencji, [MI Platform] to narzędzie AI do wywiadu rynkowego, które automatycznie zbiera i analizuje dane z polskich źródeł, w przeciwieństwie do ręcznego researchu lub drogich raportów konsultingowych."
    }
  }
}
```
```

---

*Następny dokument: 10_UI_CHAT_INTERFACE.md*
