# 12. Tools - Website Analysis

## Przegląd

Narzędzia do głębokiej analizy stron internetowych:
1. **Deep Crawler** - crawling wielopoziomowy
2. **Content Extractor** - ekstrakcja strukturalna
3. **Tech Stack Detector** - wykrywanie technologii
4. **Company Identifier** - identyfikacja firmy z website

---

## 1. DEEP CRAWLER

### 1.1 Architektura Crawlera

```python
# tools/website/deep_crawler.py

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

@dataclass
class CrawlConfig:
    """Konfiguracja crawlera"""
    max_depth: int = 3                    # Maksymalna głębokość
    max_pages: int = 50                   # Max stron do pobrania
    timeout: int = 30                     # Timeout per request
    delay: float = 0.5                    # Opóźnienie między requestami
    respect_robots: bool = True           # Respektuj robots.txt
    follow_external: bool = False         # Czy podążać za linkami zewnętrznymi
    include_patterns: List[str] = None    # Regex patterns do include
    exclude_patterns: List[str] = None    # Regex patterns do exclude
    extract_emails: bool = True
    extract_phones: bool = True
    extract_social: bool = True
    screenshot: bool = True               # Zrób screenshot strony głównej

@dataclass
class CrawledPage:
    """Pojedyncza przeczołgana strona"""
    url: str
    title: str
    meta_description: str
    meta_keywords: List[str]
    h1: List[str]
    h2: List[str]
    content_text: str                     # Oczyszczony tekst
    links_internal: List[str]
    links_external: List[str]
    images: List[Dict]                    # src, alt, title
    emails: List[str]
    phones: List[str]
    social_links: Dict[str, str]          # platform -> url
    structured_data: Dict                 # JSON-LD, microdata
    page_type: str                        # home, about, contact, product, blog, etc.
    depth: int
    crawl_time: float
    status_code: int
    content_length: int

@dataclass 
class CrawlResult:
    """Wynik pełnego crawla"""
    domain: str
    start_url: str
    pages: List[CrawledPage]
    site_structure: Dict                  # Hierarchia strony
    all_emails: Set[str]
    all_phones: Set[str]
    social_profiles: Dict[str, str]
    tech_stack: Dict
    company_info: Dict                    # Wyekstrahowane info o firmie
    crawl_stats: Dict                     # Statystyki crawla
    errors: List[Dict]
    screenshot_url: Optional[str]


class DeepCrawler:
    """
    Wielopoziomowy crawler do głębokiej analizy stron.
    """
    
    def __init__(self, config: CrawlConfig = None):
        self.config = config or CrawlConfig()
        self.visited: Set[str] = set()
        self.pages: List[CrawledPage] = []
        self.errors: List[Dict] = []
        self.robots_rules: Dict = {}
        
    async def crawl(self, start_url: str) -> CrawlResult:
        """
        Główna metoda crawlowania.
        """
        parsed = urlparse(start_url)
        self.domain = parsed.netloc
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 1. Pobierz robots.txt
        if self.config.respect_robots:
            await self._fetch_robots()
        
        # 2. Crawl rekurencyjnie
        async with aiohttp.ClientSession() as session:
            await self._crawl_page(session, start_url, depth=0)
        
        # 3. Agreguj wyniki
        result = self._aggregate_results(start_url)
        
        # 4. Screenshot (opcjonalnie)
        if self.config.screenshot:
            result.screenshot_url = await self._take_screenshot(start_url)
        
        return result
    
    async def _crawl_page(
        self, 
        session: aiohttp.ClientSession, 
        url: str, 
        depth: int
    ) -> Optional[CrawledPage]:
        """
        Crawl pojedynczej strony.
        """
        # Sprawdź limity
        if depth > self.config.max_depth:
            return None
        if len(self.visited) >= self.config.max_pages:
            return None
        if url in self.visited:
            return None
        if not self._is_allowed(url):
            return None
            
        self.visited.add(url)
        
        try:
            # Pobierz stronę
            start_time = asyncio.get_event_loop().time()
            async with session.get(url, timeout=self.config.timeout) as response:
                if response.status != 200:
                    self.errors.append({
                        'url': url,
                        'error': f'HTTP {response.status}',
                        'depth': depth
                    })
                    return None
                
                html = await response.text()
                crawl_time = asyncio.get_event_loop().time() - start_time
            
            # Parsuj stronę
            page = self._parse_page(url, html, depth, response.status, crawl_time)
            self.pages.append(page)
            
            # Delay
            await asyncio.sleep(self.config.delay)
            
            # Crawl linki wewnętrzne
            for link in page.links_internal:
                await self._crawl_page(session, link, depth + 1)
                
            return page
            
        except Exception as e:
            self.errors.append({
                'url': url,
                'error': str(e),
                'depth': depth
            })
            return None
    
    def _parse_page(
        self, 
        url: str, 
        html: str, 
        depth: int,
        status_code: int,
        crawl_time: float
    ) -> CrawledPage:
        """
        Parsowanie HTML i ekstrakcja danych.
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # Basic meta
        title = soup.title.string if soup.title else ''
        meta_desc = ''
        meta_keywords = []
        
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'description':
                meta_desc = meta.get('content', '')
            if meta.get('name') == 'keywords':
                meta_keywords = [k.strip() for k in meta.get('content', '').split(',')]
        
        # Headings
        h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
        
        # Content text (bez skryptów, stylów, nawigacji)
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        content_text = soup.get_text(separator=' ', strip=True)
        content_text = re.sub(r'\s+', ' ', content_text)
        
        # Links
        links_internal = []
        links_external = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            parsed = urlparse(href)
            if parsed.netloc == self.domain:
                if href not in links_internal:
                    links_internal.append(href)
            elif parsed.scheme in ['http', 'https']:
                if href not in links_external:
                    links_external.append(href)
        
        # Images
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': urljoin(url, img.get('src', '')),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        # Contact info
        emails = self._extract_emails(html) if self.config.extract_emails else []
        phones = self._extract_phones(html) if self.config.extract_phones else []
        social = self._extract_social_links(links_external) if self.config.extract_social else {}
        
        # Structured data
        structured_data = self._extract_structured_data(soup)
        
        # Page type classification
        page_type = self._classify_page_type(url, title, h1s, content_text)
        
        return CrawledPage(
            url=url,
            title=title,
            meta_description=meta_desc,
            meta_keywords=meta_keywords,
            h1=h1s,
            h2=h2s,
            content_text=content_text[:10000],  # Limit
            links_internal=links_internal[:100],
            links_external=links_external[:50],
            images=images[:50],
            emails=emails,
            phones=phones,
            social_links=social,
            structured_data=structured_data,
            page_type=page_type,
            depth=depth,
            crawl_time=crawl_time,
            status_code=status_code,
            content_length=len(html)
        )
    
    def _extract_emails(self, html: str) -> List[str]:
        """Ekstrakcja adresów email"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(pattern, html)
        # Filtruj fałszywe (np. example@example.com)
        filtered = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'email@'])]
        return list(set(filtered))
    
    def _extract_phones(self, html: str) -> List[str]:
        """Ekstrakcja numerów telefonów (format PL)"""
        patterns = [
            r'\+48[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',  # +48 xxx xxx xxx
            r'\(\+48\)[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',  # xxx xxx xxx
            r'\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}',  # xx xxx xx xx
        ]
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, html))
        return list(set(phones))
    
    def _extract_social_links(self, external_links: List[str]) -> Dict[str, str]:
        """Ekstrakcja linków do social media"""
        social_domains = {
            'linkedin.com': 'linkedin',
            'facebook.com': 'facebook',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'instagram.com': 'instagram',
            'youtube.com': 'youtube',
            'tiktok.com': 'tiktok',
            'github.com': 'github'
        }
        
        social = {}
        for link in external_links:
            parsed = urlparse(link)
            for domain, platform in social_domains.items():
                if domain in parsed.netloc:
                    social[platform] = link
                    break
        return social
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Ekstrakcja JSON-LD i innych structured data"""
        import json
        
        structured = {
            'json_ld': [],
            'og': {},
            'twitter': {}
        }
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured['json_ld'].append(data)
            except:
                pass
        
        # Open Graph
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            key = meta.get('property', '').replace('og:', '')
            structured['og'][key] = meta.get('content', '')
        
        # Twitter Cards
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            key = meta.get('name', '').replace('twitter:', '')
            structured['twitter'][key] = meta.get('content', '')
        
        return structured
    
    def _classify_page_type(
        self, 
        url: str, 
        title: str, 
        h1s: List[str], 
        content: str
    ) -> str:
        """Klasyfikacja typu strony"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # URL-based classification
        if any(x in url_lower for x in ['/o-nas', '/about', '/o-firmie', '/kim-jestesmy']):
            return 'about'
        if any(x in url_lower for x in ['/kontakt', '/contact']):
            return 'contact'
        if any(x in url_lower for x in ['/produkt', '/product', '/sklep', '/shop']):
            return 'product'
        if any(x in url_lower for x in ['/blog', '/aktualnosci', '/news']):
            return 'blog'
        if any(x in url_lower for x in ['/kariera', '/praca', '/career', '/jobs']):
            return 'careers'
        if any(x in url_lower for x in ['/uslugi', '/services']):
            return 'services'
        if any(x in url_lower for x in ['/cennik', '/pricing']):
            return 'pricing'
        
        # Homepage detection
        parsed = urlparse(url)
        if parsed.path in ['', '/', '/index.html', '/index.php']:
            return 'home'
        
        return 'other'
    
    def _aggregate_results(self, start_url: str) -> CrawlResult:
        """Agregacja wyników crawla"""
        # Zbierz wszystkie emails, phones, social
        all_emails = set()
        all_phones = set()
        social_profiles = {}
        
        for page in self.pages:
            all_emails.update(page.emails)
            all_phones.update(page.phones)
            social_profiles.update(page.social_links)
        
        # Struktura strony
        site_structure = self._build_site_structure()
        
        # Company info z różnych źródeł
        company_info = self._extract_company_info()
        
        # Statystyki
        crawl_stats = {
            'pages_crawled': len(self.pages),
            'pages_failed': len(self.errors),
            'total_content_size': sum(p.content_length for p in self.pages),
            'avg_crawl_time': sum(p.crawl_time for p in self.pages) / len(self.pages) if self.pages else 0,
            'max_depth_reached': max(p.depth for p in self.pages) if self.pages else 0,
            'page_types': {}
        }
        
        for page in self.pages:
            pt = page.page_type
            crawl_stats['page_types'][pt] = crawl_stats['page_types'].get(pt, 0) + 1
        
        return CrawlResult(
            domain=self.domain,
            start_url=start_url,
            pages=self.pages,
            site_structure=site_structure,
            all_emails=all_emails,
            all_phones=all_phones,
            social_profiles=social_profiles,
            tech_stack={},  # Wypełniane przez TechStackDetector
            company_info=company_info,
            crawl_stats=crawl_stats,
            errors=self.errors,
            screenshot_url=None
        )
    
    def _build_site_structure(self) -> Dict:
        """Buduje hierarchiczną strukturę strony"""
        structure = {'children': {}}
        
        for page in self.pages:
            parsed = urlparse(page.url)
            path_parts = [p for p in parsed.path.split('/') if p]
            
            current = structure
            for part in path_parts:
                if part not in current['children']:
                    current['children'][part] = {
                        'children': {},
                        'page': None
                    }
                current = current['children'][part]
            
            current['page'] = {
                'url': page.url,
                'title': page.title,
                'type': page.page_type
            }
        
        return structure
    
    def _extract_company_info(self) -> Dict:
        """Ekstrahuje informacje o firmie z przeczołganych stron"""
        info = {
            'name': None,
            'description': None,
            'address': None,
            'nip': None,
            'regon': None,
            'krs': None,
            'email': None,
            'phone': None,
            'founding_year': None
        }
        
        # Szukaj na stronie głównej i about
        priority_pages = [p for p in self.pages if p.page_type in ['home', 'about', 'contact']]
        
        for page in priority_pages:
            # JSON-LD Organization
            for ld in page.structured_data.get('json_ld', []):
                if isinstance(ld, dict):
                    if ld.get('@type') in ['Organization', 'Corporation', 'LocalBusiness']:
                        info['name'] = info['name'] or ld.get('name')
                        info['description'] = info['description'] or ld.get('description')
                        if 'address' in ld:
                            info['address'] = ld['address']
            
            # NIP/REGON/KRS z tekstu
            nip_match = re.search(r'NIP[:\s]*(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})', page.content_text)
            if nip_match:
                info['nip'] = re.sub(r'[-\s]', '', nip_match.group(1))
            
            regon_match = re.search(r'REGON[:\s]*(\d{9}|\d{14})', page.content_text)
            if regon_match:
                info['regon'] = regon_match.group(1)
            
            krs_match = re.search(r'KRS[:\s]*(\d{10})', page.content_text)
            if krs_match:
                info['krs'] = krs_match.group(1)
        
        # Email i telefon - pierwszy znaleziony
        all_emails = [e for p in self.pages for e in p.emails]
        all_phones = [ph for p in self.pages for ph in p.phones]
        info['email'] = all_emails[0] if all_emails else None
        info['phone'] = all_phones[0] if all_phones else None
        
        return info
```

---

## 2. TECH STACK DETECTOR

### 2.1 Wykrywanie Technologii

```python
# tools/website/tech_detector.py

from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import aiohttp

@dataclass
class TechStackResult:
    """Wynik detekcji tech stacku"""
    cms: Optional[str]
    frameworks: List[str]
    javascript_libraries: List[str]
    analytics: List[str]
    marketing_tools: List[str]
    cdn: Optional[str]
    hosting: Optional[str]
    ecommerce: Optional[str]
    server: Optional[str]
    security: List[str]
    widgets: List[str]
    confidence_scores: Dict[str, float]


class TechStackDetector:
    """
    Wykrywanie technologii używanych na stronie.
    Inspirowane BuiltWith/Wappalyzer.
    """
    
    # Sygnatury technologii
    SIGNATURES = {
        'cms': {
            'WordPress': {
                'html': [r'wp-content', r'wp-includes', r'wordpress'],
                'headers': {'x-powered-by': r'wordpress'}
            },
            'Drupal': {
                'html': [r'Drupal', r'/sites/default/files'],
                'headers': {'x-generator': r'drupal'}
            },
            'Joomla': {
                'html': [r'/media/jui/', r'Joomla'],
            },
            'Shopify': {
                'html': [r'cdn\.shopify\.com', r'Shopify\.theme'],
            },
            'Wix': {
                'html': [r'wix\.com', r'_wix'],
            },
            'Squarespace': {
                'html': [r'squarespace', r'static\.squarespace'],
            }
        },
        'frameworks': {
            'React': {
                'html': [r'react', r'_react', r'__REACT'],
                'scripts': [r'react\.production\.min\.js', r'react-dom']
            },
            'Vue.js': {
                'html': [r'vue', r'__vue__'],
                'scripts': [r'vue\.min\.js', r'vue\.js']
            },
            'Angular': {
                'html': [r'ng-version', r'ng-app'],
                'scripts': [r'angular']
            },
            'Next.js': {
                'html': [r'__NEXT_DATA__', r'_next/static'],
            },
            'Nuxt.js': {
                'html': [r'__NUXT__', r'_nuxt/'],
            },
            'Laravel': {
                'cookies': [r'laravel_session'],
            },
            'Django': {
                'cookies': [r'csrftoken'],
                'html': [r'csrfmiddlewaretoken']
            },
            'Ruby on Rails': {
                'headers': {'x-powered-by': r'phusion'},
                'cookies': [r'_session_id']
            },
            'ASP.NET': {
                'headers': {'x-powered-by': r'asp\.net'},
                'cookies': [r'ASP\.NET_SessionId']
            },
            'Bootstrap': {
                'html': [r'bootstrap\.min\.css', r'bootstrap\.css'],
            },
            'Tailwind CSS': {
                'html': [r'tailwindcss', r'tailwind\.'],
            }
        },
        'analytics': {
            'Google Analytics': {
                'html': [r'google-analytics\.com', r'gtag', r'ga\.js', r'analytics\.js'],
            },
            'Google Tag Manager': {
                'html': [r'googletagmanager\.com', r'gtm\.js'],
            },
            'Facebook Pixel': {
                'html': [r'connect\.facebook\.net', r'fbevents\.js'],
            },
            'Hotjar': {
                'html': [r'hotjar\.com', r'static\.hotjar\.com'],
            },
            'Mixpanel': {
                'html': [r'mixpanel\.com', r'mixpanel'],
            },
            'Heap': {
                'html': [r'heap-analytics', r'heapanalytics'],
            },
            'Matomo/Piwik': {
                'html': [r'matomo', r'piwik'],
            }
        },
        'marketing': {
            'HubSpot': {
                'html': [r'hubspot', r'hs-scripts', r'hbspt'],
            },
            'Mailchimp': {
                'html': [r'mailchimp', r'mc\.js'],
            },
            'Intercom': {
                'html': [r'intercom', r'intercomSettings'],
            },
            'Drift': {
                'html': [r'drift\.com', r'driftt'],
            },
            'Zendesk': {
                'html': [r'zendesk', r'zdassets'],
            },
            'LiveChat': {
                'html': [r'livechatinc\.com', r'livechat'],
            },
            'Crisp': {
                'html': [r'crisp\.chat', r'crisp\.js'],
            }
        },
        'ecommerce': {
            'WooCommerce': {
                'html': [r'woocommerce', r'wc-'],
            },
            'Magento': {
                'html': [r'magento', r'mage/'],
                'cookies': [r'PHPSESSID']
            },
            'PrestaShop': {
                'html': [r'prestashop', r'presta'],
            },
            'Shopware': {
                'html': [r'shopware'],
            },
            'BigCommerce': {
                'html': [r'bigcommerce'],
            }
        },
        'cdn': {
            'Cloudflare': {
                'headers': {'server': r'cloudflare', 'cf-ray': r'.+'},
            },
            'Fastly': {
                'headers': {'x-served-by': r'cache', 'x-fastly': r'.+'},
            },
            'Akamai': {
                'headers': {'x-akamai': r'.+'},
            },
            'AWS CloudFront': {
                'headers': {'x-amz-cf-id': r'.+', 'via': r'cloudfront'},
            },
            'KeyCDN': {
                'headers': {'server': r'keycdn'},
            }
        },
        'security': {
            'reCAPTCHA': {
                'html': [r'recaptcha', r'google\.com/recaptcha'],
            },
            'hCaptcha': {
                'html': [r'hcaptcha'],
            },
            'SSL/HTTPS': {
                'url': [r'^https://'],
            }
        }
    }
    
    async def detect(self, url: str, html: str, headers: Dict) -> TechStackResult:
        """
        Wykryj technologie na podstawie HTML i headers.
        """
        results = {
            'cms': None,
            'frameworks': [],
            'javascript_libraries': [],
            'analytics': [],
            'marketing_tools': [],
            'cdn': None,
            'hosting': None,
            'ecommerce': None,
            'server': headers.get('server', ''),
            'security': [],
            'widgets': [],
            'confidence_scores': {}
        }
        
        # Detect CMS
        for cms_name, signatures in self.SIGNATURES['cms'].items():
            if self._match_signatures(html, headers, signatures):
                results['cms'] = cms_name
                results['confidence_scores'][cms_name] = 0.9
                break
        
        # Detect Frameworks
        for fw_name, signatures in self.SIGNATURES['frameworks'].items():
            if self._match_signatures(html, headers, signatures):
                results['frameworks'].append(fw_name)
                results['confidence_scores'][fw_name] = 0.85
        
        # Detect Analytics
        for tool_name, signatures in self.SIGNATURES['analytics'].items():
            if self._match_signatures(html, headers, signatures):
                results['analytics'].append(tool_name)
                results['confidence_scores'][tool_name] = 0.9
        
        # Detect Marketing Tools
        for tool_name, signatures in self.SIGNATURES['marketing'].items():
            if self._match_signatures(html, headers, signatures):
                results['marketing_tools'].append(tool_name)
                results['confidence_scores'][tool_name] = 0.85
        
        # Detect E-commerce
        for ecom_name, signatures in self.SIGNATURES['ecommerce'].items():
            if self._match_signatures(html, headers, signatures):
                results['ecommerce'] = ecom_name
                results['confidence_scores'][ecom_name] = 0.9
                break
        
        # Detect CDN
        for cdn_name, signatures in self.SIGNATURES['cdn'].items():
            if self._match_signatures(html, headers, signatures):
                results['cdn'] = cdn_name
                results['confidence_scores'][cdn_name] = 0.95
                break
        
        # Detect Security
        for sec_name, signatures in self.SIGNATURES['security'].items():
            if self._match_signatures(html, headers, signatures, url=url):
                results['security'].append(sec_name)
        
        # Additional JavaScript libraries from script tags
        results['javascript_libraries'] = self._detect_js_libraries(html)
        
        return TechStackResult(**results)
    
    def _match_signatures(
        self, 
        html: str, 
        headers: Dict, 
        signatures: Dict,
        url: str = ''
    ) -> bool:
        """Sprawdź czy sygnatury pasują"""
        # HTML patterns
        if 'html' in signatures:
            for pattern in signatures['html']:
                if re.search(pattern, html, re.IGNORECASE):
                    return True
        
        # Header patterns
        if 'headers' in signatures:
            for header_name, pattern in signatures['headers'].items():
                header_value = headers.get(header_name.lower(), '')
                if re.search(pattern, header_value, re.IGNORECASE):
                    return True
        
        # Cookie patterns (from Set-Cookie header)
        if 'cookies' in signatures:
            cookies = headers.get('set-cookie', '')
            for pattern in signatures['cookies']:
                if re.search(pattern, cookies, re.IGNORECASE):
                    return True
        
        # URL patterns
        if 'url' in signatures and url:
            for pattern in signatures['url']:
                if re.search(pattern, url, re.IGNORECASE):
                    return True
        
        return False
    
    def _detect_js_libraries(self, html: str) -> List[str]:
        """Wykryj popularne biblioteki JS"""
        libraries = []
        
        js_patterns = {
            'jQuery': r'jquery[\.-]?\d*\.?(min\.)?js',
            'Lodash': r'lodash',
            'Moment.js': r'moment\.js',
            'D3.js': r'd3\.v?\d*\.?(min\.)?js',
            'Chart.js': r'chart\.js',
            'Three.js': r'three\.js',
            'GSAP': r'gsap|greensock',
            'Axios': r'axios',
            'Socket.io': r'socket\.io',
            'Swiper': r'swiper',
            'Slick': r'slick',
            'AOS': r'aos\.js',
            'Lottie': r'lottie',
        }
        
        for lib_name, pattern in js_patterns.items():
            if re.search(pattern, html, re.IGNORECASE):
                libraries.append(lib_name)
        
        return libraries
```

---

## 3. CONTENT EXTRACTOR

### 3.1 Strukturalna Ekstrakcja

```python
# tools/website/content_extractor.py

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import re

@dataclass
class ExtractedProduct:
    """Wyekstrahowany produkt"""
    name: str
    price: Optional[str]
    currency: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    url: str
    sku: Optional[str]
    availability: Optional[str]

@dataclass
class ExtractedArticle:
    """Wyekstrahowany artykuł/news"""
    title: str
    date: Optional[str]
    author: Optional[str]
    content: str
    summary: Optional[str]
    url: str
    image_url: Optional[str]
    tags: List[str]

@dataclass
class ExtractedTeamMember:
    """Wyekstrahowany członek zespołu"""
    name: str
    position: Optional[str]
    bio: Optional[str]
    image_url: Optional[str]
    email: Optional[str]
    linkedin: Optional[str]

@dataclass
class ExtractedService:
    """Wyekstrahowana usługa"""
    name: str
    description: str
    features: List[str]
    price: Optional[str]
    url: Optional[str]


class ContentExtractor:
    """
    Ekstrahuje strukturalne dane z różnych typów stron.
    """
    
    def extract_products(self, html: str, url: str) -> List[ExtractedProduct]:
        """Ekstrakcja produktów z karty produktu lub listingu"""
        soup = BeautifulSoup(html, 'lxml')
        products = []
        
        # 1. Spróbuj JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Product':
                            products.append(self._parse_product_jsonld(item, url))
                elif data.get('@type') == 'Product':
                    products.append(self._parse_product_jsonld(data, url))
            except:
                pass
        
        if products:
            return products
        
        # 2. Fallback - heurystyka HTML
        # Szukaj typowych selektorów produktowych
        product_selectors = [
            '.product', '.product-item', '.product-card',
            '[itemtype*="Product"]', '.woocommerce-product',
            '.shop-item', '.catalog-item'
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            for el in elements:
                product = self._parse_product_html(el, url)
                if product.name:
                    products.append(product)
        
        return products
    
    def _parse_product_jsonld(self, data: Dict, base_url: str) -> ExtractedProduct:
        """Parse produktu z JSON-LD"""
        price = None
        currency = None
        
        if 'offers' in data:
            offers = data['offers']
            if isinstance(offers, list):
                offers = offers[0]
            price = offers.get('price')
            currency = offers.get('priceCurrency')
        
        return ExtractedProduct(
            name=data.get('name', ''),
            price=str(price) if price else None,
            currency=currency,
            description=data.get('description'),
            image_url=data.get('image'),
            url=data.get('url', base_url),
            sku=data.get('sku'),
            availability=data.get('offers', {}).get('availability')
        )
    
    def _parse_product_html(self, element, base_url: str) -> ExtractedProduct:
        """Parse produktu z HTML"""
        # Nazwa
        name = ''
        for sel in ['.product-name', '.product-title', 'h2', 'h3', '.title']:
            el = element.select_one(sel)
            if el:
                name = el.get_text(strip=True)
                break
        
        # Cena
        price = None
        for sel in ['.price', '.product-price', '.amount', '[itemprop="price"]']:
            el = element.select_one(sel)
            if el:
                price_text = el.get_text(strip=True)
                price_match = re.search(r'[\d\s,\.]+', price_text)
                if price_match:
                    price = price_match.group().strip()
                break
        
        # Obrazek
        image = None
        img = element.select_one('img')
        if img:
            image = img.get('src') or img.get('data-src')
        
        # URL
        link = element.select_one('a')
        product_url = base_url
        if link and link.get('href'):
            from urllib.parse import urljoin
            product_url = urljoin(base_url, link['href'])
        
        return ExtractedProduct(
            name=name,
            price=price,
            currency='PLN',  # Default
            description=None,
            image_url=image,
            url=product_url,
            sku=None,
            availability=None
        )
    
    def extract_articles(self, html: str, url: str) -> List[ExtractedArticle]:
        """Ekstrakcja artykułów z bloga/newsów"""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['Article', 'NewsArticle', 'BlogPosting']:
                            articles.append(self._parse_article_jsonld(item, url))
                elif data.get('@type') in ['Article', 'NewsArticle', 'BlogPosting']:
                    articles.append(self._parse_article_jsonld(data, url))
            except:
                pass
        
        if articles:
            return articles
        
        # Fallback HTML
        article_selectors = [
            'article', '.post', '.blog-post', '.news-item',
            '.article-item', '.entry'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for el in elements[:10]:  # Limit
                article = self._parse_article_html(el, url)
                if article.title:
                    articles.append(article)
        
        return articles
    
    def _parse_article_jsonld(self, data: Dict, base_url: str) -> ExtractedArticle:
        """Parse artykułu z JSON-LD"""
        author = None
        if 'author' in data:
            author_data = data['author']
            if isinstance(author_data, dict):
                author = author_data.get('name')
            elif isinstance(author_data, str):
                author = author_data
        
        return ExtractedArticle(
            title=data.get('headline', data.get('name', '')),
            date=data.get('datePublished'),
            author=author,
            content=data.get('articleBody', ''),
            summary=data.get('description'),
            url=data.get('url', base_url),
            image_url=data.get('image'),
            tags=data.get('keywords', [])
        )
    
    def _parse_article_html(self, element, base_url: str) -> ExtractedArticle:
        """Parse artykułu z HTML"""
        # Tytuł
        title = ''
        for sel in ['h1', 'h2', '.title', '.post-title', '.entry-title']:
            el = element.select_one(sel)
            if el:
                title = el.get_text(strip=True)
                break
        
        # Data
        date = None
        for sel in ['time', '.date', '.post-date', '[datetime]']:
            el = element.select_one(sel)
            if el:
                date = el.get('datetime') or el.get_text(strip=True)
                break
        
        # Autor
        author = None
        for sel in ['.author', '.post-author', '[rel="author"]']:
            el = element.select_one(sel)
            if el:
                author = el.get_text(strip=True)
                break
        
        # Content
        content = ''
        for sel in ['.content', '.post-content', '.entry-content', 'p']:
            els = element.select(sel)
            if els:
                content = ' '.join(e.get_text(strip=True) for e in els[:5])
                break
        
        # URL
        link = element.select_one('a')
        article_url = base_url
        if link and link.get('href'):
            from urllib.parse import urljoin
            article_url = urljoin(base_url, link['href'])
        
        return ExtractedArticle(
            title=title,
            date=date,
            author=author,
            content=content[:1000],
            summary=None,
            url=article_url,
            image_url=None,
            tags=[]
        )
    
    def extract_team(self, html: str, url: str) -> List[ExtractedTeamMember]:
        """Ekstrakcja zespołu ze strony 'O nas' / 'Zespół'"""
        soup = BeautifulSoup(html, 'lxml')
        team = []
        
        # Typowe selektory dla członków zespołu
        member_selectors = [
            '.team-member', '.person', '.staff-member',
            '.employee', '.member', '.team-item'
        ]
        
        for selector in member_selectors:
            elements = soup.select(selector)
            for el in elements[:20]:
                member = self._parse_team_member(el)
                if member.name:
                    team.append(member)
        
        return team
    
    def _parse_team_member(self, element) -> ExtractedTeamMember:
        """Parse członka zespołu z HTML"""
        # Imię i nazwisko
        name = ''
        for sel in ['h3', 'h4', '.name', '.member-name']:
            el = element.select_one(sel)
            if el:
                name = el.get_text(strip=True)
                break
        
        # Stanowisko
        position = None
        for sel in ['.position', '.title', '.role', '.job-title']:
            el = element.select_one(sel)
            if el:
                position = el.get_text(strip=True)
                break
        
        # Bio
        bio = None
        for sel in ['.bio', '.description', 'p']:
            el = element.select_one(sel)
            if el:
                bio = el.get_text(strip=True)
                break
        
        # Zdjęcie
        image = None
        img = element.select_one('img')
        if img:
            image = img.get('src')
        
        # LinkedIn
        linkedin = None
        for a in element.select('a'):
            href = a.get('href', '')
            if 'linkedin.com' in href:
                linkedin = href
                break
        
        # Email
        email = None
        for a in element.select('a[href^="mailto:"]'):
            email = a['href'].replace('mailto:', '')
            break
        
        return ExtractedTeamMember(
            name=name,
            position=position,
            bio=bio[:500] if bio else None,
            image_url=image,
            email=email,
            linkedin=linkedin
        )
    
    def extract_services(self, html: str, url: str) -> List[ExtractedService]:
        """Ekstrakcja usług ze strony 'Usługi'"""
        soup = BeautifulSoup(html, 'lxml')
        services = []
        
        service_selectors = [
            '.service', '.service-item', '.service-box',
            '.offer-item', '.product-service'
        ]
        
        for selector in service_selectors:
            elements = soup.select(selector)
            for el in elements[:15]:
                service = self._parse_service(el)
                if service.name:
                    services.append(service)
        
        return services
    
    def _parse_service(self, element) -> ExtractedService:
        """Parse usługi z HTML"""
        # Nazwa
        name = ''
        for sel in ['h3', 'h4', '.title', '.service-title']:
            el = element.select_one(sel)
            if el:
                name = el.get_text(strip=True)
                break
        
        # Opis
        description = ''
        for sel in ['.description', 'p', '.content']:
            el = element.select_one(sel)
            if el:
                description = el.get_text(strip=True)
                break
        
        # Features (lista)
        features = []
        ul = element.select_one('ul')
        if ul:
            for li in ul.select('li')[:10]:
                features.append(li.get_text(strip=True))
        
        return ExtractedService(
            name=name,
            description=description[:500],
            features=features,
            price=None,
            url=None
        )
```

---

## 4. OUTPUT FORMAT

### 4.1 Website Analysis Result

```json
{
  "website_analysis": {
    "url": "https://fado.pl",
    "domain": "fado.pl",
    "crawl_date": "2025-01-13T10:30:00Z",
    
    "company_info": {
      "name": "FADO Sp. z o.o.",
      "nip": "5542717533",
      "regon": "093193958",
      "address": "ul. Fabryczna 1, 85-741 Bydgoszcz",
      "email": "biuro@fado.pl",
      "phone": "+48 52 345 67 89",
      "description": "Producent armatury przemysłowej"
    },
    
    "tech_stack": {
      "cms": "WordPress",
      "frameworks": ["Bootstrap", "jQuery"],
      "analytics": ["Google Analytics", "Google Tag Manager"],
      "marketing_tools": ["HubSpot"],
      "cdn": "Cloudflare",
      "ecommerce": "WooCommerce",
      "server": "nginx",
      "security": ["SSL/HTTPS", "reCAPTCHA"]
    },
    
    "site_structure": {
      "pages_crawled": 42,
      "max_depth": 3,
      "page_types": {
        "home": 1,
        "about": 2,
        "products": 25,
        "blog": 10,
        "contact": 1,
        "other": 3
      },
      "key_pages": [
        {"url": "/o-nas", "title": "O firmie", "type": "about"},
        {"url": "/produkty", "title": "Produkty", "type": "products"},
        {"url": "/kontakt", "title": "Kontakt", "type": "contact"}
      ]
    },
    
    "content_summary": {
      "products_found": 45,
      "blog_posts_found": 28,
      "team_members_found": 8,
      "services_found": 5
    },
    
    "social_media": {
      "linkedin": "https://linkedin.com/company/fado",
      "facebook": "https://facebook.com/fado.pl",
      "youtube": "https://youtube.com/@fado"
    },
    
    "contact_info": {
      "emails": ["biuro@fado.pl", "sprzedaz@fado.pl"],
      "phones": ["+48 52 345 67 89", "+48 52 345 67 90"]
    },
    
    "seo_analysis": {
      "meta_titles_coverage": 95,
      "meta_descriptions_coverage": 78,
      "h1_coverage": 100,
      "images_with_alt": 65,
      "mobile_friendly": true,
      "https": true
    },
    
    "crawl_stats": {
      "duration_seconds": 45,
      "pages_success": 42,
      "pages_failed": 2,
      "total_size_kb": 2450
    },
    
    "screenshot": "https://screenshots.example.com/fado-pl-2025-01-13.png"
  }
}
```

---

*Następny dokument: 13_TOOLS_DATA_SOURCES.md*
