"""
Companies API Endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException, Response
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Financial Data Models
class FinancialStatement(BaseModel):
    year: int
    revenue: float  # PLN
    net_profit: float  # PLN
    total_assets: float  # PLN
    total_equity: float  # PLN
    total_liabilities: float  # PLN
    current_assets: float  # PLN
    current_liabilities: float  # PLN
    inventory: float  # PLN
    accounts_receivable: float  # PLN


class FinancialRatios(BaseModel):
    year: int
    roe: float  # Return on Equity (%)
    roa: float  # Return on Assets (%)
    ros: float  # Return on Sales (%)
    current_ratio: float  # Current Ratio
    quick_ratio: float  # Quick Ratio
    debt_ratio: float  # Debt Ratio (%)
    debt_to_equity: float  # Debt to Equity
    inventory_turnover: float  # times per year
    dso: int  # Days Sales Outstanding (days)


class IndustryBenchmark(BaseModel):
    metric_name: str
    company_value: float
    industry_average: float
    industry_median: float
    percentile: int  # Company's percentile rank (0-100)
    comparison: str  # "above_average", "average", "below_average"


class IndustryBenchmarks(BaseModel):
    industry: str  # e.g., "Plastics Manufacturing (PKD 22.2)"
    year: int
    source: str  # e.g., "GUS Statistical Yearbook 2023"
    source_url: Optional[str] = None
    metrics: List[IndustryBenchmark]


class CompanyFinancials(BaseModel):
    company_id: str
    company_name: str
    statements: List[FinancialStatement]
    ratios: List[FinancialRatios]
    industry_benchmarks: Optional[IndustryBenchmarks] = None


# News Article Model
class NewsArticle(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    source_url: str
    published_at: str
    sentiment: str  # positive, negative, neutral
    category: str  # general, financial, product, hr, legal


class CompanyNews(BaseModel):
    company_id: str
    company_name: str
    news: List[NewsArticle]
    total_count: int


class TimelineEvent(BaseModel):
    id: str
    date: str  # ISO format date
    title: str
    description: str
    event_type: str  # founding, investment, partnership, product, legal, hr, milestone
    impact: str  # high, medium, low
    source: Optional[str] = None
    source_url: Optional[str] = None


class CompanyTimeline(BaseModel):
    company_id: str
    company_name: str
    events: List[TimelineEvent]
    total_count: int


class RelatedCompany(BaseModel):
    id: str
    name: str
    nip: str
    krs: Optional[str] = None
    relationship: str  # "subsidiary", "parent", "sister", "affiliate"
    ownership_percentage: Optional[float] = None
    description: Optional[str] = None


class CompanyProfile(BaseModel):
    id: str
    name: str
    nip: str
    krs: str
    regon: str
    address: dict
    pkd_codes: List[str]
    pkd_descriptions: List[dict]
    status: str
    founded: str
    description: Optional[str] = None
    website: Optional[str] = None
    employees_range: Optional[str] = None
    last_updated: Optional[str] = None  # ISO timestamp of last data refresh
    related_companies: Optional[List[RelatedCompany]] = []


# Data Quality Models
class DataQualityMetric(BaseModel):
    score: float  # 0-100
    status: str  # excellent, good, fair, poor
    details: List[dict]  # detailed breakdown


class DataQualityDashboard(BaseModel):
    company_id: str
    company_name: str
    overall_score: float  # 0-100
    overall_status: str  # excellent, good, fair, poor
    completeness: DataQualityMetric
    freshness: DataQualityMetric
    source_reliability: DataQualityMetric
    improvement_suggestions: List[dict]
    last_assessment: str  # ISO timestamp


# Mock news data for companies
MOCK_COMPANY_NEWS = {
    "1": [  # FADO Sp. z o.o.
        {
            "id": "news_001",
            "title": "FADO rozszerza moce produkcyjne o 30%",
            "summary": "Firma FADO Sp. z o.o. ogłosiła inwestycję o wartości 15 mln PLN w nową linię produkcyjną do tworzyw sztucznych. Rozbudowa zakładu ma zostać zakończona do końca Q2 2026.",
            "source": "Puls Biznesu",
            "source_url": "https://www.pb.pl/fado-rozbudowa-123456",
            "published_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "sentiment": "positive",
            "category": "financial"
        },
        {
            "id": "news_002",
            "title": "FADO podpisuje umowę z niemieckim partnerem",
            "summary": "FADO Sp. z o.o. zawarła strategiczną umowę partnerską z German Plastics GmbH na dostawy komponentów do sektora motoryzacyjnego. Umowa opiewa na 50 mln EUR w ciągu 3 lat.",
            "source": "Rzeczpospolita",
            "source_url": "https://www.rp.pl/fado-umowa-niemcy",
            "published_at": (datetime.now() - timedelta(days=5)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        },
        {
            "id": "news_003",
            "title": "Nowy dyrektor operacyjny w FADO",
            "summary": "Jan Nowak obejmuje stanowisko COO w FADO Sp. z o.o. Posiada 20-letnie doświadczenie w branży tworzyw sztucznych, wcześniej pracował w Splast S.A.",
            "source": "Money.pl",
            "source_url": "https://www.money.pl/fado-nowy-coo",
            "published_at": (datetime.now() - timedelta(days=8)).isoformat(),
            "sentiment": "neutral",
            "category": "hr"
        },
        {
            "id": "news_004",
            "title": "FADO prezentuje innowacyjne rozwiązania biodegradowalne",
            "summary": "Na targach Plastpol 2026 firma FADO zaprezentowała nową linię opakowań biodegradowalnych z tworzyw roślinnych. Produkt ma szansę na certyfikat OK Compost.",
            "source": "Tworzywa.pl",
            "source_url": "https://www.tworzywa.pl/fado-bio-plastpol",
            "published_at": (datetime.now() - timedelta(days=12)).isoformat(),
            "sentiment": "positive",
            "category": "product"
        },
        {
            "id": "news_005",
            "title": "FADO wśród liderów branży tworzyw sztucznych",
            "summary": "Raport roczny Polskiego Związku Przetwórców Tworzyw Sztucznych wyróżnia FADO jako jednego z najbardziej innowacyjnych producentów w Polsce.",
            "source": "Parkiet",
            "source_url": "https://www.parkiet.com/fado-lider-ranking",
            "published_at": (datetime.now() - timedelta(days=20)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        },
        {
            "id": "news_006",
            "title": "FADO przyznaje się do przekroczenia norm emisji",
            "summary": "Wojewódzki Inspektorat Ochrony Środowiska nałożył na FADO Sp. z o.o. karę w wysokości 200 tys. PLN za przekroczenie dopuszczalnych norm emisji. Firma zapowiada wdrożenie nowych filtrów.",
            "source": "Gazeta Prawna",
            "source_url": "https://www.gazetaprawna.pl/fado-normy-emisji",
            "published_at": (datetime.now() - timedelta(days=14)).isoformat(),
            "sentiment": "negative",
            "category": "legal"
        },
        {
            "id": "news_007",
            "title": "Spadek zamówień w FADO - branża motoryzacyjna zwalnia",
            "summary": "FADO Sp. z o.o. odnotowuje 15% spadek zamówień z sektora motoryzacyjnego w Q1 2026. Firma rozważa redukcję etatów w dziale produkcji.",
            "source": "Puls Biznesu",
            "source_url": "https://www.pb.pl/fado-spadek-zamowien",
            "published_at": (datetime.now() - timedelta(days=6)).isoformat(),
            "sentiment": "negative",
            "category": "financial"
        }
    ],
    "2": [  # Splast S.A.
        {
            "id": "news_101",
            "title": "Splast S.A. publikuje wyniki za Q4 2025",
            "summary": "Przychody wzrosły o 12% r/r, EBITDA wzrosła o 8%. Zarząd rekomenduje dywidendę w wysokości 2,50 PLN na akcję.",
            "source": "Bankier.pl",
            "source_url": "https://www.bankier.pl/splast-q4-wyniki",
            "published_at": (datetime.now() - timedelta(days=3)).isoformat(),
            "sentiment": "positive",
            "category": "financial"
        },
        {
            "id": "news_102",
            "title": "Splast planuje ekspansję na rynki bałtyckie",
            "summary": "Spółka ogłosiła plany otwarcia biura sprzedaży w Tallinie. Celem jest zwiększenie eksportu do krajów bałtyckich o 25% w 2026 roku.",
            "source": "Puls Biznesu",
            "source_url": "https://www.pb.pl/splast-ekspansja-baltyk",
            "published_at": (datetime.now() - timedelta(days=7)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        },
        {
            "id": "news_103",
            "title": "Kontrola UOKIK w Splast S.A.",
            "summary": "Urząd Ochrony Konkurencji i Konsumentów wszczął postępowanie wyjaśniające dotyczące potencjalnych praktyk cenowych w branży opakowań z tworzyw sztucznych.",
            "source": "Gazeta Wyborcza",
            "source_url": "https://wyborcza.biz/splast-uokik",
            "published_at": (datetime.now() - timedelta(days=15)).isoformat(),
            "sentiment": "negative",
            "category": "legal"
        }
    ],
    "3": [  # TechSoft Sp. z o.o.
        {
            "id": "news_201",
            "title": "TechSoft wdraża nowy system ERP dla dużego klienta",
            "summary": "Firma zakończyła wdrożenie systemu SAP S/4HANA dla jednego z największych producentów żywności w Polsce. Kontrakt warty 8 mln PLN.",
            "source": "CRN Polska",
            "source_url": "https://www.crn.pl/techsoft-sap-wdrozenie",
            "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        },
        {
            "id": "news_202",
            "title": "TechSoft otwiera nowe biuro w Krakowie",
            "summary": "Dynamiczny rozwój firmy wymusza ekspansję - TechSoft wynajął 2000 m2 powierzchni biurowej w Krakowie, planując zatrudnienie 100 nowych specjalistów IT.",
            "source": "Computerworld",
            "source_url": "https://www.computerworld.pl/techsoft-krakow",
            "published_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "sentiment": "positive",
            "category": "hr"
        }
    ],
    "4": [  # LogiTrans S.A.
        {
            "id": "news_301",
            "title": "LogiTrans zwiększa flotę o 50 nowych pojazdów",
            "summary": "Inwestycja o wartości 25 mln PLN obejmuje zakup 50 nowoczesnych naczep chłodniczych. LogiTrans umacnia pozycję lidera w transporcie produktów mrożonych.",
            "source": "Transport Manager",
            "source_url": "https://www.transportmanager.pl/logitrans-flota",
            "published_at": (datetime.now() - timedelta(days=4)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        },
        {
            "id": "news_302",
            "title": "Strajk kierowców zagraża dostawom LogiTrans",
            "summary": "Związki zawodowe kierowców zapowiadają 48-godzinny strajk ostrzegawczy. LogiTrans prowadzi negocjacje w sprawie podwyżek płac o 15%.",
            "source": "TVN24 Biznes",
            "source_url": "https://tvn24.pl/logitrans-strajk",
            "published_at": (datetime.now() - timedelta(days=6)).isoformat(),
            "sentiment": "negative",
            "category": "hr"
        }
    ],
    "5": [  # MetalPro Sp. z o.o.
        {
            "id": "news_401",
            "title": "MetalPro wygrywa przetarg na komponenty dla KGHM",
            "summary": "Firma z Katowic dostarczy specjalistyczne części maszyn górniczych o wartości 12 mln PLN. Realizacja kontraktu potrwa 18 miesięcy.",
            "source": "Nowy Przemysł",
            "source_url": "https://www.nowy-przemysl.pl/metalpro-kghm",
            "published_at": (datetime.now() - timedelta(days=9)).isoformat(),
            "sentiment": "positive",
            "category": "financial"
        }
    ],
    "6": [  # ConsultPro Sp. z o.o.
        {
            "id": "news_501",
            "title": "ConsultPro doradza przy fuzji dwóch spółek giełdowych",
            "summary": "Firma pełni rolę doradcy finansowego przy połączeniu dwóch średnich spółek z sektora IT. Transakcja warta 200 mln PLN.",
            "source": "Forbes Polska",
            "source_url": "https://www.forbes.pl/consultpro-fuzja",
            "published_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        }
    ],
    "7": [  # PlastPak Sp. z o.o.
        {
            "id": "news_601",
            "title": "PlastPak inwestuje w recykling",
            "summary": "Firma z Łodzi uruchamia linię do recyklingu opakowań PET. Inwestycja pozwoli przetwarzać 5000 ton plastiku rocznie.",
            "source": "Tworzywa.pl",
            "source_url": "https://www.tworzywa.pl/plastpak-recykling",
            "published_at": (datetime.now() - timedelta(days=11)).isoformat(),
            "sentiment": "positive",
            "category": "product"
        },
        {
            "id": "news_602",
            "title": "PlastPak certyfikowany według ISO 14001",
            "summary": "Firma uzyskała certyfikat zarządzania środowiskowego ISO 14001:2015. To ważny krok w kierunku zrównoważonej produkcji.",
            "source": "Rekopol",
            "source_url": "https://www.rekopol.pl/plastpak-iso",
            "published_at": (datetime.now() - timedelta(days=18)).isoformat(),
            "sentiment": "positive",
            "category": "general"
        }
    ]
}


# Mock timeline events for companies
MOCK_COMPANY_TIMELINE = {
    "1": [  # FADO Sp. z o.o. - Complete company history
        {
            "id": "event_001",
            "date": "1998-03-15",
            "title": "Założenie firmy FADO Sp. z o.o.",
            "description": "Założenie spółki przez trójkę wspólników: Jana Kowalskiego, Annę Nowak i Marka Wiśniewskiego. Kapitał zakładowy: 100,000 PLN.",
            "event_type": "founding",
            "impact": "high",
            "source": "KRS",
            "source_url": "https://ems.ms.gov.pl/"
        },
        {
            "id": "event_002",
            "date": "2000-06-10",
            "title": "Uruchomienie pierwszej linii produkcyjnej",
            "description": "Otwarcie zakładu produkcyjnego w Warszawie z linią do wytłaczania profili z PVC. Zatrudnienie 25 pracowników.",
            "event_type": "milestone",
            "impact": "high",
            "source": None,
            "source_url": None
        },
        {
            "id": "event_003",
            "date": "2003-09-20",
            "title": "Pierwsza duża umowa z branżą motoryzacyjną",
            "description": "Podpisanie kontraktu z Fiat Auto Poland na dostawę komponentów plastikowych. Wartość umowy: 5 mln PLN rocznie.",
            "event_type": "partnership",
            "impact": "high",
            "source": "Puls Biznesu",
            "source_url": "https://www.pb.pl/archiwum"
        },
        {
            "id": "event_004",
            "date": "2006-04-12",
            "title": "Inwestycja w automatyzację produkcji",
            "description": "Zakup robotów przemysłowych ABB i wdrożenie systemu MES. Inwestycja: 3 mln PLN. Wzrost wydajności o 40%.",
            "event_type": "investment",
            "impact": "medium",
            "source": None,
            "source_url": None
        },
        {
            "id": "event_005",
            "date": "2008-11-05",
            "title": "Kryzys finansowy - restrukturyzacja",
            "description": "Redukcja zatrudnienia o 15% i renegocjacja warunków kredytowych w odpowiedzi na kryzys gospodarczy 2008.",
            "event_type": "legal",
            "impact": "medium",
            "source": None,
            "source_url": None
        },
        {
            "id": "event_006",
            "date": "2011-05-18",
            "title": "Certyfikat ISO 9001",
            "description": "Uzyskanie certyfikatu ISO 9001:2008 System Zarządzania Jakością. Audyt przeprowadzony przez TÜV Rheinland.",
            "event_type": "milestone",
            "impact": "medium",
            "source": "TÜV Rheinland",
            "source_url": "https://www.tuv.com"
        },
        {
            "id": "event_007",
            "date": "2014-02-20",
            "title": "Wejście inwestora strategicznego Plastics Holding",
            "description": "Plastics Holding S.A. (podmiot kontrolowany przez Euro Polymers GmbH) nabywa 60% udziałów w FADO za 25 mln PLN.",
            "event_type": "investment",
            "impact": "high",
            "source": "KRS",
            "source_url": "https://ems.ms.gov.pl/"
        },
        {
            "id": "event_008",
            "date": "2016-07-10",
            "title": "Rozbudowa zakładu - Hala C",
            "description": "Budowa nowej hali produkcyjnej o powierzchni 3000 m2. Dodatkowe 2 linie produkcyjne. Inwestycja: 8 mln PLN.",
            "event_type": "investment",
            "impact": "high",
            "source": None,
            "source_url": None
        },
        {
            "id": "event_009",
            "date": "2018-03-25",
            "title": "Certyfikat IATF 16949 dla branży motoryzacyjnej",
            "description": "Uzyskanie prestiżowego certyfikatu IATF 16949:2016 potwierdzającego najwyższe standardy jakości dla dostawców automotive.",
            "event_type": "milestone",
            "impact": "high",
            "source": "Bureau Veritas",
            "source_url": "https://www.bureauveritas.pl"
        },
        {
            "id": "event_010",
            "date": "2020-03-15",
            "title": "Pandemia COVID-19 - przestój produkcji",
            "description": "Czasowe zamknięcie zakładu (3 tygodnie) z powodu pandemii. Wprowadzenie reżimu sanitarnego i pracy zmianowej.",
            "event_type": "legal",
            "impact": "medium",
            "source": None,
            "source_url": None
        },
        {
            "id": "event_011",
            "date": "2021-09-12",
            "title": "Nowa linia recyklingu plastiku",
            "description": "Uruchomienie linii do recyklingu tworzyw sztucznych. Zdolność przetwórcza: 1000 ton rocznie. Inwestycja: 2 mln PLN.",
            "event_type": "product",
            "impact": "medium",
            "source": "Tworzywa.pl",
            "source_url": "https://www.tworzywa.pl/fado-recykling"
        },
        {
            "id": "event_012",
            "date": "2023-01-20",
            "title": "Jan Nowak obejmuje stanowisko COO",
            "description": "Zmiana w zarządzie - Jan Nowak (były dyrektor w Splast S.A.) zostaje dyrektorem operacyjnym FADO.",
            "event_type": "hr",
            "impact": "medium",
            "source": "Money.pl",
            "source_url": "https://www.money.pl/fado-nowy-coo"
        },
        {
            "id": "event_013",
            "date": "2024-05-10",
            "title": "Partnerstwo strategiczne z German Plastics GmbH",
            "description": "Umowa na dostawy komponentów do sektora motoryzacyjnego. Wartość: 50 mln EUR w ciągu 3 lat.",
            "event_type": "partnership",
            "impact": "high",
            "source": "Rzeczpospolita",
            "source_url": "https://www.rp.pl/fado-umowa-niemcy"
        },
        {
            "id": "event_014",
            "date": "2025-11-30",
            "title": "Mandat WIOŚ za przekroczenie norm emisji",
            "description": "Wojewódzki Inspektorat Ochrony Środowiska nałożył karę 200,000 PLN za przekroczenie dopuszczalnych norm emisji. Firma zapowiada modernizację filtrów.",
            "event_type": "legal",
            "impact": "medium",
            "source": "Gazeta Prawna",
            "source_url": "https://www.gazetaprawna.pl/fado-normy-emisji"
        },
        {
            "id": "event_015",
            "date": "2026-01-10",
            "title": "Ogłoszenie inwestycji w rozbudowę zakładu o 30%",
            "description": "Plan rozbudowy mocy produkcyjnych o 30%. Nowa linia do wtrysku tworzyw. Wartość inwestycji: 15 mln PLN. Realizacja do Q2 2026.",
            "event_type": "investment",
            "impact": "high",
            "source": "Puls Biznesu",
            "source_url": "https://www.pb.pl/fado-rozbudowa-123456"
        }
    ],
    "2": [  # Splast S.A.
        {
            "id": "event_101",
            "date": "2005-06-15",
            "title": "Założenie Splast S.A.",
            "description": "Utworzenie spółki akcyjnej z kapitałem zakładowym 500,000 PLN. Siedziba: Kraków.",
            "event_type": "founding",
            "impact": "high",
            "source": "KRS",
            "source_url": "https://ems.ms.gov.pl/"
        },
        {
            "id": "event_102",
            "date": "2015-03-20",
            "title": "IPO - debiut na GPW",
            "description": "Wejście na rynek główny Giełdy Papierów Wartościowych w Warszawie. Pozyskanie 80 mln PLN z emisji akcji.",
            "event_type": "investment",
            "impact": "high",
            "source": "Bankier.pl",
            "source_url": "https://www.bankier.pl/splast-ipo"
        },
        {
            "id": "event_103",
            "date": "2025-11-15",
            "title": "Kontrola UOKIK w sprawie praktyk cenowych",
            "description": "Urząd Ochrony Konkurencji i Konsumentów wszczął postępowanie wyjaśniające dotyczące potencjalnych praktyk cenowych.",
            "event_type": "legal",
            "impact": "medium",
            "source": "Gazeta Wyborcza",
            "source_url": "https://wyborcza.biz/splast-uokik"
        }
    ]
}


# PKD Codes Database (Polish Classification of Activities)
PKD_CODES = {
    "01.11.Z": {"name": "Uprawa zbóż, roślin strączkowych i roślin oleistych na nasiona", "category": "Rolnictwo"},
    "10.71.Z": {"name": "Produkcja pieczywa i wyrobów cukierniczych", "category": "Produkcja"},
    "22.21.Z": {"name": "Produkcja płyt, arkuszy, rur i kształtowników z tworzyw sztucznych", "category": "Produkcja"},
    "22.22.Z": {"name": "Produkcja opakowań z tworzyw sztucznych", "category": "Produkcja"},
    "22.29.Z": {"name": "Produkcja pozostałych wyrobów z tworzyw sztucznych", "category": "Produkcja"},
    "25.62.Z": {"name": "Obróbka mechaniczna elementów metalowych", "category": "Produkcja"},
    "25.73.Z": {"name": "Produkcja narzędzi", "category": "Produkcja"},
    "28.22.Z": {"name": "Produkcja urządzeń dźwigowych i chwytaków", "category": "Produkcja"},
    "28.29.Z": {"name": "Produkcja pozostałych maszyn ogólnego przeznaczenia", "category": "Produkcja"},
    "41.20.Z": {"name": "Roboty budowlane związane ze wznoszeniem budynków", "category": "Budownictwo"},
    "46.71.Z": {"name": "Sprzedaż hurtowa paliw i produktów pochodnych", "category": "Handel"},
    "46.73.Z": {"name": "Sprzedaż hurtowa drewna i materiałów budowlanych", "category": "Handel"},
    "47.11.Z": {"name": "Sprzedaż detaliczna w niewyspecjalizowanych sklepach", "category": "Handel"},
    "49.41.Z": {"name": "Transport drogowy towarów", "category": "Transport"},
    "52.10.B": {"name": "Magazynowanie i przechowywanie pozostałych towarów", "category": "Logistyka"},
    "52.29.C": {"name": "Działalność pozostałych agencji transportowych", "category": "Logistyka"},
    "62.01.Z": {"name": "Działalność związana z oprogramowaniem", "category": "IT"},
    "62.02.Z": {"name": "Działalność związana z doradztwem w zakresie informatyki", "category": "IT"},
    "62.03.Z": {"name": "Działalność związana z zarządzaniem urządzeniami informatycznymi", "category": "IT"},
    "62.09.Z": {"name": "Pozostała działalność usługowa w zakresie technologii informatycznych", "category": "IT"},
    "63.11.Z": {"name": "Przetwarzanie danych; zarządzanie stronami internetowymi", "category": "IT"},
    "69.10.Z": {"name": "Działalność prawnicza", "category": "Usługi profesjonalne"},
    "69.20.Z": {"name": "Działalność rachunkowo-księgowa; doradztwo podatkowe", "category": "Usługi profesjonalne"},
    "70.22.Z": {"name": "Pozostałe doradztwo w zakresie prowadzenia działalności gospodarczej", "category": "Usługi profesjonalne"},
    "71.12.Z": {"name": "Działalność w zakresie inżynierii i związane z nią doradztwo techniczne", "category": "Usługi profesjonalne"},
    "16.23.Z": {"name": "Produkcja wyrobów stolarskich i ciesielskich dla budownictwa", "category": "Produkcja"},
    "31.02.Z": {"name": "Produkcja mebli kuchennych", "category": "Produkcja"},
    "73.11.Z": {"name": "Działalność agencji reklamowych", "category": "Marketing"},
    "74.10.Z": {"name": "Specjalistyczne projektowanie", "category": "Usługi profesjonalne"},
    "82.99.Z": {"name": "Pozostała działalność wspomagająca prowadzenie działalności gospodarczej", "category": "Usługi"},
}


# In-memory storage for company data refresh timestamps
COMPANY_LAST_UPDATED = {}


# Mock company database
MOCK_COMPANIES = [
    {
        "id": "1",
        "name": "FADO Sp. z o.o.",
        "nip": "5260016831",
        "krs": "0000145732",
        "regon": "012567834",
        "address": {"city": "Warszawa", "street": "ul. Przemysłowa 15", "postal_code": "00-001"},
        "pkd_codes": ["22.21.Z", "22.22.Z", "22.29.Z"],
        "status": "active",
        "founded": "1998",
    },
    {
        "id": "2",
        "name": "Splast S.A.",
        "nip": "6781234567",
        "krs": "0000234567",
        "regon": "234567890",
        "address": {"city": "Kraków", "street": "ul. Fabryczna 42", "postal_code": "30-001"},
        "pkd_codes": ["22.21.Z", "22.29.Z"],
        "status": "active",
        "founded": "2005",
    },
    {
        "id": "3",
        "name": "TechSoft Sp. z o.o.",
        "nip": "1234567890",
        "krs": "0000345678",
        "regon": "345678901",
        "address": {"city": "Warszawa", "street": "ul. Marszałkowska 100", "postal_code": "00-002"},
        "pkd_codes": ["62.01.Z", "62.02.Z", "63.11.Z"],
        "status": "active",
        "founded": "2010",
    },
    {
        "id": "4",
        "name": "LogiTrans S.A.",
        "nip": "9876543210",
        "krs": "0000456789",
        "regon": "456789012",
        "address": {"city": "Gdańsk", "street": "ul. Portowa 8", "postal_code": "80-001"},
        "pkd_codes": ["49.41.Z", "52.10.B", "52.29.C"],
        "status": "active",
        "founded": "2003",
    },
    {
        "id": "5",
        "name": "MetalPro Sp. z o.o.",
        "nip": "1122334455",
        "krs": "0000567890",
        "regon": "567890123",
        "address": {"city": "Katowice", "street": "ul. Stalowa 25", "postal_code": "40-001"},
        "pkd_codes": ["25.62.Z", "25.73.Z", "28.29.Z"],
        "status": "active",
        "founded": "2008",
    },
    {
        "id": "6",
        "name": "ConsultPro Sp. z o.o.",
        "nip": "5566778899",
        "krs": "0000678901",
        "regon": "678901234",
        "address": {"city": "Poznań", "street": "ul. Biznesowa 12", "postal_code": "60-001"},
        "pkd_codes": ["69.20.Z", "70.22.Z"],
        "status": "active",
        "founded": "2015",
    },
    {
        "id": "7",
        "name": "PlastPak Sp. z o.o.",
        "nip": "9988776655",
        "krs": "0000789012",
        "regon": "789012345",
        "address": {"city": "Łódź", "street": "ul. Produkcyjna 33", "postal_code": "90-001"},
        "pkd_codes": ["22.22.Z", "22.29.Z"],
        "status": "active",
        "founded": "2012",
    },
    {
        "id": "8",
        "name": "DataGap Sp. z o.o.",
        "nip": "3344556677",
        "krs": "",  # Missing KRS
        "regon": "",  # Missing REGON
        "address": {"city": "Wrocław", "street": "", "postal_code": ""},  # Missing street/postal
        "pkd_codes": ["62.01.Z"],
        "status": "active",
        "founded": "",  # Missing founded year
    },
]

# Related companies mapping: company_id -> list of related companies
RELATED_COMPANIES_MAP = {
    "1": [  # FADO Sp. z o.o. has 2 subsidiaries
        {
            "id": "7",
            "name": "PlastPak Sp. z o.o.",
            "nip": "9988776655",
            "krs": "0000789012",
            "relationship": "subsidiary",
            "ownership_percentage": 100.0,
            "description": "Spółka zależna - produkcja opakowań z tworzyw sztucznych"
        },
        {
            "id": "5",
            "name": "MetalPro Sp. z o.o.",
            "nip": "1122334455",
            "krs": "0000567890",
            "relationship": "subsidiary",
            "ownership_percentage": 51.0,
            "description": "Spółka zależna - produkcja komponentów metalowych"
        }
    ],
    "2": [  # Splast S.A. has parent company
        {
            "id": "1",
            "name": "FADO Sp. z o.o.",
            "nip": "5260016831",
            "krs": "0000145732",
            "relationship": "parent",
            "ownership_percentage": 60.0,
            "description": "Spółka matka - główny akcjonariusz"
        }
    ],
    "5": [  # MetalPro has parent
        {
            "id": "1",
            "name": "FADO Sp. z o.o.",
            "nip": "5260016831",
            "krs": "0000145732",
            "relationship": "parent",
            "ownership_percentage": 51.0,
            "description": "Spółka matka - większościowy udziałowiec"
        }
    ],
    "7": [  # PlastPak has parent
        {
            "id": "1",
            "name": "FADO Sp. z o.o.",
            "nip": "5260016831",
            "krs": "0000145732",
            "relationship": "parent",
            "ownership_percentage": 100.0,
            "description": "Spółka matka - jedyny udziałowiec"
        }
    ]
}

# Mock CEIDG companies (sole proprietorships - jednoosobowe działalności gospodarcze)
MOCK_CEIDG_COMPANIES = [
    {
        "id": "ceidg_1",
        "business_name": "Zakład Stolarski Jan Kowalski",
        "owner_name": "Jan Kowalski",
        "nip": "9876543211",
        "regon": "123456789",
        "address": {"city": "Warszawa", "street": "ul. Drewniana 45", "postal_code": "02-123"},
        "pkd_codes": ["16.23.Z", "31.02.Z"],
        "status": "active",
        "founded": "2015",
    },
    {
        "id": "ceidg_2",
        "business_name": "Studio Graficzne Anna Nowak",
        "owner_name": "Anna Nowak",
        "nip": "1234567891",
        "regon": "987654321",
        "address": {"city": "Kraków", "street": "ul. Artystyczna 12", "postal_code": "30-050"},
        "pkd_codes": ["74.10.Z", "73.11.Z"],
        "status": "active",
        "founded": "2018",
    },
    {
        "id": "ceidg_3",
        "business_name": "Usługi IT Piotr Wiśniewski",
        "owner_name": "Piotr Wiśniewski",
        "nip": "5551234567",
        "regon": "111222333",
        "address": {"city": "Wrocław", "street": "ul. Komputerowa 88", "postal_code": "50-001"},
        "pkd_codes": ["62.01.Z", "62.02.Z"],
        "status": "active",
        "founded": "2020",
    },
]


class CompanySearchResult(BaseModel):
    id: str
    name: str
    nip: str
    address: dict
    pkd_codes: List[str]
    pkd_descriptions: List[dict]
    status: str


class PKDSearchResponse(BaseModel):
    pkd_code: str
    pkd_description: str
    pkd_category: str
    companies: List[CompanySearchResult]
    total_count: int


@router.get("/search")
async def search_companies(
    response: Response,
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """Search companies by name, NIP, or KRS. Cached for 5 minutes."""
    from app.core.cache import cache_manager

    # Generate cache key
    cache_key = cache_manager.generate_cache_key("companies_search", q=q, limit=limit)

    # Try cache first
    cached_result = await cache_manager.get(cache_key)
    if cached_result is not None:
        if response:
            response.headers["X-Cache-Hit"] = "true"
        return cached_result

    # Cache miss - perform search
    q_lower = q.lower()
    results = []

    for company in MOCK_COMPANIES:
        if (q_lower in company["name"].lower() or
            q in company["nip"] or
            q in company.get("krs", "")):
            pkd_descriptions = []
            for pkd in company["pkd_codes"]:
                if pkd in PKD_CODES:
                    pkd_descriptions.append({
                        "code": pkd,
                        "name": PKD_CODES[pkd]["name"],
                        "category": PKD_CODES[pkd]["category"]
                    })
            results.append(CompanySearchResult(
                id=company["id"],
                name=company["name"],
                nip=company["nip"],
                address=company["address"],
                pkd_codes=company["pkd_codes"],
                pkd_descriptions=pkd_descriptions,
                status=company["status"]
            ))

    result = {"results": results[:limit], "total": len(results)}

    # Store in cache (5 minutes TTL)
    await cache_manager.set(cache_key, result, ttl=300)

    if response:
        response.headers["X-Cache-Hit"] = "false"

    return result


@router.get("/search/pkd", response_model=PKDSearchResponse)
async def search_by_pkd(
    code: str = Query(..., min_length=4, description="PKD code (e.g., 22.21.Z)"),
    current_user: User = Depends(get_current_user)
):
    """
    Search companies by PKD code.
    Returns all companies with the specified PKD code along with PKD description.
    """
    # Normalize PKD code
    pkd_code = code.upper().strip()

    # Get PKD description
    if pkd_code not in PKD_CODES:
        # Try partial match
        matching_codes = [k for k in PKD_CODES.keys() if k.startswith(pkd_code[:2])]
        if matching_codes:
            pkd_code = matching_codes[0]
        else:
            return PKDSearchResponse(
                pkd_code=code,
                pkd_description="Nieznany kod PKD",
                pkd_category="Nieznana",
                companies=[],
                total_count=0
            )

    pkd_info = PKD_CODES[pkd_code]

    # Find companies with this PKD code
    results = []
    for company in MOCK_COMPANIES:
        if pkd_code in company["pkd_codes"]:
            pkd_descriptions = []
            for pkd in company["pkd_codes"]:
                if pkd in PKD_CODES:
                    pkd_descriptions.append({
                        "code": pkd,
                        "name": PKD_CODES[pkd]["name"],
                        "category": PKD_CODES[pkd]["category"]
                    })
            results.append(CompanySearchResult(
                id=company["id"],
                name=company["name"],
                nip=company["nip"],
                address=company["address"],
                pkd_codes=company["pkd_codes"],
                pkd_descriptions=pkd_descriptions,
                status=company["status"]
            ))

    return PKDSearchResponse(
        pkd_code=pkd_code,
        pkd_description=pkd_info["name"],
        pkd_category=pkd_info["category"],
        companies=results,
        total_count=len(results)
    )


@router.get("/pkd-codes")
async def list_pkd_codes(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in PKD names")
):
    """List available PKD codes with optional filtering."""
    results = []
    for code, info in PKD_CODES.items():
        if category and info["category"].lower() != category.lower():
            continue
        if search and search.lower() not in info["name"].lower():
            continue
        results.append({
            "code": code,
            "name": info["name"],
            "category": info["category"]
        })
    return {"pkd_codes": results, "total": len(results)}


# ============================================================================
# WATCHLIST ENDPOINTS
# ============================================================================

# In-memory watchlist storage: { "user_id": ["company_id1", "company_id2", ...] }
COMPANY_WATCHLIST: dict = {}


@router.get("/watchlist")
async def get_watchlist_companies(
    current_user: User = Depends(get_current_user)
):
    """Get list of user's watchlisted company IDs."""
    user_id = str(current_user.id)
    watchlist = COMPANY_WATCHLIST.get(user_id, [])
    return {"watchlist": watchlist, "count": len(watchlist)}


@router.post("/{identifier}/watchlist")
async def add_to_watchlist(
    identifier: str,
    current_user: User = Depends(get_current_user)
):
    """Add a company to user's watchlist."""
    user_id = str(current_user.id)

    # Initialize user's watchlist if it doesn't exist
    if user_id not in COMPANY_WATCHLIST:
        COMPANY_WATCHLIST[user_id] = []

    # Add to watchlist if not already there
    if identifier not in COMPANY_WATCHLIST[user_id]:
        COMPANY_WATCHLIST[user_id].append(identifier)
        return {"message": "Company added to watchlist", "is_watched": True}

    return {"message": "Company already in watchlist", "is_watched": True}


@router.delete("/{identifier}/watchlist")
async def remove_from_watchlist(
    identifier: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a company from user's watchlist."""
    user_id = str(current_user.id)

    if user_id in COMPANY_WATCHLIST and identifier in COMPANY_WATCHLIST[user_id]:
        COMPANY_WATCHLIST[user_id].remove(identifier)
        return {"message": "Company removed from watchlist", "is_watched": False}

    return {"message": "Company not in watchlist", "is_watched": False}


@router.get("/{identifier}/watchlist")
async def check_watchlist_status(
    identifier: str,
    current_user: User = Depends(get_current_user)
):
    """Check if a company is in user's watchlist."""
    user_id = str(current_user.id)
    is_watched = user_id in COMPANY_WATCHLIST and identifier in COMPANY_WATCHLIST[user_id]
    return {"is_watched": is_watched}


# Company Comparison Models
class CompanyComparisonMetric(BaseModel):
    metric_name: str
    company1_value: Optional[float] = None
    company2_value: Optional[float] = None
    company1_formatted: Optional[str] = None
    company2_formatted: Optional[str] = None
    difference: Optional[float] = None
    difference_percentage: Optional[float] = None
    winner: Optional[str] = None  # "company1", "company2", "tie"
    indicator: Optional[str] = None  # "better", "worse", "neutral"


class CompanyComparison(BaseModel):
    company1: dict
    company2: dict
    metrics: List[CompanyComparisonMetric]
    summary: dict


@router.get("/compare", response_model=CompanyComparison)
async def compare_companies(
    company1_id: str = Query(..., description="First company identifier (NIP/KRS/REGON)"),
    company2_id: str = Query(..., description="Second company identifier (NIP/KRS/REGON)")
    # Temporarily disabled auth for testing: current_user: User = Depends(get_current_user)
):
    """
    Compare two companies side by side across multiple metrics
    """
    # Fetch both companies
    company1 = None
    company2 = None

    for c in MOCK_COMPANIES:
        if c["id"] == company1_id or c["nip"] == company1_id or c.get("krs", "") == company1_id:
            company1 = c
        if c["id"] == company2_id or c["nip"] == company2_id or c.get("krs", "") == company2_id:
            company2 = c

    if not company1:
        raise HTTPException(status_code=404, detail=f"Company {company1_id} not found")
    if not company2:
        raise HTTPException(status_code=404, detail=f"Company {company2_id} not found")

    # Helper function to calculate difference
    def calc_diff(val1: Optional[float], val2: Optional[float], higher_is_better: bool = True):
        if val1 is None or val2 is None:
            return None, None, None

        diff = val1 - val2
        diff_pct = (diff / val2 * 100) if val2 != 0 else 0

        if abs(diff_pct) < 5:  # Within 5% is considered tie
            winner = "tie"
        elif (higher_is_better and val1 > val2) or (not higher_is_better and val1 < val2):
            winner = "company1"
        else:
            winner = "company2"

        return diff, diff_pct, winner

    # Build comparison metrics
    metrics = []

    # Mock financial data for demonstration
    mock_revenue = {"1": 45000000, "7": 12000000, "5": 8500000, "2": 35000000}
    mock_employees = {"1": 250, "7": 85, "5": 62, "2": 180}
    mock_roe = {"1": 15.2, "7": 11.8, "5": 9.5, "2": 13.4}

    # Revenue comparison
    c1_revenue = mock_revenue.get(company1["id"])
    c2_revenue = mock_revenue.get(company2["id"])
    diff, diff_pct, winner = calc_diff(c1_revenue, c2_revenue, higher_is_better=True)

    metrics.append(CompanyComparisonMetric(
        metric_name="Przychody (PLN)",
        company1_value=c1_revenue,
        company2_value=c2_revenue,
        company1_formatted=f"{c1_revenue:,.0f} PLN" if c1_revenue else "Brak danych",
        company2_formatted=f"{c2_revenue:,.0f} PLN" if c2_revenue else "Brak danych",
        difference=diff,
        difference_percentage=diff_pct,
        winner=winner
    ))

    # Employees
    c1_employees = mock_employees.get(company1["id"])
    c2_employees = mock_employees.get(company2["id"])
    diff, diff_pct, winner = calc_diff(c1_employees, c2_employees, higher_is_better=True)

    metrics.append(CompanyComparisonMetric(
        metric_name="Liczba pracowników",
        company1_value=c1_employees,
        company2_value=c2_employees,
        company1_formatted=str(int(c1_employees)) if c1_employees else "Brak danych",
        company2_formatted=str(int(c2_employees)) if c2_employees else "Brak danych",
        difference=diff,
        difference_percentage=diff_pct,
        winner=winner
    ))

    # ROE
    c1_roe = mock_roe.get(company1["id"])
    c2_roe = mock_roe.get(company2["id"])
    diff, diff_pct, winner = calc_diff(c1_roe, c2_roe, higher_is_better=True)

    metrics.append(CompanyComparisonMetric(
        metric_name="ROE (%)",
        company1_value=c1_roe,
        company2_value=c2_roe,
        company1_formatted=f"{c1_roe:.1f}%" if c1_roe else "Brak danych",
        company2_formatted=f"{c2_roe:.1f}%" if c2_roe else "Brak danych",
        difference=diff,
        difference_percentage=diff_pct,
        winner=winner
    ))

    # Calculate summary (who wins overall)
    wins_c1 = sum(1 for m in metrics if m.winner == "company1")
    wins_c2 = sum(1 for m in metrics if m.winner == "company2")
    ties = sum(1 for m in metrics if m.winner == "tie")

    summary = {
        "company1_wins": wins_c1,
        "company2_wins": wins_c2,
        "ties": ties,
        "overall_winner": "company1" if wins_c1 > wins_c2 else "company2" if wins_c2 > wins_c1 else "tie"
    }

    return CompanyComparison(
        company1={
            "id": company1_id,
            "name": company1.get("name", ""),
            "nip": company1.get("nip", ""),
            "krs": company1.get("krs", ""),
            "industry": company1.get("industry", "")
        },
        company2={
            "id": company2_id,
            "name": company2.get("name", ""),
            "nip": company2.get("nip", ""),
            "krs": company2.get("krs", ""),
            "industry": company2.get("industry", "")
        },
        metrics=metrics,
        summary=summary
    )


@router.get("/{identifier}", response_model=CompanyProfile)
async def get_company(
    identifier: str
    # Temporarily disabled auth for testing: current_user: User = Depends(get_current_user)
):
    """Get company profile by NIP, KRS, or internal ID."""
    # Find company by id, nip, or krs
    company = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Build PKD descriptions
    pkd_descriptions = []
    for pkd in company["pkd_codes"]:
        if pkd in PKD_CODES:
            pkd_descriptions.append({
                "code": pkd,
                "name": PKD_CODES[pkd]["name"],
                "category": PKD_CODES[pkd]["category"]
            })

    # Additional company info
    descriptions = {
        "1": "Wiodący producent wyrobów z tworzyw sztucznych w Polsce, specjalizujący się w komponentach dla sektora motoryzacyjnego i AGD.",
        "2": "Duży producent opakowań i folii z tworzyw sztucznych dla branży spożywczej i przemysłowej.",
        "3": "Dynamicznie rozwijająca się firma IT specjalizująca się we wdrożeniach systemów ERP i rozwiązaniach chmurowych.",
        "4": "Lider w transporcie i logistyce produktów wymagających kontroli temperatury w Polsce i Europie.",
        "5": "Producent precyzyjnych elementów metalowych dla przemysłu maszynowego i wydobywczego.",
        "6": "Firma doradcza oferująca usługi księgowe, podatkowe i wsparcie przy transakcjach M&A.",
        "7": "Producent opakowań z tworzyw sztucznych z naciskiem na rozwiązania ekologiczne i recykling."
    }

    websites = {
        "1": "https://www.fado.pl",
        "2": "https://www.splast.pl",
        "3": "https://www.techsoft.pl",
        "4": "https://www.logitrans.pl",
        "5": "https://www.metalpro.pl",
        "6": "https://www.consultpro.pl",
        "7": "https://www.plastpak.pl"
    }

    employees = {
        "1": "201-500",
        "2": "501-1000",
        "3": "51-200",
        "4": "201-500",
        "5": "51-200",
        "6": "11-50",
        "7": "51-200"
    }

    # Get last updated timestamp (default to current time if never refreshed)
    company_id = company["id"]
    if company_id not in COMPANY_LAST_UPDATED:
        COMPANY_LAST_UPDATED[company_id] = datetime.now().isoformat()

    # Get related companies
    related_companies_data = RELATED_COMPANIES_MAP.get(company_id, [])
    related_companies = [
        RelatedCompany(**rc) for rc in related_companies_data
    ]

    return CompanyProfile(
        id=company["id"],
        name=company["name"],
        nip=company["nip"],
        krs=company.get("krs", ""),
        regon=company.get("regon", ""),
        address=company["address"],
        pkd_codes=company["pkd_codes"],
        pkd_descriptions=pkd_descriptions,
        status=company["status"],
        founded=company.get("founded", "N/A"),
        description=descriptions.get(company["id"]),
        website=websites.get(company["id"]),
        employees_range=employees.get(company["id"]),
        last_updated=COMPANY_LAST_UPDATED[company_id],
        related_companies=related_companies
    )


@router.get("/{identifier}/financials", response_model=CompanyFinancials)
async def get_company_financials(identifier: str):
    """Get company financial data including statements and calculated ratios."""
    # Mock financial data for FADO Sp. z o.o.
    if identifier in ["5260016831", "1"]:
        return CompanyFinancials(
            company_id=identifier,
            company_name="FADO Sp. z o.o.",
            statements=[
                FinancialStatement(
                    year=2023,
                    revenue=45_200_000,
                    net_profit=4_800_000,
                    total_assets=51_000_000,
                    total_equity=26_400_000,
                    total_liabilities=16_320_000,
                    current_assets=24_500_000,
                    current_liabilities=11_700_000,
                    inventory=7_300_000,
                    accounts_receivable=5_600_000
                ),
                FinancialStatement(
                    year=2022,
                    revenue=40_200_000,
                    net_profit=4_000_000,
                    total_assets=48_000_000,
                    total_equity=25_000_000,
                    total_liabilities=15_360_000,
                    current_assets=22_000_000,
                    current_liabilities=10_500_000,
                    inventory=6_800_000,
                    accounts_receivable=5_200_000
                ),
                FinancialStatement(
                    year=2021,
                    revenue=35_800_000,
                    net_profit=3_200_000,
                    total_assets=45_000_000,
                    total_equity=23_500_000,
                    total_liabilities=14_400_000,
                    current_assets=20_000_000,
                    current_liabilities=9_500_000,
                    inventory=6_200_000,
                    accounts_receivable=4_800_000
                )
            ],
            ratios=[
                FinancialRatios(
                    year=2023,
                    roe=18.2,  # net_profit / total_equity * 100
                    roa=9.4,   # net_profit / total_assets * 100
                    ros=10.6,  # net_profit / revenue * 100
                    current_ratio=2.1,  # current_assets / current_liabilities
                    quick_ratio=1.4,    # (current_assets - inventory) / current_liabilities
                    debt_ratio=32.0,    # total_liabilities / total_assets * 100
                    debt_to_equity=0.47,  # total_liabilities / total_equity
                    inventory_turnover=6.2,  # revenue / inventory
                    dso=45  # (accounts_receivable / revenue) * 365
                ),
                FinancialRatios(
                    year=2022,
                    roe=16.0,
                    roa=8.3,
                    ros=10.0,
                    current_ratio=2.1,
                    quick_ratio=1.4,
                    debt_ratio=32.0,
                    debt_to_equity=0.61,
                    inventory_turnover=5.9,
                    dso=47
                ),
                FinancialRatios(
                    year=2021,
                    roe=13.6,
                    roa=7.1,
                    ros=8.9,
                    current_ratio=2.1,
                    quick_ratio=1.5,
                    debt_ratio=32.0,
                    debt_to_equity=0.61,
                    inventory_turnover=5.8,
                    dso=49
                )
            ],
            industry_benchmarks=IndustryBenchmarks(
                industry="Plastics Manufacturing (PKD 22.2)",
                year=2023,
                source="GUS Statistical Yearbook 2023 - Manufacturing Sector Analysis",
                source_url="https://stat.gov.pl/yearbook/2023",
                metrics=[
                    IndustryBenchmark(
                        metric_name="ROE (Return on Equity)",
                        company_value=18.2,
                        industry_average=12.5,
                        industry_median=11.8,
                        percentile=78,
                        comparison="above_average"
                    ),
                    IndustryBenchmark(
                        metric_name="ROA (Return on Assets)",
                        company_value=9.4,
                        industry_average=7.2,
                        industry_median=6.9,
                        percentile=72,
                        comparison="above_average"
                    ),
                    IndustryBenchmark(
                        metric_name="ROS (Return on Sales)",
                        company_value=10.6,
                        industry_average=8.3,
                        industry_median=7.9,
                        percentile=75,
                        comparison="above_average"
                    ),
                    IndustryBenchmark(
                        metric_name="Current Ratio",
                        company_value=2.1,
                        industry_average=1.8,
                        industry_median=1.7,
                        percentile=68,
                        comparison="above_average"
                    ),
                    IndustryBenchmark(
                        metric_name="Quick Ratio",
                        company_value=1.4,
                        industry_average=1.2,
                        industry_median=1.1,
                        percentile=65,
                        comparison="above_average"
                    ),
                    IndustryBenchmark(
                        metric_name="Debt Ratio",
                        company_value=32.0,
                        industry_average=45.2,
                        industry_median=46.8,
                        percentile=72,
                        comparison="below_average"  # Lower debt is better
                    ),
                    IndustryBenchmark(
                        metric_name="Debt to Equity",
                        company_value=0.47,
                        industry_average=0.82,
                        industry_median=0.88,
                        percentile=68,
                        comparison="below_average"  # Lower is better
                    ),
                    IndustryBenchmark(
                        metric_name="Inventory Turnover",
                        company_value=6.2,
                        industry_average=5.1,
                        industry_median=4.8,
                        percentile=71,
                        comparison="above_average"
                    ),
                    IndustryBenchmark(
                        metric_name="DSO (Days Sales Outstanding)",
                        company_value=45.0,
                        industry_average=52.0,
                        industry_median=54.0,
                        percentile=65,
                        comparison="below_average"  # Lower DSO is better
                    )
                ]
            )
        )

    # Return empty data for unknown companies
    return CompanyFinancials(
        company_id=identifier,
        company_name="Unknown Company",
        statements=[],
        ratios=[]
    )


@router.get("/{identifier}/ownership")
async def get_company_ownership(identifier: str):
    """Get company ownership structure."""
    # TODO: Implement ownership mapping
    return {
        "company_id": identifier,
        "shareholders": [],
        "beneficial_owners": []
    }


@router.get("/{identifier}/people")
async def get_company_people(identifier: str):
    """Get company key people."""
    # TODO: Implement key people retrieval
    return {
        "company_id": identifier,
        "management_board": [],
        "supervisory_board": []
    }


@router.get("/{identifier}/competitors")
async def get_company_competitors(identifier: str):
    """Get company competitors."""
    # TODO: Implement competitor mapping
    return {
        "company_id": identifier,
        "competitors": []
    }


@router.get("/{identifier}/news", response_model=CompanyNews)
async def get_company_news(
    identifier: str,
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None, description="Filter by category: general, financial, product, hr, legal"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment: positive, negative, neutral"),
    date_from: Optional[str] = Query(None, description="Filter news from this date (ISO format YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter news until this date (ISO format YYYY-MM-DD)")
    # Temporarily disabled auth for testing: , current_user: User = Depends(get_current_user)
):
    """Get news about company."""
    # Find company by id, nip, or krs
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get news for this company
    news_items = MOCK_COMPANY_NEWS.get(company_id, [])

    # Filter by category if specified
    if category:
        news_items = [n for n in news_items if n["category"] == category]

    # Filter by sentiment if specified
    if sentiment:
        news_items = [n for n in news_items if n["sentiment"] == sentiment]

    # Filter by date range if specified
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            news_items = [n for n in news_items if datetime.fromisoformat(n["published_at"].replace('Z', '+00:00')) >= from_date]
        except ValueError:
            pass  # Invalid date format, skip filter

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            # Add one day to include the end date fully
            to_date = to_date + timedelta(days=1)
            news_items = [n for n in news_items if datetime.fromisoformat(n["published_at"].replace('Z', '+00:00')) < to_date]
        except ValueError:
            pass  # Invalid date format, skip filter

    # Limit results
    news_items = news_items[:limit]

    return CompanyNews(
        company_id=company_id,
        company_name=company["name"],
        news=[NewsArticle(**n) for n in news_items],
        total_count=len(news_items)
    )


@router.get("/{identifier}/timeline", response_model=CompanyTimeline)
async def get_company_timeline(
    identifier: str,
    event_type: Optional[str] = Query(None, description="Filter by event type: founding, investment, partnership, product, legal, hr, milestone"),
    impact: Optional[str] = Query(None, description="Filter by impact: high, medium, low"),
    year_from: Optional[int] = Query(None, description="Filter events from this year"),
    year_to: Optional[int] = Query(None, description="Filter events until this year")
    # Temporarily disabled auth for testing: , current_user: User = Depends(get_current_user)
):
    """Get timeline of key events for company."""
    # Find company by id, nip, or krs
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get timeline events for this company
    events = MOCK_COMPANY_TIMELINE.get(company_id, [])

    # Filter by event type if specified
    if event_type:
        events = [e for e in events if e["event_type"] == event_type]

    # Filter by impact if specified
    if impact:
        events = [e for e in events if e["impact"] == impact]

    # Filter by year range if specified
    if year_from:
        events = [e for e in events if int(e["date"][:4]) >= year_from]

    if year_to:
        events = [e for e in events if int(e["date"][:4]) <= year_to]

    # Sort by date (oldest first)
    events = sorted(events, key=lambda x: x["date"])

    return CompanyTimeline(
        company_id=company_id,
        company_name=company["name"],
        events=[TimelineEvent(**e) for e in events],
        total_count=len(events)
    )


class RefreshResponse(BaseModel):
    success: bool
    message: str
    last_updated: str
    company_id: str


@router.post("/{identifier}/refresh", response_model=RefreshResponse)
async def refresh_company_data(
    identifier: str
    # Temporarily disabled auth for testing: , current_user: User = Depends(get_current_user)
):
    """
    Manually refresh company data from external sources.
    This simulates fetching fresh data from KRS, CEIDG, news APIs, etc.
    """
    # Find company by id, nip, or krs
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Simulate data refresh delay (would be real API calls in production)
    import asyncio
    await asyncio.sleep(1.5)  # Simulate API calls taking time

    # Update last_updated timestamp
    now = datetime.now().isoformat()
    COMPANY_LAST_UPDATED[company_id] = now

    return RefreshResponse(
        success=True,
        message=f"Dane firmy {company['name']} zostały odświeżone",
        last_updated=now,
        company_id=company_id
    )


# ============================================================================
# SCHEDULED DATA UPDATES
# ============================================================================

class UpdateSchedule(BaseModel):
    company_id: str
    frequency: str  # daily, weekly, monthly
    time: str  # HH:MM format (24-hour)
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None


class ScheduleConfig(BaseModel):
    company_id: str
    company_name: str
    frequency: str
    time: str
    enabled: bool
    last_run: Optional[str]
    next_run: Optional[str]


class ScheduleResponse(BaseModel):
    success: bool
    message: str
    schedule: ScheduleConfig


# In-memory storage for update schedules
COMPANY_UPDATE_SCHEDULES = {}

# In-memory storage for schedule notifications
SCHEDULE_NOTIFICATIONS = []


def calculate_next_run(frequency: str, time_str: str) -> str:
    """Calculate next run timestamp based on frequency and time"""
    now = datetime.now()
    hour, minute = map(int, time_str.split(':'))

    if frequency == "daily":
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
    elif frequency == "weekly":
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        days_ahead = 7 - now.weekday()  # Next Monday
        if days_ahead <= 0 or (days_ahead == 7 and next_run <= now):
            days_ahead += 7
        next_run += timedelta(days=days_ahead)
    elif frequency == "monthly":
        next_run = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
        # Next month
        if next_run <= now:
            if next_run.month == 12:
                next_run = next_run.replace(year=next_run.year + 1, month=1)
            else:
                next_run = next_run.replace(month=next_run.month + 1)
    else:
        next_run = now

    return next_run.isoformat()


@router.post("/{identifier}/schedule", response_model=ScheduleResponse)
async def configure_update_schedule(
    identifier: str,
    frequency: str = Query(..., regex="^(daily|weekly|monthly)$"),
    time: str = Query(..., regex="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"),
    enabled: bool = Query(True)
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """
    Configure automatic update schedule for a company.

    - frequency: daily, weekly, or monthly
    - time: HH:MM format (24-hour), e.g., "09:00" for 9 AM
    - enabled: whether the schedule is active
    """
    # Find company
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Calculate next run time
    # For testing: Set next_run to 20 seconds from now for immediate testing
    if enabled:
        next_run = (datetime.now() + timedelta(seconds=20)).isoformat()
    else:
        next_run = None

    # Store schedule
    schedule = UpdateSchedule(
        company_id=company_id,
        frequency=frequency,
        time=time,
        enabled=enabled,
        last_run=None,
        next_run=next_run
    )
    COMPANY_UPDATE_SCHEDULES[company_id] = schedule

    return ScheduleResponse(
        success=True,
        message=f"Harmonogram aktualizacji dla {company['name']} został skonfigurowany",
        schedule=ScheduleConfig(
            company_id=company_id,
            company_name=company["name"],
            frequency=frequency,
            time=time,
            enabled=enabled,
            last_run=None,
            next_run=next_run
        )
    )


@router.get("/{identifier}/schedule", response_model=ScheduleConfig)
async def get_update_schedule(
    identifier: str
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """Get current update schedule configuration for a company"""
    # Find company
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get schedule if exists
    schedule = COMPANY_UPDATE_SCHEDULES.get(company_id)

    if not schedule:
        raise HTTPException(status_code=404, detail="No schedule configured for this company")

    return ScheduleConfig(
        company_id=company_id,
        company_name=company["name"],
        frequency=schedule.frequency,
        time=schedule.time,
        enabled=schedule.enabled,
        last_run=schedule.last_run,
        next_run=schedule.next_run
    )


@router.delete("/{identifier}/schedule")
async def delete_update_schedule(
    identifier: str
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """Delete/disable automatic update schedule for a company"""
    # Find company
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company_id in COMPANY_UPDATE_SCHEDULES:
        del COMPANY_UPDATE_SCHEDULES[company_id]
        return {"success": True, "message": f"Harmonogram dla {company['name']} został usunięty"}
    else:
        raise HTTPException(status_code=404, detail="No schedule found for this company")


@router.get("/schedules/all")
async def list_all_schedules(
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """List all configured update schedules"""
    schedules = []
    for company_id, schedule in COMPANY_UPDATE_SCHEDULES.items():
        # Find company name
        company = next((c for c in MOCK_COMPANIES if c["id"] == company_id), None)
        if company:
            schedules.append(ScheduleConfig(
                company_id=company_id,
                company_name=company["name"],
                frequency=schedule.frequency,
                time=schedule.time,
                enabled=schedule.enabled,
                last_run=schedule.last_run,
                next_run=schedule.next_run
            ))

    return {"schedules": schedules, "total": len(schedules)}


@router.get("/schedules/notifications")
async def get_schedule_notifications(
    unread_only: bool = Query(False)
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """Get notifications from scheduled updates"""
    notifications = SCHEDULE_NOTIFICATIONS

    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]

    # Sort by timestamp descending (newest first)
    notifications = sorted(notifications, key=lambda x: x["timestamp"], reverse=True)

    return {"notifications": notifications, "total": len(notifications), "unread": len([n for n in SCHEDULE_NOTIFICATIONS if not n.get("read", False)])}


@router.post("/schedules/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """Mark a schedule notification as read"""
    for notification in SCHEDULE_NOTIFICATIONS:
        if notification["id"] == notification_id:
            notification["read"] = True
            return {"success": True, "message": "Notification marked as read"}

    raise HTTPException(status_code=404, detail="Notification not found")


# Data Quality Assessment Helper
def calculate_quality_score(filled_fields: int, total_fields: int) -> dict:
    """Calculate quality score and status"""
    score = (filled_fields / total_fields * 100) if total_fields > 0 else 0

    if score >= 90:
        status = "excellent"
    elif score >= 70:
        status = "good"
    elif score >= 50:
        status = "fair"
    else:
        status = "poor"

    return {"score": round(score, 1), "status": status}


@router.get("/{identifier}/data-quality", response_model=DataQualityDashboard)
async def get_company_data_quality(
    identifier: str
    # TODO: Re-enable auth after testing
    # current_user: User = Depends(get_current_user)
):
    """Get data quality metrics for a company"""
    # Find company
    company = None
    company_id = None
    for c in MOCK_COMPANIES:
        if (c["id"] == identifier or
            c["nip"] == identifier or
            c.get("krs", "") == identifier):
            company = c
            company_id = c["id"]
            break

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Assess Completeness (check which fields are filled)
    completeness_fields = {
        "Podstawowe dane": {
            "NIP": bool(company.get("nip")),
            "KRS": bool(company.get("krs")),
            "REGON": bool(company.get("regon")),
            "Adres": bool(company.get("address")),
            "Data założenia": bool(company.get("founded"))
        },
        "Informacje biznesowe": {
            "Opis działalności": bool(company.get("description")),
            "Strona WWW": bool(company.get("website")),
            "Kody PKD": bool(company.get("pkd_codes")),
            "Zatrudnienie": bool(company.get("employees_range"))
        },
        "Dane finansowe": {
            "Kapitał zakładowy": False,  # Not in basic profile
            "Sprawozdania finansowe": False
        },
        "Zarząd i struktura": {
            "Zarząd": False,
            "Wspólnicy": False,
            "Rada nadzorcza": False
        }
    }

    # Count filled fields
    total_fields = 0
    filled_fields = 0
    completeness_details = []

    for section, fields in completeness_fields.items():
        section_total = len(fields)
        section_filled = sum(1 for v in fields.values() if v)
        total_fields += section_total
        filled_fields += section_filled

        completeness_details.append({
            "section": section,
            "filled": section_filled,
            "total": section_total,
            "percentage": round(section_filled / section_total * 100, 1) if section_total > 0 else 0,
            "fields": fields
        })

    completeness_score = calculate_quality_score(filled_fields, total_fields)

    # Assess Freshness (how recent is the data)
    last_update_str = COMPANY_LAST_UPDATED.get(company_id, datetime.now().isoformat())
    last_update = datetime.fromisoformat(last_update_str)
    days_since_update = (datetime.now() - last_update).days

    freshness_details = [
        {
            "source": "KRS/CEIDG",
            "last_updated": last_update_str,
            "days_ago": days_since_update,
            "status": "fresh" if days_since_update < 30 else "stale" if days_since_update < 90 else "outdated"
        },
        {
            "source": "Sprawozdania finansowe",
            "last_updated": (datetime.now() - timedelta(days=180)).isoformat(),
            "days_ago": 180,
            "status": "stale"
        },
        {
            "source": "Aktualności",
            "last_updated": (datetime.now() - timedelta(days=2)).isoformat(),
            "days_ago": 2,
            "status": "fresh"
        },
        {
            "source": "Struktura własnościowa",
            "last_updated": (datetime.now() - timedelta(days=365)).isoformat(),
            "days_ago": 365,
            "status": "outdated"
        }
    ]

    # Calculate freshness score based on average days
    avg_days = sum(d["days_ago"] for d in freshness_details) / len(freshness_details)
    if avg_days < 30:
        freshness_score = {"score": 95.0, "status": "excellent"}
    elif avg_days < 90:
        freshness_score = {"score": 75.0, "status": "good"}
    elif avg_days < 180:
        freshness_score = {"score": 55.0, "status": "fair"}
    else:
        freshness_score = {"score": 30.0, "status": "poor"}

    # Assess Source Reliability
    source_reliability_details = [
        {
            "source": "KRS (rządowe)",
            "reliability": "verified",
            "confidence": 100,
            "last_verification": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "source": "CEIDG (rządowe)",
            "reliability": "verified",
            "confidence": 100,
            "last_verification": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "source": "Strona WWW (web scraping)",
            "reliability": "unverified",
            "confidence": 70,
            "last_verification": (datetime.now() - timedelta(days=7)).isoformat()
        },
        {
            "source": "Aktualności (media)",
            "reliability": "semi-verified",
            "confidence": 85,
            "last_verification": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "source": "Dane finansowe (e-KRS)",
            "reliability": "verified",
            "confidence": 95,
            "last_verification": (datetime.now() - timedelta(days=180)).isoformat()
        }
    ]

    # Calculate reliability score as weighted average
    total_weight = len(source_reliability_details)
    weighted_confidence = sum(d["confidence"] for d in source_reliability_details) / total_weight

    if weighted_confidence >= 90:
        reliability_score = {"score": weighted_confidence, "status": "excellent"}
    elif weighted_confidence >= 75:
        reliability_score = {"score": weighted_confidence, "status": "good"}
    elif weighted_confidence >= 60:
        reliability_score = {"score": weighted_confidence, "status": "fair"}
    else:
        reliability_score = {"score": weighted_confidence, "status": "poor"}

    # Generate improvement suggestions
    improvement_suggestions = []

    if completeness_score["score"] < 80:
        improvement_suggestions.append({
            "priority": "high",
            "category": "completeness",
            "title": "Uzupełnij brakujące dane podstawowe",
            "description": f"Profil firmy jest kompletny w {completeness_score['score']:.1f}%. Uzupełnij brakujące pola: zarząd, wspólnicy, dane finansowe.",
            "impact": "Zwiększy wiarygodność profilu o ~25%"
        })

    if freshness_score["score"] < 70:
        improvement_suggestions.append({
            "priority": "medium",
            "category": "freshness",
            "title": "Odśwież dane z zewnętrznych źródeł",
            "description": "Niektóre dane nie były aktualizowane od ponad 90 dni. Zalecane odświeżenie danych ze struktur własnościowych i finansów.",
            "impact": "Zwiększy aktualność o ~30%"
        })

    if reliability_score["score"] < 80:
        improvement_suggestions.append({
            "priority": "medium",
            "category": "reliability",
            "title": "Zweryfikuj dane z niezaufanych źródeł",
            "description": "Część danych pochodzi ze źródeł o niższej wiarygodności (web scraping). Zalecana weryfikacja z oficjalnymi źródłami.",
            "impact": "Zwiększy pewność danych o ~15%"
        })

    # No suggestions? Add generic one
    if not improvement_suggestions:
        improvement_suggestions.append({
            "priority": "low",
            "category": "monitoring",
            "title": "Włącz automatyczne aktualizacje",
            "description": "Profil jest kompletny i aktualny. Rozważ włączenie automatycznych aktualizacji aby utrzymać wysoką jakość.",
            "impact": "Utrzyma jakość danych na poziomie 90%+"
        })

    # Calculate overall score (weighted average)
    overall_score = (
        completeness_score["score"] * 0.4 +  # 40% weight
        freshness_score["score"] * 0.3 +      # 30% weight
        reliability_score["score"] * 0.3       # 30% weight
    )

    if overall_score >= 85:
        overall_status = "excellent"
    elif overall_score >= 70:
        overall_status = "good"
    elif overall_score >= 50:
        overall_status = "fair"
    else:
        overall_status = "poor"

    return DataQualityDashboard(
        company_id=company_id,
        company_name=company["name"],
        overall_score=round(overall_score, 1),
        overall_status=overall_status,
        completeness=DataQualityMetric(
            score=completeness_score["score"],
            status=completeness_score["status"],
            details=completeness_details
        ),
        freshness=DataQualityMetric(
            score=freshness_score["score"],
            status=freshness_score["status"],
            details=freshness_details
        ),
        source_reliability=DataQualityMetric(
            score=reliability_score["score"],
            status=reliability_score["status"],
            details=source_reliability_details
        ),
        improvement_suggestions=improvement_suggestions,
        last_assessment=datetime.now().isoformat()
    )


# Data Conflict Resolution Models
class DataConflictValue(BaseModel):
    value: str
    source: str
    confidence: float  # 0-100
    last_updated: str
    is_verified: bool


class DataConflict(BaseModel):
    field_name: str
    field_label: str
    conflicting_values: List[DataConflictValue]
    recommended_value_index: Optional[int] = None  # Index of recommended value in conflicting_values


class DataConflictsResponse(BaseModel):
    company_id: int
    company_name: str
    conflicts: List[DataConflict]
    conflict_count: int


class ResolveConflictRequest(BaseModel):
    field_name: str
    selected_value: str
    selected_source: str


@router.get("/conflicts/{company_id}", response_model=DataConflictsResponse)
async def get_data_conflicts(
    company_id: int,
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Get data conflicts for a company.
    Returns fields where multiple sources provide different values.
    """
    # Mock data - company with conflicts
    if company_id == 1:  # FADO
        conflicts = [
            DataConflict(
                field_name="founded_year",
                field_label="Rok założenia",
                conflicting_values=[
                    DataConflictValue(
                        value="2005",
                        source="KRS (rządowe)",
                        confidence=95.0,
                        last_updated=(datetime.now() - timedelta(days=30)).isoformat(),
                        is_verified=True
                    ),
                    DataConflictValue(
                        value="2006",
                        source="Strona WWW",
                        confidence=70.0,
                        last_updated=(datetime.now() - timedelta(days=7)).isoformat(),
                        is_verified=False
                    )
                ],
                recommended_value_index=0  # Recommend KRS value
            ),
            DataConflict(
                field_name="employees_count",
                field_label="Liczba pracowników",
                conflicting_values=[
                    DataConflictValue(
                        value="150-200",
                        source="LinkedIn",
                        confidence=75.0,
                        last_updated=(datetime.now() - timedelta(days=15)).isoformat(),
                        is_verified=False
                    ),
                    DataConflictValue(
                        value="120-150",
                        source="Strona WWW",
                        confidence=60.0,
                        last_updated=(datetime.now() - timedelta(days=60)).isoformat(),
                        is_verified=False
                    ),
                    DataConflictValue(
                        value="180",
                        source="GUS",
                        confidence=85.0,
                        last_updated=(datetime.now() - timedelta(days=90)).isoformat(),
                        is_verified=True
                    )
                ],
                recommended_value_index=2  # Recommend GUS value (verified + highest confidence)
            )
        ]

        return DataConflictsResponse(
            company_id=company_id,
            company_name="FADO Sp. z o.o.",
            conflicts=conflicts,
            conflict_count=len(conflicts)
        )

    # No conflicts for other companies
    return DataConflictsResponse(
        company_id=company_id,
        company_name="Company Name",
        conflicts=[],
        conflict_count=0
    )


@router.post("/conflicts/{company_id}/resolve")
async def resolve_data_conflict(
    company_id: int,
    request: ResolveConflictRequest,
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Resolve a data conflict by selecting preferred value.
    In production, this would update the company record.
    """
    return {
        "success": True,
        "message": f"Conflict for '{request.field_name}' resolved",
        "selected_value": request.selected_value,
        "selected_source": request.selected_source,
        "company_id": company_id
    }
