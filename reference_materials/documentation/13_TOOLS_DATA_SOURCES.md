# 13. Tools - Data Sources

## Przegląd

Integracje ze źródłami danych:
1. **Polish Registries** - KRS, CEIDG, REGON, CRBR
2. **Company Intelligence** - LinkedIn, Glassdoor
3. **Web Intelligence** - SimilarWeb, SemRush
4. **News & Media** - Google News, Polish portals
5. **Financial Data** - e-KRS, EMIS, InfoVeriti

---

## 1. POLISH REGISTRIES

### 1.1 KRS API Client

```python
# tools/data_sources/krs_client.py

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import aiohttp
import re

@dataclass
class KRSCompany:
    """Dane firmy z KRS"""
    krs_number: str
    name: str
    name_short: Optional[str]
    legal_form: str
    registration_date: datetime
    nip: Optional[str]
    regon: Optional[str]
    
    # Adres
    street: str
    building_number: str
    apartment_number: Optional[str]
    postal_code: str
    city: str
    voivodeship: str
    country: str
    
    # Kapitał
    share_capital: Optional[float]
    share_capital_currency: str
    
    # Status
    status: str  # ACTIVE, LIQUIDATION, BANKRUPTCY, DELETED
    
    # Przedmiot działalności
    pkd_main: str
    pkd_main_description: str
    pkd_additional: List[Dict[str, str]]
    
    # Organy
    management_board: List[Dict]
    supervisory_board: List[Dict]
    shareholders: List[Dict]
    proxies: List[Dict]
    
    # Daty
    last_update: datetime
    
    # Raw data
    raw_data: Dict


class KRSClient:
    """
    Klient do API KRS (Krajowy Rejestr Sądowy).
    Używa API rejestr.io oraz oficjalnego API KRS.
    """
    
    # Endpointy
    KRS_OFFICIAL_API = "https://api-krs.ms.gov.pl/api/krs"
    REJESTR_IO_API = "https://rejestr.io/api/v2"
    
    def __init__(self, rejestr_io_token: Optional[str] = None):
        self.rejestr_io_token = rejestr_io_token
    
    async def search_by_name(
        self, 
        name: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Wyszukaj firmy po nazwie.
        """
        async with aiohttp.ClientSession() as session:
            # Spróbuj rejestr.io (lepsze wyniki)
            if self.rejestr_io_token:
                results = await self._search_rejestr_io(session, name, limit)
                if results:
                    return results
            
            # Fallback do oficjalnego API
            return await self._search_official(session, name, limit)
    
    async def _search_rejestr_io(
        self, 
        session: aiohttp.ClientSession,
        name: str,
        limit: int
    ) -> List[Dict]:
        """Wyszukiwanie przez rejestr.io"""
        url = f"{self.REJESTR_IO_API}/companies"
        params = {
            'q': name,
            'limit': limit
        }
        headers = {
            'Authorization': f'Bearer {self.rejestr_io_token}'
        }
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
        except Exception as e:
            print(f"Rejestr.io error: {e}")
        
        return []
    
    async def _search_official(
        self, 
        session: aiohttp.ClientSession,
        name: str,
        limit: int
    ) -> List[Dict]:
        """Wyszukiwanie przez oficjalne API"""
        url = f"{self.KRS_OFFICIAL_API}/OdsyijlanieRejestrPrzedsiebiorcy"
        params = {
            'nazwa': name,
            'limit': limit
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('odpis', {}).get('items', [])
        except Exception as e:
            print(f"Official KRS error: {e}")
        
        return []
    
    async def get_by_krs(self, krs_number: str) -> Optional[KRSCompany]:
        """
        Pobierz pełne dane firmy po numerze KRS.
        """
        # Normalizuj numer KRS (10 cyfr, z zerami wiodącymi)
        krs_number = krs_number.zfill(10)
        
        async with aiohttp.ClientSession() as session:
            # Oficjalne API
            data = await self._fetch_official_krs(session, krs_number)
            
            if data:
                return self._parse_krs_response(data, krs_number)
        
        return None
    
    async def get_by_nip(self, nip: str) -> Optional[KRSCompany]:
        """
        Pobierz dane firmy po NIP.
        """
        # Usuń myślniki i spacje
        nip = re.sub(r'[\s-]', '', nip)
        
        # Najpierw znajdź KRS po NIP
        search_results = await self.search_by_nip(nip)
        
        if search_results:
            krs_number = search_results[0].get('krs')
            if krs_number:
                return await self.get_by_krs(krs_number)
        
        return None
    
    async def search_by_nip(self, nip: str) -> List[Dict]:
        """Wyszukaj firmę po NIP"""
        async with aiohttp.ClientSession() as session:
            if self.rejestr_io_token:
                url = f"{self.REJESTR_IO_API}/companies"
                params = {'nip': nip}
                headers = {'Authorization': f'Bearer {self.rejestr_io_token}'}
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('items', [])
        
        return []
    
    async def _fetch_official_krs(
        self, 
        session: aiohttp.ClientSession,
        krs_number: str
    ) -> Optional[Dict]:
        """Pobierz dane z oficjalnego API KRS"""
        url = f"{self.KRS_OFFICIAL_API}/OdpisPelny/{krs_number}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"KRS fetch error: {e}")
        
        return None
    
    def _parse_krs_response(self, data: Dict, krs_number: str) -> KRSCompany:
        """Parsowanie odpowiedzi z KRS API"""
        odpis = data.get('odpis', {})
        dane = odpis.get('dane', {})
        
        # Adres
        adres = dane.get('siedzibaIAdres', {}).get('adres', {})
        
        # Kapitał
        kapital = dane.get('kapital', {})
        share_capital = None
        if kapital.get('wysokoscKapitaluZakladowego'):
            try:
                share_capital = float(kapital['wysokoscKapitaluZakladowego'].replace(',', '.'))
            except:
                pass
        
        # PKD
        pkd_list = dane.get('dzialalnoscGospodarcza', {}).get('dzialalnosc', [])
        pkd_main = ''
        pkd_main_desc = ''
        pkd_additional = []
        
        for pkd in pkd_list:
            if pkd.get('glowna'):
                pkd_main = pkd.get('kodPKD', '')
                pkd_main_desc = pkd.get('opis', '')
            else:
                pkd_additional.append({
                    'code': pkd.get('kodPKD', ''),
                    'description': pkd.get('opis', '')
                })
        
        # Zarząd
        management_board = []
        for member in dane.get('reprezentacja', {}).get('sklad', []):
            management_board.append({
                'name': f"{member.get('imiona', '')} {member.get('nazwisko', '')}".strip(),
                'position': member.get('funkcja', ''),
                'since': member.get('dataOd')
            })
        
        # Rada Nadzorcza
        supervisory_board = []
        for member in dane.get('organNadzoru', {}).get('sklad', []):
            supervisory_board.append({
                'name': f"{member.get('imiona', '')} {member.get('nazwisko', '')}".strip(),
                'position': member.get('funkcja', ''),
                'since': member.get('dataOd')
            })
        
        # Wspólnicy
        shareholders = []
        for shareholder in dane.get('wspolnicy', []):
            shareholders.append({
                'name': shareholder.get('nazwa') or f"{shareholder.get('imiona', '')} {shareholder.get('nazwisko', '')}".strip(),
                'shares': shareholder.get('liczbaUdzialow'),
                'share_value': shareholder.get('wartoscUdzialow'),
                'percentage': shareholder.get('procentUdzialow')
            })
        
        # Status
        status = 'ACTIVE'
        if dane.get('czyWUpadlosci'):
            status = 'BANKRUPTCY'
        elif dane.get('czyWLikwidacji'):
            status = 'LIQUIDATION'
        elif dane.get('dataWykreslenia'):
            status = 'DELETED'
        
        return KRSCompany(
            krs_number=krs_number,
            name=dane.get('nazwa', ''),
            name_short=dane.get('nazwaSkrocona'),
            legal_form=dane.get('formaOrganizacyjna', ''),
            registration_date=datetime.fromisoformat(dane.get('dataRejestracjiWKRS', '2000-01-01')),
            nip=dane.get('nip'),
            regon=dane.get('regon'),
            street=adres.get('ulica', ''),
            building_number=adres.get('nrDomu', ''),
            apartment_number=adres.get('nrLokalu'),
            postal_code=adres.get('kodPocztowy', ''),
            city=adres.get('miejscowosc', ''),
            voivodeship=adres.get('wojewodztwo', ''),
            country=adres.get('kraj', 'POLSKA'),
            share_capital=share_capital,
            share_capital_currency='PLN',
            status=status,
            pkd_main=pkd_main,
            pkd_main_description=pkd_main_desc,
            pkd_additional=pkd_additional,
            management_board=management_board,
            supervisory_board=supervisory_board,
            shareholders=shareholders,
            proxies=[],
            last_update=datetime.now(),
            raw_data=data
        )
    
    async def get_financial_statements(self, krs_number: str) -> List[Dict]:
        """
        Pobierz linki do sprawozdań finansowych.
        """
        krs_number = krs_number.zfill(10)
        
        async with aiohttp.ClientSession() as session:
            url = f"https://ekrs.ms.gov.pl/api/SprawozaniaFinansowe/{krs_number}"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('sprawozdania', [])
            except Exception as e:
                print(f"Financial statements error: {e}")
        
        return []
```

### 1.2 CEIDG Client

```python
# tools/data_sources/ceidg_client.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import aiohttp

@dataclass
class CEIDGEntry:
    """Wpis z CEIDG (jednoosobowa działalność)"""
    name: str
    owner_name: str
    nip: str
    regon: str
    status: str  # AKTYWNY, ZAWIESZONY, WYKRESLONY
    
    # Adres główny
    main_address: Dict
    
    # Adres korespondencyjny
    correspondence_address: Optional[Dict]
    
    # Działalność
    pkd_main: str
    pkd_additional: List[str]
    
    # Daty
    start_date: str
    suspension_date: Optional[str]
    end_date: Optional[str]
    
    # Kontakt
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]


class CEIDGClient:
    """
    Klient do API CEIDG (Centralna Ewidencja i Informacja o Działalności Gospodarczej).
    """
    
    BASE_URL = "https://dane.biznes.gov.pl/api/ceidg/v2"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(
        self, 
        query: str = None,
        nip: str = None,
        regon: str = None,
        limit: int = 10
    ) -> List[CEIDGEntry]:
        """
        Wyszukaj wpisy w CEIDG.
        """
        params = {'limit': limit}
        
        if nip:
            params['nip'] = nip
        elif regon:
            params['regon'] = regon
        elif query:
            params['nazwa'] = query
        
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            async with session.get(
                f"{self.BASE_URL}/firmy",
                params=params,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_entry(item) for item in data.get('firmy', [])]
        
        return []
    
    def _parse_entry(self, data: Dict) -> CEIDGEntry:
        """Parse pojedynczego wpisu CEIDG"""
        return CEIDGEntry(
            name=data.get('nazwa', ''),
            owner_name=f"{data.get('imie', '')} {data.get('nazwisko', '')}".strip(),
            nip=data.get('nip', ''),
            regon=data.get('regon', ''),
            status=data.get('status', 'UNKNOWN'),
            main_address=data.get('adresGlowny', {}),
            correspondence_address=data.get('adresKorespondencyjny'),
            pkd_main=data.get('pkdGlowny', ''),
            pkd_additional=data.get('pkdDodatkowe', []),
            start_date=data.get('dataRozpoczecia'),
            suspension_date=data.get('dataZawieszenia'),
            end_date=data.get('dataZakonczenia'),
            email=data.get('email'),
            phone=data.get('telefon'),
            website=data.get('stronaWww')
        )
```

---

## 2. COMPANY INTELLIGENCE

### 2.1 LinkedIn Scraper

```python
# tools/data_sources/linkedin_scraper.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup

@dataclass
class LinkedInCompany:
    """Profil firmy z LinkedIn"""
    name: str
    tagline: Optional[str]
    description: Optional[str]
    website: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]  # "51-200 employees"
    headquarters: Optional[str]
    founded: Optional[int]
    specialties: List[str]
    linkedin_url: str
    logo_url: Optional[str]
    followers: Optional[int]
    employees_on_linkedin: Optional[int]

@dataclass
class LinkedInPerson:
    """Profil osoby z LinkedIn"""
    name: str
    headline: Optional[str]
    current_company: Optional[str]
    current_position: Optional[str]
    location: Optional[str]
    linkedin_url: str
    profile_image: Optional[str]


class LinkedInScraper:
    """
    Scraper do pobierania publicznych danych z LinkedIn.
    
    UWAGA: LinkedIn aktywnie blokuje scraping.
    Dla produkcji zalecane jest użycie oficjalnego API lub serwisów jak:
    - Proxycurl
    - PhantomBuster
    - Scrapin.io
    """
    
    # Używamy Proxycurl jako proxy do LinkedIn
    PROXYCURL_API = "https://nubela.co/proxycurl/api/v2"
    
    def __init__(self, proxycurl_api_key: str = None):
        self.api_key = proxycurl_api_key
    
    async def get_company(self, linkedin_url: str) -> Optional[LinkedInCompany]:
        """
        Pobierz profil firmy z LinkedIn.
        """
        if not self.api_key:
            return None
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.PROXYCURL_API}/linkedin/company"
            params = {'url': linkedin_url}
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_company(data, linkedin_url)
        
        return None
    
    async def search_company(self, name: str) -> List[Dict]:
        """
        Wyszukaj firmy na LinkedIn po nazwie.
        """
        if not self.api_key:
            return []
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.PROXYCURL_API}/search/company"
            params = {
                'name': name,
                'country': 'PL'
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
        
        return []
    
    async def get_company_employees(
        self, 
        linkedin_url: str,
        role_filter: str = None
    ) -> List[LinkedInPerson]:
        """
        Pobierz listę pracowników firmy.
        """
        if not self.api_key:
            return []
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.PROXYCURL_API}/linkedin/company/employees"
            params = {
                'url': linkedin_url,
                'role_search': role_filter,
                'page_size': 50
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_person(p) for p in data.get('employees', [])]
        
        return []
    
    def _parse_company(self, data: Dict, url: str) -> LinkedInCompany:
        """Parse danych firmy"""
        return LinkedInCompany(
            name=data.get('name', ''),
            tagline=data.get('tagline'),
            description=data.get('description'),
            website=data.get('website'),
            industry=data.get('industry'),
            company_size=data.get('company_size'),
            headquarters=data.get('headquarters'),
            founded=data.get('founded'),
            specialties=data.get('specialties', []),
            linkedin_url=url,
            logo_url=data.get('logo'),
            followers=data.get('followers'),
            employees_on_linkedin=data.get('employees_on_linkedin')
        )
    
    def _parse_person(self, data: Dict) -> LinkedInPerson:
        """Parse danych osoby"""
        return LinkedInPerson(
            name=data.get('name', ''),
            headline=data.get('headline'),
            current_company=data.get('current_company'),
            current_position=data.get('current_position'),
            location=data.get('location'),
            linkedin_url=data.get('linkedin_url', ''),
            profile_image=data.get('profile_pic')
        )
```

---

## 3. WEB INTELLIGENCE

### 3.1 SimilarWeb API Client

```python
# tools/data_sources/similarweb_client.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import aiohttp

@dataclass
class WebsiteTraffic:
    """Dane o ruchu na stronie"""
    domain: str
    global_rank: Optional[int]
    country_rank: Optional[int]  # Rank w Polsce
    category_rank: Optional[int]
    
    # Traffic
    total_visits: int  # Miesięczne wizyty
    bounce_rate: float  # %
    pages_per_visit: float
    avg_visit_duration: float  # sekundy
    
    # Traffic sources
    traffic_sources: Dict[str, float]  # direct, referral, search, social, mail, ads
    
    # Geography
    top_countries: List[Dict]  # country, share
    
    # Competitors
    similar_sites: List[str]


class SimilarWebClient:
    """
    Klient do SimilarWeb API.
    """
    
    BASE_URL = "https://api.similarweb.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_traffic(self, domain: str) -> Optional[WebsiteTraffic]:
        """
        Pobierz dane o ruchu na domenie.
        """
        async with aiohttp.ClientSession() as session:
            # Traffic overview
            overview = await self._get_traffic_overview(session, domain)
            
            if not overview:
                return None
            
            # Traffic sources
            sources = await self._get_traffic_sources(session, domain)
            
            # Geography
            geo = await self._get_geography(session, domain)
            
            # Similar sites
            similar = await self._get_similar_sites(session, domain)
            
            return WebsiteTraffic(
                domain=domain,
                global_rank=overview.get('global_rank'),
                country_rank=overview.get('country_rank'),
                category_rank=overview.get('category_rank'),
                total_visits=overview.get('visits', 0),
                bounce_rate=overview.get('bounce_rate', 0),
                pages_per_visit=overview.get('pages_per_visit', 0),
                avg_visit_duration=overview.get('average_visit_duration', 0),
                traffic_sources=sources,
                top_countries=geo,
                similar_sites=similar
            )
    
    async def _get_traffic_overview(self, session: aiohttp.ClientSession, domain: str) -> Dict:
        """Pobierz overview ruchu"""
        url = f"{self.BASE_URL}/website/{domain}/total-traffic-and-engagement/visits"
        params = {
            'api_key': self.api_key,
            'start_date': '2024-01',
            'end_date': '2024-12',
            'country': 'world',
            'granularity': 'monthly',
            'main_domain_only': 'false'
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"SimilarWeb overview error: {e}")
        
        return {}
    
    async def _get_traffic_sources(self, session: aiohttp.ClientSession, domain: str) -> Dict[str, float]:
        """Pobierz źródła ruchu"""
        url = f"{self.BASE_URL}/website/{domain}/traffic-sources/overview"
        params = {'api_key': self.api_key}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'direct': data.get('direct', 0),
                        'referral': data.get('referrals', 0),
                        'search': data.get('search', 0),
                        'social': data.get('social', 0),
                        'mail': data.get('mail', 0),
                        'ads': data.get('paid', 0)
                    }
        except Exception as e:
            print(f"SimilarWeb sources error: {e}")
        
        return {}
    
    async def _get_geography(self, session: aiohttp.ClientSession, domain: str) -> List[Dict]:
        """Pobierz geografię odwiedzających"""
        url = f"{self.BASE_URL}/website/{domain}/geo/traffic-by-country"
        params = {'api_key': self.api_key}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('records', [])[:10]
        except Exception as e:
            print(f"SimilarWeb geo error: {e}")
        
        return []
    
    async def _get_similar_sites(self, session: aiohttp.ClientSession, domain: str) -> List[str]:
        """Pobierz podobne strony"""
        url = f"{self.BASE_URL}/website/{domain}/similarsites"
        params = {'api_key': self.api_key}
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [site.get('url') for site in data.get('similar_sites', [])[:10]]
        except Exception as e:
            print(f"SimilarWeb similar error: {e}")
        
        return []
```

---

## 4. NEWS & MEDIA

### 4.1 News Aggregator

```python
# tools/data_sources/news_aggregator.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import aiohttp
import feedparser

@dataclass
class NewsArticle:
    """Artykuł newsowy"""
    title: str
    url: str
    source: str
    published_date: datetime
    snippet: str
    image_url: Optional[str]
    sentiment: Optional[str]  # positive, neutral, negative


class NewsAggregator:
    """
    Agregator newsów z wielu źródeł.
    """
    
    # Google News RSS
    GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
    
    # Polskie portale biznesowe
    POLISH_SOURCES = {
        'pulshr': 'https://www.pulshr.pl/rss/',
        'money': 'https://www.money.pl/rss/',
        'bankier': 'https://www.bankier.pl/rss/',
        'parkiet': 'https://www.parkiet.com/rss/',
        'forsal': 'https://forsal.pl/rss/',
        'pb': 'https://www.pb.pl/rss/'
    }
    
    def __init__(self, serpapi_key: str = None):
        self.serpapi_key = serpapi_key
    
    async def search(
        self, 
        query: str,
        days: int = 30,
        language: str = 'pl',
        max_results: int = 20
    ) -> List[NewsArticle]:
        """
        Wyszukaj newsy o danym temacie.
        """
        articles = []
        
        # 1. Google News via SerpAPI (jeśli dostępne)
        if self.serpapi_key:
            google_articles = await self._search_google_news(query, days, max_results)
            articles.extend(google_articles)
        
        # 2. Google News RSS (fallback)
        else:
            rss_articles = await self._search_google_rss(query, language)
            articles.extend(rss_articles)
        
        # 3. Polskie źródła
        polish_articles = await self._search_polish_sources(query)
        articles.extend(polish_articles)
        
        # Deduplikacja po URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        # Sortuj po dacie
        unique_articles.sort(key=lambda x: x.published_date, reverse=True)
        
        return unique_articles[:max_results]
    
    async def _search_google_news(
        self, 
        query: str, 
        days: int,
        max_results: int
    ) -> List[NewsArticle]:
        """Wyszukiwanie przez Google News (SerpAPI)"""
        articles = []
        
        async with aiohttp.ClientSession() as session:
            url = "https://serpapi.com/search"
            params = {
                'engine': 'google_news',
                'q': query,
                'gl': 'pl',
                'hl': 'pl',
                'api_key': self.serpapi_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('news_results', [])[:max_results]:
                        articles.append(NewsArticle(
                            title=item.get('title', ''),
                            url=item.get('link', ''),
                            source=item.get('source', {}).get('name', ''),
                            published_date=self._parse_date(item.get('date', '')),
                            snippet=item.get('snippet', ''),
                            image_url=item.get('thumbnail'),
                            sentiment=None
                        ))
        
        return articles
    
    async def _search_google_rss(self, query: str, language: str) -> List[NewsArticle]:
        """Wyszukiwanie przez Google News RSS"""
        articles = []
        
        url = f"{self.GOOGLE_NEWS_RSS}?q={query}&hl={language}&gl=PL&ceid=PL:{language}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    for entry in feed.entries[:20]:
                        articles.append(NewsArticle(
                            title=entry.get('title', ''),
                            url=entry.get('link', ''),
                            source=entry.get('source', {}).get('title', 'Google News'),
                            published_date=self._parse_feedparser_date(entry.get('published_parsed')),
                            snippet=entry.get('summary', '')[:300],
                            image_url=None,
                            sentiment=None
                        ))
        
        return articles
    
    async def _search_polish_sources(self, query: str) -> List[NewsArticle]:
        """Przeszukaj polskie źródła RSS"""
        articles = []
        
        # TODO: Implementacja wyszukiwania w polskich RSS
        # Na razie zwracamy pustą listę
        
        return articles
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse daty z różnych formatów"""
        try:
            # "2 days ago", "1 hour ago", etc.
            if 'ago' in date_str.lower():
                if 'hour' in date_str:
                    hours = int(date_str.split()[0])
                    return datetime.now() - timedelta(hours=hours)
                elif 'day' in date_str:
                    days = int(date_str.split()[0])
                    return datetime.now() - timedelta(days=days)
                elif 'week' in date_str:
                    weeks = int(date_str.split()[0])
                    return datetime.now() - timedelta(weeks=weeks)
            
            # ISO format
            return datetime.fromisoformat(date_str)
        except:
            return datetime.now()
    
    def _parse_feedparser_date(self, parsed) -> datetime:
        """Parse daty z feedparser"""
        if parsed:
            return datetime(*parsed[:6])
        return datetime.now()
    
    async def analyze_sentiment(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Dodaj analizę sentymentu do artykułów.
        Wymaga integracji z LLM lub dedykowanym modelem.
        """
        # TODO: Implementacja przez Claude API
        return articles
```

---

## 5. FINANCIAL DATA

### 5.1 Financial Statements Fetcher

```python
# tools/data_sources/financial_fetcher.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import aiohttp
import PyPDF2
from io import BytesIO

@dataclass
class FinancialStatement:
    """Sprawozdanie finansowe"""
    company_name: str
    krs: str
    year: int
    type: str  # annual, quarterly
    
    # Rachunek zysków i strat
    revenue: Optional[float]
    operating_profit: Optional[float]
    net_profit: Optional[float]
    
    # Bilans
    total_assets: Optional[float]
    equity: Optional[float]
    liabilities: Optional[float]
    
    # Cash flow
    operating_cash_flow: Optional[float]
    investing_cash_flow: Optional[float]
    financing_cash_flow: Optional[float]
    
    # Wskaźniki
    employees: Optional[int]
    
    # Źródło
    source_url: str
    extracted_from_pdf: bool


class FinancialFetcher:
    """
    Pobieranie i parsowanie sprawozdań finansowych.
    """
    
    EKRS_API = "https://ekrs.ms.gov.pl/api"
    
    async def get_statements(
        self, 
        krs: str, 
        years: int = 3
    ) -> List[FinancialStatement]:
        """
        Pobierz sprawozdania finansowe za ostatnie N lat.
        """
        krs = krs.zfill(10)
        statements = []
        
        # 1. Pobierz listę sprawozdań z e-KRS
        statement_links = await self._get_statement_links(krs)
        
        # 2. Dla każdego sprawozdania pobierz PDF i wyekstrahuj dane
        for link in statement_links[:years]:
            statement = await self._extract_statement(krs, link)
            if statement:
                statements.append(statement)
        
        return statements
    
    async def _get_statement_links(self, krs: str) -> List[Dict]:
        """Pobierz linki do sprawozdań z e-KRS"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.EKRS_API}/SprawozdaniaFinansowe/{krs}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('sprawozdania', [])
        
        return []
    
    async def _extract_statement(self, krs: str, link_data: Dict) -> Optional[FinancialStatement]:
        """Pobierz PDF i wyekstrahuj dane"""
        pdf_url = link_data.get('url')
        year = link_data.get('rok')
        
        if not pdf_url:
            return None
        
        # Pobierz PDF
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status != 200:
                    return None
                
                pdf_bytes = await response.read()
        
        # Parsuj PDF
        extracted = await self._parse_financial_pdf(pdf_bytes)
        
        return FinancialStatement(
            company_name=link_data.get('nazwa', ''),
            krs=krs,
            year=year,
            type='annual',
            revenue=extracted.get('revenue'),
            operating_profit=extracted.get('operating_profit'),
            net_profit=extracted.get('net_profit'),
            total_assets=extracted.get('total_assets'),
            equity=extracted.get('equity'),
            liabilities=extracted.get('liabilities'),
            operating_cash_flow=extracted.get('operating_cf'),
            investing_cash_flow=extracted.get('investing_cf'),
            financing_cash_flow=extracted.get('financing_cf'),
            employees=extracted.get('employees'),
            source_url=pdf_url,
            extracted_from_pdf=True
        )
    
    async def _parse_financial_pdf(self, pdf_bytes: bytes) -> Dict:
        """
        Parsuj PDF sprawozdania finansowego.
        Używa LLM do ekstrakcji strukturalnej.
        """
        # 1. Wyciągnij tekst z PDF
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages[:20]:  # Pierwsze 20 stron
            text += page.extract_text() + "\n"
        
        # 2. Użyj LLM do ekstrakcji (implementacja przez agenta)
        # TODO: Integracja z Claude API
        
        # Na razie zwracamy pusty słownik
        return {}
    
    def calculate_ratios(self, statement: FinancialStatement) -> Dict:
        """
        Oblicz wskaźniki finansowe.
        """
        ratios = {}
        
        # Rentowność
        if statement.revenue and statement.revenue > 0:
            if statement.net_profit:
                ratios['net_margin'] = statement.net_profit / statement.revenue * 100
            if statement.operating_profit:
                ratios['operating_margin'] = statement.operating_profit / statement.revenue * 100
        
        # ROE
        if statement.equity and statement.equity > 0 and statement.net_profit:
            ratios['roe'] = statement.net_profit / statement.equity * 100
        
        # ROA
        if statement.total_assets and statement.total_assets > 0 and statement.net_profit:
            ratios['roa'] = statement.net_profit / statement.total_assets * 100
        
        # Zadłużenie
        if statement.total_assets and statement.total_assets > 0 and statement.liabilities:
            ratios['debt_ratio'] = statement.liabilities / statement.total_assets * 100
        
        # Equity ratio
        if statement.total_assets and statement.total_assets > 0 and statement.equity:
            ratios['equity_ratio'] = statement.equity / statement.total_assets * 100
        
        return ratios
```

---

## 6. UNIFIED DATA CLIENT

### 6.1 Data Client Facade

```python
# tools/data_sources/unified_client.py

from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from .krs_client import KRSClient, KRSCompany
from .ceidg_client import CEIDGClient, CEIDGEntry
from .linkedin_scraper import LinkedInScraper, LinkedInCompany
from .similarweb_client import SimilarWebClient, WebsiteTraffic
from .news_aggregator import NewsAggregator, NewsArticle
from .financial_fetcher import FinancialFetcher, FinancialStatement

@dataclass
class CompanyFullProfile:
    """Pełny profil firmy z wielu źródeł"""
    # Identyfikacja
    name: str
    nip: Optional[str]
    regon: Optional[str]
    krs: Optional[str]
    
    # Dane rejestrowe
    registry_data: Optional[KRSCompany]
    ceidg_data: Optional[CEIDGEntry]
    
    # Online presence
    website: Optional[str]
    linkedin_data: Optional[LinkedInCompany]
    traffic_data: Optional[WebsiteTraffic]
    
    # Finanse
    financial_statements: List[FinancialStatement]
    
    # News
    recent_news: List[NewsArticle]
    
    # Meta
    data_sources: List[str]
    data_freshness: Dict[str, str]
    confidence_scores: Dict[str, float]


class UnifiedDataClient:
    """
    Fasada do pobierania danych z wielu źródeł.
    Zapewnia spójny interfejs i obsługuje failover.
    """
    
    def __init__(self, config: Dict[str, str]):
        # Inicjalizacja klientów
        self.krs = KRSClient(rejestr_io_token=config.get('rejestr_io_token'))
        self.ceidg = CEIDGClient(api_key=config.get('ceidg_api_key')) if config.get('ceidg_api_key') else None
        self.linkedin = LinkedInScraper(proxycurl_api_key=config.get('proxycurl_api_key'))
        self.similarweb = SimilarWebClient(api_key=config.get('similarweb_api_key')) if config.get('similarweb_api_key') else None
        self.news = NewsAggregator(serpapi_key=config.get('serpapi_key'))
        self.financial = FinancialFetcher()
    
    async def get_full_company_profile(
        self,
        identifier: str,
        identifier_type: str = 'auto'  # 'auto', 'name', 'nip', 'krs', 'website'
    ) -> CompanyFullProfile:
        """
        Pobierz pełny profil firmy z wszystkich dostępnych źródeł.
        """
        data_sources = []
        confidence_scores = {}
        
        # 1. Określ typ identyfikatora jeśli auto
        if identifier_type == 'auto':
            identifier_type = self._detect_identifier_type(identifier)
        
        # 2. Pobierz dane rejestrowe
        registry_data = None
        ceidg_data = None
        
        if identifier_type == 'krs':
            registry_data = await self.krs.get_by_krs(identifier)
            if registry_data:
                data_sources.append('KRS')
                confidence_scores['KRS'] = 0.95
        
        elif identifier_type == 'nip':
            registry_data = await self.krs.get_by_nip(identifier)
            if registry_data:
                data_sources.append('KRS')
                confidence_scores['KRS'] = 0.95
            
            # Sprawdź też CEIDG
            if self.ceidg and not registry_data:
                ceidg_results = await self.ceidg.search(nip=identifier)
                if ceidg_results:
                    ceidg_data = ceidg_results[0]
                    data_sources.append('CEIDG')
                    confidence_scores['CEIDG'] = 0.95
        
        elif identifier_type == 'name':
            # Wyszukaj po nazwie
            krs_results = await self.krs.search_by_name(identifier)
            if krs_results:
                # Weź pierwszy wynik i pobierz pełne dane
                first_match = krs_results[0]
                if first_match.get('krs'):
                    registry_data = await self.krs.get_by_krs(first_match['krs'])
                    if registry_data:
                        data_sources.append('KRS')
                        confidence_scores['KRS'] = 0.8  # Niższy bo przez search
        
        # 3. Pobierz dane z LinkedIn
        linkedin_data = None
        company_name = registry_data.name if registry_data else identifier
        
        linkedin_results = await self.linkedin.search_company(company_name)
        if linkedin_results:
            linkedin_url = linkedin_results[0].get('linkedin_url')
            if linkedin_url:
                linkedin_data = await self.linkedin.get_company(linkedin_url)
                if linkedin_data:
                    data_sources.append('LinkedIn')
                    confidence_scores['LinkedIn'] = 0.85
        
        # 4. Pobierz dane o ruchu
        traffic_data = None
        website = None
        
        # Znajdź website z różnych źródeł
        if linkedin_data and linkedin_data.website:
            website = linkedin_data.website
        elif ceidg_data and ceidg_data.website:
            website = ceidg_data.website
        # TODO: Można też crawlować stronę KRS jeśli jest link
        
        if website and self.similarweb:
            from urllib.parse import urlparse
            domain = urlparse(website).netloc
            traffic_data = await self.similarweb.get_traffic(domain)
            if traffic_data:
                data_sources.append('SimilarWeb')
                confidence_scores['SimilarWeb'] = 0.9
        
        # 5. Pobierz sprawozdania finansowe
        financial_statements = []
        if registry_data and registry_data.krs_number:
            financial_statements = await self.financial.get_statements(
                registry_data.krs_number,
                years=3
            )
            if financial_statements:
                data_sources.append('e-KRS Financial')
                confidence_scores['Financial'] = 0.95
        
        # 6. Pobierz newsy
        recent_news = await self.news.search(company_name, days=90, max_results=10)
        if recent_news:
            data_sources.append('News')
            confidence_scores['News'] = 0.7
        
        return CompanyFullProfile(
            name=company_name,
            nip=registry_data.nip if registry_data else (ceidg_data.nip if ceidg_data else None),
            regon=registry_data.regon if registry_data else (ceidg_data.regon if ceidg_data else None),
            krs=registry_data.krs_number if registry_data else None,
            registry_data=registry_data,
            ceidg_data=ceidg_data,
            website=website,
            linkedin_data=linkedin_data,
            traffic_data=traffic_data,
            financial_statements=financial_statements,
            recent_news=recent_news,
            data_sources=data_sources,
            data_freshness={},  # TODO
            confidence_scores=confidence_scores
        )
    
    def _detect_identifier_type(self, identifier: str) -> str:
        """Wykryj typ identyfikatora"""
        import re
        
        # Usuń spacje i myślniki
        clean = re.sub(r'[\s-]', '', identifier)
        
        # NIP: 10 cyfr
        if re.match(r'^\d{10}$', clean):
            return 'nip'
        
        # KRS: 10 cyfr (z możliwymi zerami wiodącymi)
        if re.match(r'^\d{1,10}$', clean) and len(clean) <= 10:
            if int(clean) < 1000000000:  # KRS to max 10 cyfr
                return 'krs'
        
        # URL/website
        if identifier.startswith('http') or '.' in identifier:
            return 'website'
        
        # Default: nazwa
        return 'name'
```

---

*Następny dokument: 14_TOOLS_FILE_PROCESSING.md*
