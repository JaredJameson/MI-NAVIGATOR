# 08. Frameworki Strategiczne

## Przegląd

Szablony frameworków strategicznych używane przez agentów do strukturyzowania analiz:
1. **SWOT** - Mocne/słabe strony, szanse/zagrożenia
2. **PESTLE** - Makrootoczenie
3. **Porter's Five Forces** - Siły konkurencyjne
4. **BCG Matrix** - Portfolio produktowe
5. **Ansoff Matrix** - Strategie wzrostu

---

## 1. SWOT ANALYSIS

```markdown
# SWOT FRAMEWORK

## KIEDY STOSOWAĆ
- Analiza pozycji konkurencyjnej firmy
- Ocena projektu/produktu przed launch
- Planowanie strategiczne
- Due diligence

## STRUKTURA ANALIZY

### STRENGTHS (Mocne Strony) - Wewnętrzne, Pozytywne
Pytania diagnostyczne:
- Co firma robi lepiej niż konkurencja?
- Jakie unikalne zasoby/kompetencje posiada?
- Co klienci wskazują jako przewagę?
- Jakie patenty/technologie posiada?
- Jaka jest siła marki?

Typowe kategorie:
- Zasoby finansowe
- Kompetencje zespołu
- Technologia/IP
- Relacje z klientami
- Efektywność operacyjna
- Marka i reputacja

### WEAKNESSES (Słabe Strony) - Wewnętrzne, Negatywne
Pytania diagnostyczne:
- Gdzie firma przegrywa z konkurencją?
- Jakich zasobów/kompetencji brakuje?
- Co klienci krytykują?
- Jakie procesy są nieefektywne?
- Gdzie są luki w ofercie?

Typowe kategorie:
- Ograniczenia finansowe
- Braki kompetencyjne
- Przestarzała technologia
- Słaba dystrybucja
- Problemy jakościowe

### OPPORTUNITIES (Szanse) - Zewnętrzne, Pozytywne
Pytania diagnostyczne:
- Jakie trendy rynkowe sprzyjają firmie?
- Jakie nowe segmenty można zdobyć?
- Jakie zmiany regulacyjne tworzą szanse?
- Czy konkurenci mają problemy?
- Jakie technologie otwierają możliwości?

Typowe kategorie:
- Wzrost rynku
- Nowe segmenty
- Zmiany regulacyjne
- Słabości konkurentów
- Nowe technologie
- Zmiany demograficzne

### THREATS (Zagrożenia) - Zewnętrzne, Negatywne
Pytania diagnostyczne:
- Jakie trendy mogą zaszkodzić?
- Co robi konkurencja?
- Jakie ryzyka regulacyjne istnieją?
- Czy pojawiają się substytuty?
- Jakie zagrożenia makroekonomiczne?

Typowe kategorie:
- Nowi konkurenci
- Produkty substytucyjne
- Zmiany regulacyjne
- Spowolnienie gospodarcze
- Zmiany technologiczne
- Problemy z dostawcami

## FORMAT WYJŚCIOWY

```json
{
  "swot_analysis": {
    "company": "NAZWA FIRMY",
    "date": "2025-01-13",
    "analyst": "Market Intelligence Agent",
    
    "strengths": [
      {
        "factor": "Silna marka w segmencie premium",
        "evidence": "NPS 72, rozpoznawalność 85% w grupie docelowej",
        "impact": "high",
        "sustainability": "long-term"
      },
      {
        "factor": "Własne patenty technologiczne",
        "evidence": "12 aktywnych patentów, 3 pending",
        "impact": "high",
        "sustainability": "medium-term"
      }
    ],
    
    "weaknesses": [
      {
        "factor": "Ograniczona dystrybucja zagraniczna",
        "evidence": "Tylko 15% przychodów z eksportu vs 40% u lidera",
        "impact": "medium",
        "addressable": true,
        "required_investment": "high"
      }
    ],
    
    "opportunities": [
      {
        "factor": "Rosnący rynek renewable energy",
        "evidence": "CAGR 12% do 2030, Green Deal EU",
        "impact": "high",
        "timeline": "3-5 years",
        "fit_with_strengths": ["Technologia", "R&D"]
      }
    ],
    
    "threats": [
      {
        "factor": "Import tańszych produktów z Azji",
        "evidence": "Wzrost importu o 25% r/r",
        "probability": "high",
        "impact": "medium",
        "mitigation_possible": true
      }
    ],
    
    "cross_analysis": {
      "so_strategies": [
        "Wykorzystać patenty do ekspansji na rynek OZE"
      ],
      "wo_strategies": [
        "Partnerstwa dystrybucyjne w EU"
      ],
      "st_strategies": [
        "Wzmocnić pozycjonowanie premium vs import"
      ],
      "wt_strategies": [
        "Dywersyfikacja geograficzna zmniejszy ryzyko"
      ]
    },
    
    "summary": {
      "overall_position": "Silna pozycja z potencjałem wzrostu",
      "priority_actions": [
        "Ekspansja na rynek OZE",
        "Rozwój dystrybucji zagranicznej"
      ],
      "key_risks": [
        "Presja cenowa z importu"
      ]
    }
  }
}
```

## SCORING MODEL

Każdy czynnik oceniany w skali:
- Impact: high (3) / medium (2) / low (1)
- Probability/Certainty: high / medium / low
- Timeline: immediate / short-term / long-term

Overall score = Σ(Impact × Probability weight)
```

---

## 2. PESTLE ANALYSIS

```markdown
# PESTLE FRAMEWORK

## KIEDY STOSOWAĆ
- Analiza wejścia na nowy rynek
- Ocena makrootoczenia przed inwestycją
- Planowanie strategiczne długoterminowe
- Analiza ryzyk geopolitycznych

## STRUKTURA ANALIZY

### P - Political (Czynniki Polityczne)
- Stabilność polityczna
- Polityka handlowa
- Regulacje branżowe
- Polityka podatkowa
- Relacje międzynarodowe

### E - Economic (Czynniki Ekonomiczne)
- PKB i wzrost gospodarczy
- Inflacja
- Stopy procentowe
- Kursy walut
- Bezrobocie
- Siła nabywcza

### S - Social (Czynniki Społeczne)
- Demografia
- Edukacja i kwalifikacje
- Styl życia
- Postawy konsumenckie
- Mobilność społeczna
- Zdrowie publiczne

### T - Technological (Czynniki Technologiczne)
- Poziom innowacyjności
- Automatyzacja
- Digitalizacja
- R&D spending
- Transfer technologii
- Infrastruktura IT

### L - Legal (Czynniki Prawne)
- Prawo pracy
- Ochrona konsumentów
- Prawo konkurencji
- Własność intelektualna
- Ochrona danych (GDPR)
- Wymogi certyfikacji

### E - Environmental (Czynniki Środowiskowe)
- Regulacje środowiskowe
- Zmiany klimatyczne
- Zrównoważony rozwój
- Gospodarka odpadami
- Ślad węglowy
- ESG requirements

## FORMAT WYJŚCIOWY

```json
{
  "pestle_analysis": {
    "market": "Polska - sektor produkcyjny",
    "date": "2025-01-13",
    "horizon": "3-5 lat",
    
    "political": {
      "factors": [
        {
          "factor": "Członkostwo w UE",
          "current_state": "Stabilne, dostęp do funduszy",
          "trend": "stable",
          "impact_on_business": "positive",
          "impact_score": 8,
          "key_implications": [
            "Dostęp do rynku 450M konsumentów",
            "Fundusze na modernizację",
            "Harmonizacja regulacji"
          ]
        },
        {
          "factor": "Relacje z głównymi partnerami handlowymi",
          "current_state": "Napięcia z niektórymi rynkami",
          "trend": "uncertain",
          "impact_on_business": "mixed",
          "impact_score": 5
        },
        {
          "factor": "Polityka przemysłowa",
          "current_state": "Wsparcie dla reindustrializacji",
          "trend": "positive",
          "impact_on_business": "positive",
          "impact_score": 7
        }
      ],
      "overall_assessment": "Generalnie sprzyjające, z pewnymi niepewnościami",
      "risk_level": "medium-low"
    },
    
    "economic": {
      "factors": [
        {
          "factor": "Wzrost PKB",
          "current_value": "3.2%",
          "forecast": "2.8-3.5%",
          "trend": "stable-positive",
          "impact_score": 7
        },
        {
          "factor": "Inflacja",
          "current_value": "4.5%",
          "forecast": "spadek do 3%",
          "trend": "improving",
          "impact_score": 6
        },
        {
          "factor": "Koszty pracy",
          "current_value": "Wzrost 8-10% r/r",
          "trend": "rising",
          "impact_on_business": "negative",
          "impact_score": 4
        },
        {
          "factor": "Kursy walut EUR/PLN",
          "current_value": "4.35",
          "volatility": "medium",
          "impact_score": 5
        }
      ],
      "overall_assessment": "Stabilna gospodarka z presją kosztową",
      "risk_level": "medium"
    },
    
    "social": {
      "factors": [
        {
          "factor": "Demografia - starzenie społeczeństwa",
          "trend": "negative",
          "timeline": "long-term",
          "impact_on_business": "negative",
          "impact_score": 4,
          "implications": ["Niedobór pracowników", "Rosnące koszty pracy"]
        },
        {
          "factor": "Poziom wykształcenia technicznego",
          "current_state": "Wysoki, ale malejąca liczba absolwentów",
          "trend": "concerning",
          "impact_score": 5
        },
        {
          "factor": "Świadomość ekologiczna",
          "trend": "rising",
          "impact_on_business": "opportunity",
          "impact_score": 7
        }
      ],
      "overall_assessment": "Wyzwania demograficzne, rosnąca świadomość ESG",
      "risk_level": "medium"
    },
    
    "technological": {
      "factors": [
        {
          "factor": "Industry 4.0 adoption",
          "current_state": "Przyspiesza",
          "trend": "positive",
          "impact_on_business": "opportunity",
          "impact_score": 9
        },
        {
          "factor": "AI i automatyzacja",
          "adoption_rate": "Rosnąca",
          "trend": "accelerating",
          "impact_on_business": "transformational",
          "impact_score": 9
        },
        {
          "factor": "Infrastruktura cyfrowa",
          "current_state": "Dobra i rozwijająca się",
          "trend": "positive",
          "impact_score": 7
        }
      ],
      "overall_assessment": "Duże możliwości z transformacji cyfrowej",
      "risk_level": "low (opportunity-driven)"
    },
    
    "legal": {
      "factors": [
        {
          "factor": "GDPR i ochrona danych",
          "compliance_required": true,
          "complexity": "high",
          "impact_score": 6
        },
        {
          "factor": "Prawo pracy",
          "trend": "Rosnąca ochrona pracowników",
          "impact_on_business": "increasing costs",
          "impact_score": 5
        },
        {
          "factor": "Certyfikacje produktowe (CE, ISO)",
          "requirements": "Stabilne",
          "trend": "stable",
          "impact_score": 6
        }
      ],
      "overall_assessment": "Stabilne środowisko prawne, rosnące wymogi compliance",
      "risk_level": "medium"
    },
    
    "environmental": {
      "factors": [
        {
          "factor": "EU Green Deal",
          "timeline": "2030-2050",
          "impact_on_business": "transformational",
          "impact_score": 9,
          "requirements": [
            "Redukcja emisji CO2",
            "Circular economy",
            "ESG reporting"
          ]
        },
        {
          "factor": "Carbon pricing / ETS",
          "trend": "Rosnące ceny uprawnień",
          "impact_on_business": "cost increase",
          "impact_score": 7
        },
        {
          "factor": "Wymogi recyklingu",
          "trend": "Zaostrzające się",
          "impact_on_business": "mixed - cost & opportunity",
          "impact_score": 7
        }
      ],
      "overall_assessment": "Transformacja środowiskowa jako główny driver zmian",
      "risk_level": "high (but also opportunity)"
    },
    
    "summary": {
      "key_opportunities": [
        "Transformacja cyfrowa (Industry 4.0, AI)",
        "Green transition - nowe produkty i rynki",
        "Fundusze UE na modernizację"
      ],
      "key_threats": [
        "Presja kosztowa (praca, energia, CO2)",
        "Niedobór wykwalifikowanych pracowników",
        "Rosnące wymogi regulacyjne"
      ],
      "strategic_implications": [
        "Inwestycje w automatyzację",
        "Rozwój oferty sustainable products",
        "Budowa employer branding"
      ],
      "overall_environment_rating": "Moderately Favorable",
      "confidence_level": "high"
    }
  }
}
```
```

---

## 3. PORTER'S FIVE FORCES

```markdown
# PORTER'S FIVE FORCES FRAMEWORK

## KIEDY STOSOWAĆ
- Analiza atrakcyjności branży
- Ocena intensywności konkurencji
- Planowanie strategii konkurencyjnej
- Due diligence sektorowe

## STRUKTURA ANALIZY

### 1. THREAT OF NEW ENTRANTS (Groźba nowych wejść)
Bariery wejścia do oceny:
- Ekonomia skali
- Wymagany kapitał początkowy
- Dostęp do kanałów dystrybucji
- Polityka rządowa / licencje
- Koszty zmiany dostawcy dla klientów
- Przewagi kosztowe niezależne od skali (patenty, lokalizacja)
- Oczekiwana retaliacja obecnych graczy

Pytania diagnostyczne:
- Ile kosztuje wejście na rynek?
- Jak długo trwa zbudowanie pozycji?
- Czy są silne marki?
- Czy potrzebne są certyfikacje/licencje?

### 2. BARGAINING POWER OF SUPPLIERS (Siła dostawców)
Czynniki zwiększające siłę:
- Koncentracja dostawców
- Brak substytutów
- Znaczenie branży dla dostawcy
- Koszty zmiany dostawcy
- Zagrożenie integracją w przód
- Zróżnicowanie produktów dostawcy

Pytania diagnostyczne:
- Ilu jest dostawców kluczowych komponentów?
- Czy łatwo zmienić dostawcę?
- Czy dostawca może wejść na nasz rynek?

### 3. BARGAINING POWER OF BUYERS (Siła nabywców)
Czynniki zwiększające siłę:
- Koncentracja nabywców
- Wolumen zakupów
- Standaryzacja produktów
- Koszty zmiany dostawcy
- Zagrożenie integracją wstecz
- Wrażliwość cenowa
- Dostęp do informacji

Pytania diagnostyczne:
- Jak skoncentrowani są klienci?
- Czy produkt jest standardowy?
- Jak wrażliwi są na cenę?

### 4. THREAT OF SUBSTITUTES (Zagrożenie substytutami)
Czynniki do oceny:
- Dostępność substytutów
- Stosunek cena/wydajność substytutów
- Koszty zmiany na substytut
- Skłonność nabywców do substytucji
- Trendy technologiczne

Pytania diagnostyczne:
- Czym klient może zastąpić nasz produkt?
- Czy substytuty są tańsze/lepsze?
- Jakie trendy sprzyjają substytutom?

### 5. INDUSTRY RIVALRY (Rywalizacja w branży)
Czynniki intensyfikujące:
- Liczba konkurentów
- Tempo wzrostu branży
- Koszty stałe / koszty magazynowania
- Zróżnicowanie produktów
- Bariery wyjścia
- Różnorodność strategii konkurentów

Pytania diagnostyczne:
- Ilu jest konkurentów?
- Czy rynek rośnie czy stagnuje?
- Jak silna jest konkurencja cenowa?

## FORMAT WYJŚCIOWY

```json
{
  "porter_five_forces": {
    "industry": "Armatura przemysłowa - Polska",
    "date": "2025-01-13",
    
    "threat_of_new_entrants": {
      "force_strength": "medium",
      "score": 5,
      "factors": [
        {
          "factor": "Kapitał początkowy",
          "assessment": "Znaczący - €1-5M na linię produkcyjną",
          "barrier_level": "medium-high"
        },
        {
          "factor": "Certyfikacje wymagane",
          "assessment": "CE, ISO niezbędne - 12-18 mies.",
          "barrier_level": "medium"
        },
        {
          "factor": "Relacje z dystrybutorami",
          "assessment": "Trudne do zbudowania - lojalność",
          "barrier_level": "medium-high"
        },
        {
          "factor": "Ekonomia skali",
          "assessment": "Umiarkowana - specjalizacja możliwa",
          "barrier_level": "medium"
        },
        {
          "factor": "Marki i reputacja",
          "assessment": "Istotne w premium, mniej w commodity",
          "barrier_level": "medium"
        }
      ],
      "recent_entrants": [
        "Import z Turcji - konkurencja cenowa",
        "Chińscy producenci - segment economy"
      ],
      "conclusion": "Umiarkowane bariery - wejście możliwe w niszach"
    },
    
    "supplier_power": {
      "force_strength": "medium-low",
      "score": 4,
      "factors": [
        {
          "factor": "Koncentracja dostawców stali",
          "assessment": "Kilku dużych graczy, ale wymienialnych",
          "power_level": "medium"
        },
        {
          "factor": "Koncentracja dostawców komponentów",
          "assessment": "Wielu dostawców, łatwa substytucja",
          "power_level": "low"
        },
        {
          "factor": "Koszty zmiany dostawcy",
          "assessment": "Niskie dla standardowych materiałów",
          "power_level": "low"
        },
        {
          "factor": "Zagrożenie integracją w przód",
          "assessment": "Niskie - inny biznes",
          "power_level": "low"
        }
      ],
      "key_suppliers": ["Huty stali", "Producenci uszczelek", "Odlewnie"],
      "conclusion": "Dostawcy mają ograniczoną siłę przetargową"
    },
    
    "buyer_power": {
      "force_strength": "medium-high",
      "score": 7,
      "factors": [
        {
          "factor": "Koncentracja nabywców",
          "assessment": "Hurtownie i sieci instalacyjne - skoncentrowane",
          "power_level": "high"
        },
        {
          "factor": "Wolumen zakupów",
          "assessment": "Duże zamówienia od dystrybutorów",
          "power_level": "high"
        },
        {
          "factor": "Standaryzacja produktów",
          "assessment": "Wysoka w segmencie podstawowym",
          "power_level": "high"
        },
        {
          "factor": "Koszty zmiany",
          "assessment": "Niskie dla produktów standardowych",
          "power_level": "medium-high"
        },
        {
          "factor": "Wrażliwość cenowa",
          "assessment": "Wysoka w commodity, niska w specjalistycznych",
          "power_level": "medium"
        }
      ],
      "key_buyers": ["Hurtownie instalacyjne", "Sieci DIY", "Wykonawcy"],
      "conclusion": "Nabywcy mają znaczącą siłę przetargową, zwłaszcza dystrybutorzy"
    },
    
    "threat_of_substitutes": {
      "force_strength": "low",
      "score": 3,
      "factors": [
        {
          "factor": "Alternatywne technologie",
          "assessment": "Plastikowa armatura - ograniczone zastosowania",
          "threat_level": "low"
        },
        {
          "factor": "Nowe materiały",
          "assessment": "Kompozyty - nisza, nie mainstream",
          "threat_level": "low"
        },
        {
          "factor": "Zmiana technologii instalacji",
          "assessment": "Ewolucyjna, nie rewolucyjna",
          "threat_level": "low"
        }
      ],
      "potential_substitutes": [
        "Armatura z tworzyw sztucznych (zastosowania niskotemperaturowe)",
        "Systemy prefabrykowane"
      ],
      "conclusion": "Niskie zagrożenie - metal pozostaje standardem"
    },
    
    "industry_rivalry": {
      "force_strength": "high",
      "score": 8,
      "factors": [
        {
          "factor": "Liczba konkurentów",
          "assessment": "Wielu - krajowi + import",
          "intensity": "high"
        },
        {
          "factor": "Tempo wzrostu rynku",
          "assessment": "Umiarkowane 3-5% - walka o udziały",
          "intensity": "medium-high"
        },
        {
          "factor": "Zróżnicowanie produktów",
          "assessment": "Niskie w commodity, wyższe w specjalistycznych",
          "intensity": "high"
        },
        {
          "factor": "Koszty stałe",
          "assessment": "Wysokie - presja na wykorzystanie mocy",
          "intensity": "high"
        },
        {
          "factor": "Bariery wyjścia",
          "assessment": "Średnie - sprzęt specjalistyczny",
          "intensity": "medium"
        }
      ],
      "main_competitors": [
        {"name": "Konkurent A", "strategy": "Cost leadership"},
        {"name": "Konkurent B", "strategy": "Differentiation"},
        {"name": "Import Azja", "strategy": "Aggressive pricing"}
      ],
      "conclusion": "Intensywna rywalizacja, zwłaszcza cenowa"
    },
    
    "overall_analysis": {
      "industry_attractiveness": "moderate",
      "profitability_pressure": "medium-high",
      
      "forces_summary": {
        "threat_of_entrants": {"score": 5, "trend": "stable"},
        "supplier_power": {"score": 4, "trend": "stable"},
        "buyer_power": {"score": 7, "trend": "increasing"},
        "threat_of_substitutes": {"score": 3, "trend": "stable"},
        "industry_rivalry": {"score": 8, "trend": "increasing"}
      },
      
      "strongest_forces": [
        "Industry rivalry - intensywna konkurencja cenowa",
        "Buyer power - skoncentrowani dystrybutorzy"
      ],
      
      "weakest_forces": [
        "Threat of substitutes - brak realnych alternatyw",
        "Supplier power - wielu dostawców"
      ],
      
      "strategic_implications": [
        "Różnicowanie przez jakość/serwis kluczowe",
        "Budowanie relacji z dystrybutorami",
        "Unikanie wojny cenowej w commodity",
        "Fokus na segmenty specjalistyczne"
      ],
      
      "recommended_strategies": [
        {
          "strategy": "Differentiation",
          "rationale": "Ucieczka od konkurencji cenowej",
          "focus": "Innowacje, jakość, serwis"
        },
        {
          "strategy": "Focus",
          "rationale": "Specjalizacja w niszach",
          "focus": "Specific industries (OZE, farmacja)"
        }
      ]
    }
  }
}
```
```

---

## 4. BCG MATRIX

```markdown
# BCG GROWTH-SHARE MATRIX

## KIEDY STOSOWAĆ
- Analiza portfolio produktowego
- Alokacja zasobów między produkty/jednostki
- Decyzje o inwestycjach i wycofaniach
- Planowanie strategiczne portfolio

## DEFINICJE KWADRANTÓW

### STARS (Gwiazdy) ⭐
- Wysoki wzrost rynku + Wysoki udział
- Charakterystyka: Liderzy na rosnących rynkach
- Cash flow: Generują dużo, ale wymagają dużo (netto: neutral)
- Strategia: Inwestować w utrzymanie pozycji

### CASH COWS (Dojne krowy) 🐄
- Niski wzrost + Wysoki udział
- Charakterystyka: Liderzy na dojrzałych rynkach
- Cash flow: Generują znacznie więcej niż wymagają
- Strategia: Harvesting - maksymalizować cash flow

### QUESTION MARKS (Znaki zapytania) ❓
- Wysoki wzrost + Niski udział
- Charakterystyka: Pozycja do zbudowania lub porzucenia
- Cash flow: Wymagają dużo, generują mało
- Strategia: Inwestować selektywnie lub wyjść

### DOGS (Psy) 🐕
- Niski wzrost + Niski udział
- Charakterystyka: Słaba pozycja na stagnującym rynku
- Cash flow: Niski lub ujemny
- Strategia: Wycofać lub restrukturyzować

## METODOLOGIA

### Krok 1: Definiowanie jednostek analizy
- Linie produktowe
- Jednostki biznesowe
- Marki
- Rynki geograficzne

### Krok 2: Obliczenie współrzędnych

**Oś X - Względny udział rynkowy:**
Relative Market Share = Udział firmy / Udział największego konkurenta
- >1.0 = Lider rynkowy
- <1.0 = Follower

**Oś Y - Tempo wzrostu rynku:**
- Wysoki wzrost: >10% rocznie (lub > średnia branży)
- Niski wzrost: <10% (lub < średnia)
- Punkt podziału: często 10% lub średnia wzrostu całego portfolio

### Krok 3: Rozmiar bąbelków
- Proporcjonalny do przychodów lub zysku
- Pokazuje znaczenie jednostki w portfolio

## FORMAT WYJŚCIOWY

```json
{
  "bcg_matrix": {
    "company": "FADO Sp. z o.o.",
    "date": "2025-01-13",
    "analysis_period": "2024",
    
    "market_growth_threshold": 8,
    "relative_share_threshold": 1.0,
    
    "business_units": [
      {
        "name": "Zawory kulowe standard",
        "revenue_pln": 25000000,
        "revenue_share": "35%",
        "market_growth_rate": 4,
        "company_market_share": 18,
        "leader_market_share": 22,
        "relative_market_share": 0.82,
        "quadrant": "cash_cow",
        "position_x": 0.82,
        "position_y": 4,
        "bubble_size": 35,
        "assessment": "Silna pozycja na dojrzałym rynku",
        "recommended_strategy": "Harvest - optymalizuj koszty, maksymalizuj marżę",
        "investment_priority": "low",
        "cash_generation": "high"
      },
      {
        "name": "Armatura OZE",
        "revenue_pln": 8000000,
        "revenue_share": "11%",
        "market_growth_rate": 15,
        "company_market_share": 8,
        "leader_market_share": 25,
        "relative_market_share": 0.32,
        "quadrant": "question_mark",
        "position_x": 0.32,
        "position_y": 15,
        "bubble_size": 11,
        "assessment": "Obiecujący rynek, słaba pozycja",
        "recommended_strategy": "Invest or divest - zdecydować o przyszłości",
        "investment_priority": "high (if committed)",
        "cash_generation": "negative"
      },
      {
        "name": "Systemy przemysłowe premium",
        "revenue_pln": 18000000,
        "revenue_share": "25%",
        "market_growth_rate": 12,
        "company_market_share": 28,
        "leader_market_share": 28,
        "relative_market_share": 1.0,
        "quadrant": "star",
        "position_x": 1.0,
        "position_y": 12,
        "bubble_size": 25,
        "assessment": "Lider na rosnącym rynku",
        "recommended_strategy": "Invest - utrzymaj pozycję, buduj share",
        "investment_priority": "high",
        "cash_generation": "neutral"
      },
      {
        "name": "Zawory specjalistyczne (legacy)",
        "revenue_pln": 5000000,
        "revenue_share": "7%",
        "market_growth_rate": -2,
        "company_market_share": 12,
        "leader_market_share": 35,
        "relative_market_share": 0.34,
        "quadrant": "dog",
        "position_x": 0.34,
        "position_y": -2,
        "bubble_size": 7,
        "assessment": "Słaba pozycja na schyłkowym rynku",
        "recommended_strategy": "Divest or niche - rozważ wyjście lub specjalizację",
        "investment_priority": "none",
        "cash_generation": "low/negative"
      }
    ],
    
    "portfolio_summary": {
      "stars": {
        "count": 1,
        "revenue_share": "25%",
        "cash_implication": "Cash neutral"
      },
      "cash_cows": {
        "count": 1,
        "revenue_share": "35%",
        "cash_implication": "Cash generators"
      },
      "question_marks": {
        "count": 1,
        "revenue_share": "11%",
        "cash_implication": "Cash users"
      },
      "dogs": {
        "count": 1,
        "revenue_share": "7%",
        "cash_implication": "Cash trap"
      }
    },
    
    "strategic_recommendations": {
      "invest": [
        "Systemy przemysłowe premium - utrzymaj leadership",
        "Armatura OZE - zwiększ inwestycje jeśli committed"
      ],
      "maintain": [
        "Zawory kulowe standard - optymalizuj, nie inwestuj"
      ],
      "divest": [
        "Zawory specjalistyczne legacy - rozważ wyjście"
      ],
      "watch": [
        "Armatura OZE - decyzja w ciągu 12 mies."
      ]
    },
    
    "portfolio_balance": {
      "assessment": "Umiarkowanie zrównoważone",
      "strengths": "Silna cash cow i star",
      "weaknesses": "Duży question mark wymaga decyzji",
      "future_risk": "Zależność od jednej cash cow"
    }
  }
}
```

## WIZUALIZACJA

```
                    HIGH MARKET GROWTH
                          ↑
        QUESTION MARKS    |    STARS
        ❓                |    ⭐
        Armatura OZE      |    Systemy premium
        (11%, RMS 0.32)   |    (25%, RMS 1.0)
                          |
    LOW ←─────────────────┼─────────────────→ HIGH
    RELATIVE              |              RELATIVE
    MARKET SHARE          |              MARKET SHARE
                          |
        DOGS              |    CASH COWS
        🐕                |    🐄
        Zawory legacy     |    Zawory standard
        (7%, RMS 0.34)    |    (35%, RMS 0.82)
                          |
                          ↓
                    LOW MARKET GROWTH
```
```

---

## 5. ANSOFF MATRIX

```markdown
# ANSOFF GROWTH MATRIX

## KIEDY STOSOWAĆ
- Planowanie strategii wzrostu
- Ocena opcji ekspansji
- Dywersyfikacja portfolio
- Planowanie wejścia na nowe rynki

## STRUKTURA MATRYCY

```
                     PRODUKTY
                 Istniejące    Nowe
              ┌─────────────┬─────────────┐
    Istniejące│   MARKET    │  PRODUCT    │
              │ PENETRATION │ DEVELOPMENT │
    RYNKI     │   (Niskie   │  (Średnie   │
              │   ryzyko)   │   ryzyko)   │
              ├─────────────┼─────────────┤
       Nowe   │   MARKET    │DIVERSIFI-   │
              │ DEVELOPMENT │  CATION     │
              │  (Średnie   │  (Wysokie   │
              │   ryzyko)   │   ryzyko)   │
              └─────────────┴─────────────┘
```

## STRATEGIE SZCZEGÓŁOWO

### 1. MARKET PENETRATION (Penetracja Rynku)
Istniejące produkty → Istniejące rynki

Taktyki:
- Zwiększenie udziału rynkowego
- Zwiększenie częstotliwości zakupów
- Pozyskanie klientów konkurencji
- Intensyfikacja marketingu
- Programy lojalnościowe
- Optymalizacja cenowa

Ryzyko: NISKIE
Typowy wzrost: 5-15%

### 2. PRODUCT DEVELOPMENT (Rozwój Produktu)
Nowe produkty → Istniejące rynki

Taktyki:
- Innowacje produktowe
- Rozszerzenie linii produktowej
- Nowe funkcjonalności
- Nowe warianty/wersje
- Ulepszenia jakościowe
- Private label dla partnerów

Ryzyko: ŚREDNIE
Typowy wzrost: 10-25%

### 3. MARKET DEVELOPMENT (Rozwój Rynku)
Istniejące produkty → Nowe rynki

Taktyki:
- Ekspansja geograficzna
- Nowe segmenty klientów
- Nowe kanały dystrybucji
- Nowe zastosowania produktu
- Eksport

Ryzyko: ŚREDNIE
Typowy wzrost: 15-30%

### 4. DIVERSIFICATION (Dywersyfikacja)
Nowe produkty → Nowe rynki

Typy:
- Related (pokrewna) - synergie z core business
- Unrelated (niepokrewna) - czysta dywersyfikacja

Taktyki:
- Akwizycje
- Joint ventures
- Rozwój organiczny
- Licencje

Ryzyko: WYSOKIE
Typowy wzrost: 20-50%+

## FORMAT WYJŚCIOWY

```json
{
  "ansoff_analysis": {
    "company": "FADO Sp. z o.o.",
    "date": "2025-01-13",
    "current_revenue": 72000000,
    "growth_target": "15% w ciągu 3 lat",
    
    "strategies": {
      "market_penetration": {
        "current_applicability": "high",
        "risk_level": "low",
        "investment_required": "low-medium",
        "time_to_results": "6-12 months",
        
        "initiatives": [
          {
            "initiative": "Zwiększenie udziału u istniejących dystrybutorów",
            "description": "Programy partnerskie, szkolenia, wsparcie marketingowe",
            "estimated_impact": "+5% revenue",
            "investment": 500000,
            "timeline": "12 months",
            "probability_of_success": "80%"
          },
          {
            "initiative": "Pozyskanie klientów konkurencji",
            "description": "Targetowana kampania do klientów Konkurenta X",
            "estimated_impact": "+3% revenue",
            "investment": 300000,
            "timeline": "18 months",
            "probability_of_success": "60%"
          },
          {
            "initiative": "Cross-selling do bazy klientów",
            "description": "Sprzedaż dodatkowych kategorii",
            "estimated_impact": "+2% revenue",
            "investment": 100000,
            "timeline": "6 months",
            "probability_of_success": "75%"
          }
        ],
        
        "total_potential": "+10% revenue",
        "total_investment": 900000,
        "recommendation": "PROCEED - niskie ryzyko, solidny zwrot"
      },
      
      "product_development": {
        "current_applicability": "medium-high",
        "risk_level": "medium",
        "investment_required": "medium-high",
        "time_to_results": "12-24 months",
        
        "initiatives": [
          {
            "initiative": "Linia produktów Smart/IoT",
            "description": "Zawory z czujnikami i łącznością",
            "estimated_impact": "+8% revenue",
            "investment": 2000000,
            "timeline": "24 months",
            "probability_of_success": "60%"
          },
          {
            "initiative": "Rozszerzenie portfolio OZE",
            "description": "Armatura dla pomp ciepła, fotowoltaiki",
            "estimated_impact": "+5% revenue",
            "investment": 1000000,
            "timeline": "18 months",
            "probability_of_success": "70%"
          }
        ],
        
        "total_potential": "+13% revenue",
        "total_investment": 3000000,
        "recommendation": "SELECTIVE - priorytet OZE, IoT jako opcja"
      },
      
      "market_development": {
        "current_applicability": "medium",
        "risk_level": "medium",
        "investment_required": "high",
        "time_to_results": "18-36 months",
        
        "initiatives": [
          {
            "initiative": "Ekspansja DACH (Niemcy, Austria, Szwajcaria)",
            "description": "Wejście przez partnerów dystrybucyjnych",
            "estimated_impact": "+12% revenue",
            "investment": 3000000,
            "timeline": "36 months",
            "probability_of_success": "55%"
          },
          {
            "initiative": "Segment farmaceutyczny w Polsce",
            "description": "Certyfikacja i sprzedaż do pharma",
            "estimated_impact": "+4% revenue",
            "investment": 800000,
            "timeline": "24 months",
            "probability_of_success": "65%"
          }
        ],
        
        "total_potential": "+16% revenue",
        "total_investment": 3800000,
        "recommendation": "SELECTIVE - DACH ambitne, pharma bezpieczniejsze"
      },
      
      "diversification": {
        "current_applicability": "low",
        "risk_level": "high",
        "investment_required": "very high",
        "time_to_results": "24-48 months",
        
        "initiatives": [
          {
            "initiative": "Akwizycja producenta systemów rurowych",
            "description": "Rozszerzenie oferty o kompletne systemy",
            "estimated_impact": "+20% revenue",
            "investment": 10000000,
            "timeline": "24 months",
            "probability_of_success": "40%"
          }
        ],
        
        "total_potential": "+20% revenue",
        "total_investment": 10000000,
        "recommendation": "NOT RECOMMENDED - zbyt wysokie ryzyko vs core"
      }
    },
    
    "recommended_portfolio": {
      "priority_1": {
        "strategy": "Market Penetration",
        "allocation": "30%",
        "expected_return": "+10%",
        "risk": "low"
      },
      "priority_2": {
        "strategy": "Product Development (OZE)",
        "allocation": "40%",
        "expected_return": "+5-8%",
        "risk": "medium"
      },
      "priority_3": {
        "strategy": "Market Development (Pharma)",
        "allocation": "30%",
        "expected_return": "+4%",
        "risk": "medium"
      },
      "not_recommended": "Diversification - focus on core"
    },
    
    "growth_path": {
      "year_1": "+6-8% (penetration + quick wins)",
      "year_2": "+8-12% (product development kicks in)",
      "year_3": "+12-15% (full portfolio effect)",
      "3_year_total": "+28-35%"
    },
    
    "risk_mitigation": [
      "Stage-gate process dla development",
      "Pilot markets przed full rollout",
      "Partnership model dla nowych rynków"
    ]
  }
}
```
```

---

## 6. CHOOSING THE RIGHT FRAMEWORK

```markdown
# FRAMEWORK SELECTION GUIDE

## Kiedy używać którego frameworka:

| Sytuacja | Rekomendowany Framework |
|----------|-------------------------|
| Analiza pozycji firmy | SWOT |
| Wejście na nowy rynek | PESTLE + Porter |
| Analiza branży | Porter's Five Forces |
| Alokacja zasobów w portfolio | BCG Matrix |
| Planowanie wzrostu | Ansoff Matrix |
| Due diligence | SWOT + Porter + Financial |
| Planowanie strategiczne | Wszystkie w kombinacji |

## Łączenie frameworków

### Pełna analiza strategiczna:
1. PESTLE → zrozum makrootoczenie
2. Porter → zrozum branżę
3. SWOT → zrozum pozycję firmy
4. BCG → zrozum portfolio
5. Ansoff → zaplanuj wzrost

### Quick competitive assessment:
1. SWOT
2. Porter (uproszczony)

### Market entry analysis:
1. PESTLE
2. Porter
3. Ansoff
```

---

*Następny dokument: 09_FRAMEWORKS_OPERATIONAL.md*