"""
Companies API Endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


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
    "73.11.Z": {"name": "Działalność agencji reklamowych", "category": "Marketing"},
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
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """Search companies by name, NIP, or KRS."""
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

    return {"results": results[:limit], "total": len(results)}


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
        last_updated=COMPANY_LAST_UPDATED[company_id]
    )


@router.get("/{identifier}/financials")
async def get_company_financials(identifier: str):
    """Get company financial data."""
    # TODO: Implement financial data retrieval
    return {
        "company_id": identifier,
        "statements": [],
        "ratios": {}
    }


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
