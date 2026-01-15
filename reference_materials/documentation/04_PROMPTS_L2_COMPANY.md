# 04. Prompty Level 2 - Company Intelligence

## Przegląd

Level 2 prompty to **szczegółowe instrukcje dla poszczególnych agentów** 
odpowiedzialnych za zbieranie i analizę danych o firmach.

Agenci w tym module:
1. **Company Profile Agent** - dane podstawowe, rejestrowe
2. **Financial Analysis Agent** - dane finansowe, wskaźniki
3. **Ownership Mapping Agent** - struktura właścicielska
4. **Digital Presence Agent** - obecność online
5. **Key People Agent** - kadra zarządzająca
6. **News & Sentiment Agent** - wzmianki i sentyment

---

## 1. COMPANY PROFILE AGENT

```markdown
# COMPANY PROFILE ANALYSIS - Task Prompt

## ZADANIE
Zbierz i ustrukturyzuj kompleksowe informacje o firmie.

## DANE DO ZEBRANIA

### A. Dane Identyfikacyjne (WYMAGANE)
| Pole | Źródło | Priorytet |
|------|--------|-----------|
| Pełna nazwa prawna | KRS/CEIDG | CRITICAL |
| Forma prawna | KRS | CRITICAL |
| NIP | KRS/CEIDG | CRITICAL |
| REGON | KRS/CEIDG | HIGH |
| KRS (jeśli dotyczy) | KRS | HIGH |
| Data rejestracji | KRS/CEIDG | MEDIUM |
| Adres siedziby | KRS/CEIDG | HIGH |
| Adresy oddziałów | KRS | LOW |

### B. Działalność (WYMAGANE)
| Pole | Źródło | Priorytet |
|------|--------|-----------|
| Główne PKD | KRS | HIGH |
| Pozostałe PKD | KRS | MEDIUM |
| Opis działalności | Website + KRS | HIGH |
| Produkty/usługi | Website | HIGH |
| Branża | Inference | HIGH |
| Model biznesowy | Website/Analysis | MEDIUM |

### C. Skala Działalności (JEŚLI DOSTĘPNE)
| Pole | Źródło | Priorytet |
|------|--------|-----------|
| Kapitał zakładowy | KRS | MEDIUM |
| Przychody (ostatni rok) | Sprawozdania | HIGH |
| Liczba pracowników | LinkedIn/GUS | HIGH |
| Zasięg geograficzny | Website | MEDIUM |

## ŹRÓDŁA DANYCH (w kolejności priorytetów)

### Źródła Oficjalne
1. **KRS API** - dane rejestrowe spółek
   - Endpoint: https://api-krs.ms.gov.pl
   - Dane: nazwa, forma, adresy, PKD, kapitał, zarząd
   
2. **CEIDG** - jednoosobowe działalności
   - Endpoint: https://dane.biznes.gov.pl/api/ceidg
   - Dane: nazwa, właściciel, adres, PKD

3. **Rejestr.io** - enriched data
   - Dane: finanse, powiązania, historia

### Źródła Internetowe
4. **Website** - strona firmowa
   - Crawl: /o-nas, /about, /kontakt
   - Dane: opis, produkty, zespół

5. **LinkedIn Company Page**
   - Dane: pracownicy, opis, branża

6. **Google/Web Search**
   - Dane: artykuły, wzmianki

## PROCEDURA

### Krok 1: Identyfikacja Firmy
```
INPUT: nazwa firmy (może być niepełna)

1. Wyszukaj w KRS po nazwie
2. Jeśli brak - sprawdź CEIDG
3. Jeśli wiele wyników - poproś o doprecyzowanie
4. Potwierdź identyfikację (NIP, adres)
```

### Krok 2: Pobierz Dane Rejestrowe
```
1. Wywołaj KRS API z numerem KRS
2. Zapisz: nazwa, forma, adres, PKD, kapitał
3. Pobierz listę członków zarządu
4. Pobierz historię wpisów (jeśli dostępna)
```

### Krok 3: Wzbogać z Website
```
1. Zidentyfikuj oficjalną stronę
2. Crawluj kluczowe sekcje
3. Ekstraheluj: produkty, opis, kontakty
4. Wykryj technologie (jeśli relevantne)
```

### Krok 4: Uzupełnij Luki
```
1. Sprawdź LinkedIn dla brakujących danych
2. Web search dla kontekstu branżowego
3. Oznacz pola bez danych jako "brak danych"
```

## FORMAT WYJŚCIOWY

```json
{
  "company_profile": {
    "identification": {
      "legal_name": "FADO Spółka z ograniczoną odpowiedzialnością",
      "trade_name": "FADO",
      "legal_form": "sp. z o.o.",
      "nip": "9532648925",
      "regon": "092461388",
      "krs": "0000123456",
      "registration_date": "1995-03-15",
      "registration_court": "Sąd Rejonowy w Bydgoszczy"
    },
    "location": {
      "headquarters": {
        "street": "ul. Przemysłowa 10",
        "city": "Bydgoszcz",
        "postal_code": "85-758",
        "country": "Polska"
      },
      "branches": []
    },
    "business": {
      "main_pkd": {
        "code": "28.14.Z",
        "description": "Produkcja pozostałych kurków i zaworów"
      },
      "other_pkd": ["46.74.Z", "33.12.Z"],
      "description": "Producent armatury przemysłowej...",
      "products_services": [
        "Zawory kulowe",
        "Armatura do instalacji",
        "Systemy rurociągowe"
      ],
      "industry": "Armatura przemysłowa",
      "business_model": "B2B",
      "geographic_scope": "Polska, Europa"
    },
    "scale": {
      "share_capital": 5000000,
      "share_capital_currency": "PLN",
      "employees_range": "200-500",
      "revenue_last_year": null,
      "revenue_source": null
    },
    "metadata": {
      "data_collected_at": "2025-01-13T14:30:00Z",
      "sources_used": ["KRS", "company_website", "LinkedIn"],
      "confidence_score": 0.92,
      "data_gaps": ["revenue_last_year"],
      "last_krs_update": "2024-06-15"
    }
  }
}
```

## WERYFIKACJA JAKOŚCI

Przed zwróceniem wyniku, sprawdź:
- [ ] NIP ma poprawny format i cyfrę kontrolną
- [ ] KRS ma 10 cyfr
- [ ] Adres jest kompletny
- [ ] PKD jest aktualne (nie wycofane)
- [ ] Dane z różnych źródeł są spójne
- [ ] Brakujące pola są oznaczone

## FLAGI I OSTRZEŻENIA

Zgłoś gdy wykryjesz:
- `COMPANY_IN_LIQUIDATION` - firma w likwidacji
- `COMPANY_BANKRUPT` - firma w upadłości
- `DATA_OUTDATED` - dane starsze niż 1 rok
- `MULTIPLE_MATCHES` - niejednoznaczna identyfikacja
- `LIMITED_DATA` - mało dostępnych informacji
```

---

## 2. FINANCIAL ANALYSIS AGENT

```markdown
# FINANCIAL ANALYSIS - Task Prompt

## ZADANIE
Przeanalizuj kondycję finansową firmy na podstawie dostępnych źródeł.

## DANE DO ZEBRANIA

### A. Sprawozdania Finansowe
| Pole | Źródło | Lata |
|------|--------|------|
| Przychody ze sprzedaży | Sprawozdanie | 3 ostatnie |
| Zysk/strata netto | Sprawozdanie | 3 ostatnie |
| Suma bilansowa | Bilans | 3 ostatnie |
| Kapitał własny | Bilans | 3 ostatnie |
| Zobowiązania | Bilans | 3 ostatnie |

### B. Wskaźniki do Obliczenia
| Wskaźnik | Wzór | Interpretacja |
|----------|------|---------------|
| Rentowność netto | Zysk netto / Przychody | >5% dobra |
| ROE | Zysk netto / Kapitał własny | >15% dobra |
| Wskaźnik zadłużenia | Zobowiązania / Aktywa | <50% bezpieczny |
| Płynność bieżąca | Aktywa obrotowe / Zobow. krótkoterm. | >1.5 dobra |

### C. Trendy
| Analiza | Metoda |
|---------|--------|
| Dynamika przychodów | YoY % |
| Dynamika zysku | YoY % |
| Trend zadłużenia | 3-letni kierunek |

## ŹRÓDŁA DANYCH

### Bezpłatne
1. **e-KRS** - sprawozdania finansowe (PDF)
   - Dostępne dla spółek handlowych
   - Opóźnienie: 6-12 miesięcy
   
2. **Monitor Polski B** (historyczne)
   - Starsze sprawozdania

### Płatne
3. **InfoVeriti** - przetworzone dane finansowe
4. **Bisnode/Dun&Bradstreet** - rating kredytowy
5. **EMIS** - raporty branżowe

## PROCEDURA

### Krok 1: Pobierz Sprawozdania
```
1. Sprawdź dostępność w e-KRS
2. Pobierz PDF sprawozdania za ostatnie 3 lata
3. Wyekstrahuj kluczowe pozycje
4. Jeśli brak - oznacz i poszukaj alternatyw
```

### Krok 2: Oblicz Wskaźniki
```
1. Rentowność: netto, brutto, operacyjna
2. Płynność: bieżąca, szybka
3. Zadłużenie: ogólne, długoterminowe
4. Efektywność: rotacja należności, zapasów
```

### Krok 3: Analiza Trendów
```
1. Oblicz dynamikę rok do roku
2. Zidentyfikuj trendy 3-letnie
3. Porównaj z branżą (jeśli dane dostępne)
4. Wyciągnij wnioski
```

## FORMAT WYJŚCIOWY

```json
{
  "financial_analysis": {
    "company_id": "KRS:0000123456",
    "analysis_date": "2025-01-13",
    "data_period": "2021-2023",
    
    "income_statement": {
      "revenue": {
        "2023": 45000000,
        "2022": 42000000,
        "2021": 38000000,
        "currency": "PLN"
      },
      "net_profit": {
        "2023": 3200000,
        "2022": 2800000,
        "2021": 2100000
      },
      "yoy_growth": {
        "revenue": "7.1%",
        "profit": "14.3%"
      }
    },
    
    "balance_sheet": {
      "total_assets": 28000000,
      "equity": 15000000,
      "liabilities": 13000000,
      "current_assets": 12000000,
      "current_liabilities": 6000000
    },
    
    "ratios": {
      "profitability": {
        "net_margin": "7.1%",
        "roe": "21.3%",
        "roa": "11.4%",
        "assessment": "powyżej średniej branżowej"
      },
      "liquidity": {
        "current_ratio": 2.0,
        "quick_ratio": 1.4,
        "assessment": "dobra płynność"
      },
      "leverage": {
        "debt_ratio": "46.4%",
        "debt_to_equity": 0.87,
        "assessment": "umiarkowane zadłużenie"
      }
    },
    
    "trends": {
      "revenue_trend": "rosnący",
      "profit_trend": "rosnący",
      "debt_trend": "stabilny"
    },
    
    "overall_assessment": {
      "financial_health": "dobra",
      "growth_potential": "wysoki",
      "risk_level": "niski",
      "key_strengths": [
        "Stabilny wzrost przychodów",
        "Rosnąca rentowność",
        "Dobra płynność"
      ],
      "key_concerns": [
        "Rosnące zobowiązania handlowe"
      ]
    },
    
    "metadata": {
      "data_source": "e-KRS sprawozdania finansowe",
      "data_freshness": "2023 (ostatnie dostępne)",
      "confidence": "high",
      "limitations": ["Brak danych za 2024"]
    }
  }
}
```

## INTERPRETACJE BRANŻOWE

Dostosuj ocenę do branży:
- **Produkcja** - marże 5-15%, zadłużenie <60%
- **Handel** - marże 2-5%, wysoka rotacja
- **Usługi** - marże 10-25%, niskie aktywa trwałe
- **IT/SaaS** - straty na początku OK, ważny wzrost
```

---

## 3. OWNERSHIP MAPPING AGENT

```markdown
# OWNERSHIP MAPPING - Task Prompt

## ZADANIE
Zmapuj strukturę właścicielską firmy i powiązania kapitałowe.

## DANE DO ZEBRANIA

### A. Udziałowcy/Akcjonariusze
| Pole | Opis |
|------|------|
| Nazwa/imię | Kto jest udziałowcem |
| Udział % | Procent udziałów |
| Typ | Osoba fizyczna / prawna |
| Kraj | Rezydencja / siedziba |

### B. Beneficjenci Rzeczywiści
| Pole | Opis |
|------|------|
| Imię i nazwisko | Osoba fizyczna |
| Charakter kontroli | Bezpośredni / pośredni |
| % kontroli | Jeśli znany |

### C. Spółki Powiązane
| Typ powiązania | Opis |
|----------------|------|
| Spółki zależne | Firma jest właścicielem |
| Spółki nadrzędne | Właściciele firmy |
| Spółki siostrzane | Wspólny właściciel |

## ŹRÓDŁA

1. **KRS** - udziałowcy w sp. z o.o., akcjonariusze w S.A.
2. **CRBR** - Centralny Rejestr Beneficjentów Rzeczywistych
3. **Rejestr.io** - powiązania, grafy
4. **OpenCorporates** - dane międzynarodowe

## FORMAT WYJŚCIOWY

```json
{
  "ownership_structure": {
    "company": "FADO Sp. z o.o.",
    "krs": "0000123456",
    
    "shareholders": [
      {
        "name": "Jan Kowalski",
        "type": "person",
        "share_percent": 60,
        "share_capital": 3000000,
        "country": "PL"
      },
      {
        "name": "ABC Holdings Ltd",
        "type": "company",
        "share_percent": 40,
        "jurisdiction": "UK",
        "registration_number": "12345678"
      }
    ],
    
    "beneficial_owners": [
      {
        "name": "Jan Kowalski",
        "control_type": "direct",
        "control_percent": 60
      },
      {
        "name": "Maria Smith",
        "control_type": "indirect",
        "control_percent": 40,
        "via": "ABC Holdings Ltd"
      }
    ],
    
    "related_companies": {
      "subsidiaries": [
        {
          "name": "FADO Export Sp. z o.o.",
          "krs": "0000234567",
          "ownership_percent": 100
        }
      ],
      "parent_companies": [],
      "sister_companies": [
        {
          "name": "ABC Manufacturing Sp. z o.o.",
          "common_owner": "Jan Kowalski"
        }
      ]
    },
    
    "ownership_graph": {
      "nodes": [...],
      "edges": [...]
    },
    
    "flags": [],
    "metadata": {
      "source": "KRS + CRBR",
      "updated": "2025-01-13"
    }
  }
}
```

## FLAGI DO ZGŁOSZENIA

- `OFFSHORE_OWNER` - właściciel w jurysdykcji offshore
- `COMPLEX_STRUCTURE` - wielopoziomowa struktura
- `RECENT_CHANGES` - zmiany w ostatnich 6 miesiącach
- `POLITICIAN_CONNECTION` - powiązania z PEP
- `CROSS_OWNERSHIP` - wzajemne udziały
```

---

## 4. DIGITAL PRESENCE AGENT

```markdown
# DIGITAL PRESENCE ANALYSIS - Task Prompt

## ZADANIE
Oceń obecność cyfrową firmy i jej pozycję online.

## DANE DO ZEBRANIA

### A. Strona Internetowa
| Metryka | Źródło |
|---------|--------|
| Domena | WHOIS |
| Tech stack | BuiltWith |
| Ruch miesięczny | SimilarWeb |
| Bounce rate | SimilarWeb |
| Czas na stronie | SimilarWeb |

### B. SEO & Content
| Metryka | Źródło |
|---------|--------|
| Domain Authority | Moz/Ahrefs |
| Backlinks | Ahrefs |
| Top keywords | SimilarWeb |
| Blog/content | Website crawl |

### C. Social Media
| Platforma | Metryki |
|-----------|---------|
| LinkedIn | Followers, employees, engagement |
| Facebook | Fans, engagement |
| YouTube | Subscribers, views |
| Instagram | Followers |
| Twitter/X | Followers |

### D. Recenzje Online
| Źródło | Metryki |
|--------|---------|
| Google Maps | Rating, count |
| Facebook | Rating |
| Branżowe portale | Opinie |

## FORMAT WYJŚCIOWY

```json
{
  "digital_presence": {
    "company": "FADO Sp. z o.o.",
    
    "website": {
      "domain": "fado.pl",
      "domain_age_years": 15,
      "ssl": true,
      "tech_stack": ["WordPress", "WooCommerce", "PHP"],
      "traffic": {
        "monthly_visits": 45000,
        "bounce_rate": "42%",
        "avg_duration": "2:30",
        "pages_per_visit": 3.2
      },
      "traffic_sources": {
        "organic": "55%",
        "direct": "25%",
        "referral": "15%",
        "social": "5%"
      },
      "top_pages": [
        "/produkty/zawory-kulowe",
        "/katalog",
        "/kontakt"
      ]
    },
    
    "seo": {
      "domain_authority": 35,
      "backlinks_count": 1200,
      "referring_domains": 180,
      "top_keywords": [
        {"keyword": "zawory kulowe", "position": 3},
        {"keyword": "armatura przemysłowa", "position": 8}
      ]
    },
    
    "social_media": {
      "linkedin": {
        "url": "linkedin.com/company/fado",
        "followers": 2500,
        "employees_on_linkedin": 120,
        "engagement_rate": "2.1%"
      },
      "facebook": {
        "url": "facebook.com/fadopl",
        "fans": 5800,
        "rating": 4.6,
        "reviews_count": 45
      },
      "youtube": null,
      "instagram": null
    },
    
    "reviews": {
      "google_maps": {
        "rating": 4.5,
        "reviews_count": 28
      },
      "overall_sentiment": "positive"
    },
    
    "digital_score": {
      "overall": 72,
      "website": 75,
      "seo": 65,
      "social": 70,
      "reputation": 80
    },
    
    "recommendations": [
      "Zwiększyć aktywność na LinkedIn",
      "Rozważyć obecność na YouTube",
      "Poprawić mobile UX"
    ]
  }
}
```
```

---

## 5. KEY PEOPLE AGENT

```markdown
# KEY PEOPLE ANALYSIS - Task Prompt

## ZADANIE
Zidentyfikuj kluczowe osoby w firmie i ich background.

## DANE DO ZEBRANIA

### Zarząd i Rada Nadzorcza (z KRS)
- Imię i nazwisko
- Funkcja
- Data powołania
- Kadencja

### Kluczowi Menedżerowie (z LinkedIn/Website)
- C-level executives
- Dyrektorzy działów
- Kluczowi specjaliści

### Background Check (dla każdej osoby)
- Historia zawodowa
- Wykształcenie
- Inne spółki w zarządach
- Publikacje/wypowiedzi

## FORMAT WYJŚCIOWY

```json
{
  "key_people": {
    "management_board": [
      {
        "name": "Jan Kowalski",
        "role": "Prezes Zarządu",
        "appointed": "2018-03-15",
        "tenure_years": 7,
        "background": {
          "previous_roles": [
            {"company": "ABC S.A.", "role": "VP Sales", "years": "2010-2018"}
          ],
          "education": "Politechnika Gdańska, Inżynieria Mechaniczna",
          "other_boards": ["XYZ Sp. z o.o."]
        },
        "linkedin": "linkedin.com/in/jankowalski",
        "public_profile": "Aktywny speaker na konferencjach branżowych"
      }
    ],
    "supervisory_board": [...],
    "key_executives": [...],
    
    "summary": {
      "management_stability": "wysoka",
      "industry_experience": "głęboka",
      "network_strength": "średnia"
    }
  }
}
```
```

---

## 6. NEWS & SENTIMENT AGENT

```markdown
# NEWS & SENTIMENT ANALYSIS - Task Prompt

## ZADANIE
Zbierz i przeanalizuj wzmianki o firmie w mediach.

## ŹRÓDŁA

1. **Google News** - artykuły newsowe
2. **Branżowe portale** - np. plastech.pl dla tworzyw
3. **Social media** - wzmianki i dyskusje
4. **Komunikaty prasowe** - oficjalne oświadczenia

## ANALIZA

### Ilościowa
- Liczba wzmianek (30/90/365 dni)
- Trend (rosnący/malejący/stabilny)
- Share of voice vs konkurenci

### Jakościowa
- Sentyment (positive/neutral/negative)
- Główne tematy
- Kluczowe wydarzenia

## FORMAT WYJŚCIOWY

```json
{
  "news_analysis": {
    "company": "FADO Sp. z o.o.",
    "period": "ostatnie 90 dni",
    
    "quantitative": {
      "total_mentions": 45,
      "trend": "rosnący",
      "by_source": {
        "news": 20,
        "industry_portals": 15,
        "social": 10
      }
    },
    
    "sentiment": {
      "positive": 60,
      "neutral": 35,
      "negative": 5,
      "overall": "positive"
    },
    
    "key_topics": [
      {"topic": "Nowy produkt", "mentions": 12, "sentiment": "positive"},
      {"topic": "Ekspansja", "mentions": 8, "sentiment": "positive"}
    ],
    
    "notable_articles": [
      {
        "title": "FADO wprowadza nową linię zaworów",
        "source": "Plastech.pl",
        "date": "2025-01-05",
        "sentiment": "positive",
        "url": "https://..."
      }
    ],
    
    "alerts": []
  }
}
```
```

---

*Następny dokument: 05_PROMPTS_L2_MARKET.md*
