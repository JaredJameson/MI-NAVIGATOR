"""
Query Router Service

Classifies user queries and routes them to appropriate analysis agents.
Uses keyword matching and pattern recognition to determine query intent.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class QueryRoute(str, Enum):
    """Available query routes"""
    COMPANY_PROFILE = "company_profile"
    FINANCIAL_ANALYSIS = "financial_analysis"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    OWNERSHIP_MAPPING = "ownership_mapping"
    DIGITAL_PRESENCE = "digital_presence"
    NEWS_SENTIMENT = "news_sentiment"
    SWOT_ANALYSIS = "swot_analysis"
    PORTER_ANALYSIS = "porter_analysis"
    PESTLE_ANALYSIS = "pestle_analysis"
    BCG_ANALYSIS = "bcg_analysis"
    WEBSITE_ANALYSIS = "website_analysis"
    GENERAL_INQUIRY = "general_inquiry"


class QueryRouterService:
    """
    Routes user queries to appropriate analysis agents based on intent classification.

    Uses multi-stage classification:
    1. Keyword matching for explicit intents
    2. Pattern matching for structured queries
    3. Context analysis for ambiguous queries
    """

    # Keywords for each route (PL + EN)
    ROUTE_KEYWORDS = {
        QueryRoute.COMPANY_PROFILE: [
            # Polish
            "profil", "firma", "informacje o firmie", "dane firmy", "krs", "nip", "regon",
            "adres firmy", "zarząd", "wspólnicy", "struktura", "podstawowe dane",
            # English
            "company profile", "company info", "company data", "basic information",
            "company details", "organization", "business entity", "registry",
        ],
        QueryRoute.FINANCIAL_ANALYSIS: [
            # Polish
            "finanse", "analiza finansowa", "sprawozdanie", "bilans", "zyski", "straty",
            "przychody", "rentowność", "zadłużenie", "płynność", "wskaźniki finansowe",
            "wyniki finansowe", "rachunkowość", "kapitał", "aktywa", "pasywa",
            # English
            "financial", "finances", "financial analysis", "financial statement", "balance sheet",
            "profit", "loss", "revenue", "profitability", "debt", "liquidity", "financial ratios",
            "financial results", "accounting", "capital", "assets", "liabilities",
        ],
        QueryRoute.MARKET_ANALYSIS: [
            # Polish
            "rynek", "analiza rynku", "wielkość rynku", "tam sam som", "segmenty rynku",
            "trendy rynkowe", "wzrost rynku", "potencjał rynku", "sektor", "branża",
            "makroekonomia", "prognozy", "prognoza rynku",
            # English
            "market", "market analysis", "market size", "tam sam som", "market segments",
            "market trends", "market growth", "market potential", "sector", "industry",
            "macroeconomics", "forecast", "market forecast",
        ],
        QueryRoute.COMPETITIVE_ANALYSIS: [
            # Polish
            "konkurencja", "konkurenci", "analiza konkurencji", "porównanie", "benchmark",
            "pozycja konkurencyjna", "udział w rynku", "landscape konkurencyjny",
            "główni gracze", "alternatywy", "konkurencyjność",
            # English
            "competition", "competitors", "competitive analysis", "comparison", "benchmark",
            "competitive position", "market share", "competitive landscape",
            "key players", "alternatives", "competitiveness",
        ],
        QueryRoute.OWNERSHIP_MAPPING: [
            # Polish
            "właściciele", "udziałowcy", "akcjonariusze", "struktura właścicielska",
            "beneficjenci rzeczywiści", "powiązania kapitałowe", "spółki zależne",
            "udziały", "pakiet kontrolny",
            # English
            "owners", "shareholders", "stakeholders", "ownership structure",
            "beneficial owners", "capital connections", "subsidiaries",
            "shares", "controlling stake",
        ],
        QueryRoute.DIGITAL_PRESENCE: [
            # Polish
            "strona www", "online", "obecność cyfrowa", "social media", "media społecznościowe",
            "linkedin", "facebook", "instagram", "marketing online", "seo",
            # English
            "website", "online", "digital presence", "social media",
            "linkedin", "facebook", "instagram", "online marketing", "seo",
        ],
        QueryRoute.NEWS_SENTIMENT: [
            # Polish
            "wiadomości", "aktualności", "news", "sentiment", "opinie", "prasa",
            "media", "publikacje", "wydarzenia", "incident",
            # English
            "news", "updates", "sentiment", "opinions", "press",
            "media", "publications", "events", "incident",
        ],
        QueryRoute.SWOT_ANALYSIS: [
            # Polish
            "swot", "mocne strony", "słabe strony", "szanse", "zagrożenia",
            "strengths", "weaknesses", "opportunities", "threats",
            # English (same as Polish for SWOT)
        ],
        QueryRoute.PORTER_ANALYSIS: [
            # Polish
            "porter", "5 sił portera", "pięć sił", "siły konkurencji", "atrakcyjność branży",
            # English
            "porter", "five forces", "porter's five forces", "competitive forces",
            "industry attractiveness",
        ],
        QueryRoute.PESTLE_ANALYSIS: [
            # Polish
            "pestle", "pestel", "pest", "analiza otoczenia", "makrootoczenie",
            "polityka", "ekonomia", "społeczeństwo", "technologia", "prawo", "środowisko",
            # English
            "pestle", "pestel", "pest", "environmental analysis", "macro environment",
            "political", "economic", "social", "technological", "legal", "environmental",
        ],
        QueryRoute.BCG_ANALYSIS: [
            # Polish
            "bcg", "macierz bcg", "gwiazdy", "dojne krowy", "znaki zapytania", "psy",
            "portfolio", "analiza portfolio",
            # English
            "bcg", "bcg matrix", "stars", "cash cows", "question marks", "dogs",
            "portfolio", "portfolio analysis",
        ],
        QueryRoute.WEBSITE_ANALYSIS: [
            # Polish
            "analiza strony", "audyt strony", "strona internetowa", "website",
            "technologia", "stack technologiczny", "cms", "performance",
            # English
            "website analysis", "site audit", "web analysis", "technology stack",
            "tech stack", "cms", "performance",
        ],
    }

    # Patterns for structured queries
    QUERY_PATTERNS = [
        # Company profile patterns
        (r"(jaka jest|co to za|informacje o|dane o)\s+firma", QueryRoute.COMPANY_PROFILE),
        (r"(profil|profile)\s+(firmy|company)", QueryRoute.COMPANY_PROFILE),

        # Financial patterns
        (r"(jak.*finans|sytuacja finansowa|kondycja finansowa)", QueryRoute.FINANCIAL_ANALYSIS),
        (r"(ile zarabia|przychody|obroty|zyski)", QueryRoute.FINANCIAL_ANALYSIS),

        # Market patterns
        (r"(jak duży|wielkość|rozmiar)\s+(rynek|rynku)", QueryRoute.MARKET_ANALYSIS),
        (r"(market size|tam|sam|som)", QueryRoute.MARKET_ANALYSIS),

        # Competitive patterns
        (r"(kim są|who are|lista)\s+(konkurent|competitor)", QueryRoute.COMPETITIVE_ANALYSIS),
        (r"(porównaj|compare|benchmark)", QueryRoute.COMPETITIVE_ANALYSIS),

        # Framework patterns
        (r"\bswot\b", QueryRoute.SWOT_ANALYSIS),
        (r"\bporter\b", QueryRoute.PORTER_ANALYSIS),
        (r"\bpestle\b", QueryRoute.PESTLE_ANALYSIS),
        (r"\bbcg\b", QueryRoute.BCG_ANALYSIS),
    ]

    def classify_query(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Tuple[QueryRoute, float, List[Tuple[QueryRoute, float]]]:
        """
        Classify a user query and return the most likely route with confidence.

        Args:
            query: User's query text
            context: Optional context (previous queries, user preferences, etc.)

        Returns:
            Tuple of (primary_route, confidence, alternative_routes)
            where alternative_routes is a list of (route, confidence) tuples
        """
        query_lower = query.lower()

        # Stage 1: Pattern matching (highest confidence)
        for pattern, route in self.QUERY_PATTERNS:
            if re.search(pattern, query_lower):
                return route, 0.95, self._get_alternative_routes(query_lower, exclude=route)

        # Stage 2: Keyword matching (medium-high confidence)
        route_scores = {}

        for route, keywords in self.ROUTE_KEYWORDS.items():
            score = 0.0
            matched_keywords = []

            for keyword in keywords:
                if keyword.lower() in query_lower:
                    # Higher score for longer, more specific keywords
                    keyword_weight = len(keyword.split()) * 0.1 + 0.1
                    score += keyword_weight
                    matched_keywords.append(keyword)

            if score > 0:
                # Normalize score to 0-1 range (0.6-0.9 for keyword matches)
                # Cap at 0.9 to reserve 0.95+ for pattern matches
                normalized_score = min(0.6 + (score * 0.3), 0.9)
                route_scores[route] = (normalized_score, matched_keywords)

        if route_scores:
            # Sort by score descending
            sorted_routes = sorted(
                route_scores.items(),
                key=lambda x: x[1][0],
                reverse=True
            )

            primary_route = sorted_routes[0][0]
            primary_confidence = sorted_routes[0][1][0]

            # Get alternative routes (confidence > 0.5)
            alternatives = [
                (route, score)
                for route, (score, _) in sorted_routes[1:]
                if score > 0.5
            ]

            return primary_route, primary_confidence, alternatives

        # Stage 3: Context-based routing (if context provided)
        if context:
            # Use context to infer intent
            # For example: if previous query was about a company, likely continuing that thread
            if "last_route" in context:
                return context["last_route"], 0.4, []

        # Default: General inquiry (low confidence)
        return QueryRoute.GENERAL_INQUIRY, 0.3, []

    def _get_alternative_routes(
        self,
        query_lower: str,
        exclude: Optional[QueryRoute] = None
    ) -> List[Tuple[QueryRoute, float]]:
        """
        Get alternative routes for a query, excluding the primary route.

        Args:
            query_lower: Lowercase query text
            exclude: Route to exclude from alternatives

        Returns:
            List of (route, confidence) tuples
        """
        alternatives = []

        for route, keywords in self.ROUTE_KEYWORDS.items():
            if route == exclude:
                continue

            score = 0.0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 0.1

            if score > 0:
                # Lower confidence for alternatives
                confidence = min(score * 0.5, 0.7)
                alternatives.append((route, confidence))

        # Sort by confidence descending, limit to top 3
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return alternatives[:3]

    def get_route_description(self, route: QueryRoute, language: str = "pl") -> str:
        """
        Get a human-readable description of a route.

        Args:
            route: The query route
            language: Language code ("pl" or "en")

        Returns:
            Description string
        """
        descriptions = {
            "pl": {
                QueryRoute.COMPANY_PROFILE: "Analiza profilu firmy - podstawowe dane, zarząd, struktura",
                QueryRoute.FINANCIAL_ANALYSIS: "Analiza finansowa - bilans, wyniki, wskaźniki",
                QueryRoute.MARKET_ANALYSIS: "Analiza rynku - wielkość, trendy, prognozy",
                QueryRoute.COMPETITIVE_ANALYSIS: "Analiza konkurencji - konkurenci, pozycja rynkowa",
                QueryRoute.OWNERSHIP_MAPPING: "Mapowanie właścicieli - udziałowcy, powiązania",
                QueryRoute.DIGITAL_PRESENCE: "Obecność cyfrowa - strona www, social media",
                QueryRoute.NEWS_SENTIMENT: "Wiadomości i sentiment - aktualności, opinie",
                QueryRoute.SWOT_ANALYSIS: "Analiza SWOT - mocne/słabe strony, szanse/zagrożenia",
                QueryRoute.PORTER_ANALYSIS: "Analiza 5 Sił Portera - atrakcyjność branży",
                QueryRoute.PESTLE_ANALYSIS: "Analiza PESTLE - otoczenie makroekonomiczne",
                QueryRoute.BCG_ANALYSIS: "Macierz BCG - analiza portfolio produktów",
                QueryRoute.WEBSITE_ANALYSIS: "Analiza strony www - technologia, performance",
                QueryRoute.GENERAL_INQUIRY: "Zapytanie ogólne - wymaga doprecyzowania",
            },
            "en": {
                QueryRoute.COMPANY_PROFILE: "Company Profile - basic data, management, structure",
                QueryRoute.FINANCIAL_ANALYSIS: "Financial Analysis - balance sheet, results, ratios",
                QueryRoute.MARKET_ANALYSIS: "Market Analysis - size, trends, forecasts",
                QueryRoute.COMPETITIVE_ANALYSIS: "Competitive Analysis - competitors, market position",
                QueryRoute.OWNERSHIP_MAPPING: "Ownership Mapping - shareholders, connections",
                QueryRoute.DIGITAL_PRESENCE: "Digital Presence - website, social media",
                QueryRoute.NEWS_SENTIMENT: "News & Sentiment - updates, opinions",
                QueryRoute.SWOT_ANALYSIS: "SWOT Analysis - strengths/weaknesses, opportunities/threats",
                QueryRoute.PORTER_ANALYSIS: "Porter's Five Forces - industry attractiveness",
                QueryRoute.PESTLE_ANALYSIS: "PESTLE Analysis - macro environment",
                QueryRoute.BCG_ANALYSIS: "BCG Matrix - product portfolio analysis",
                QueryRoute.WEBSITE_ANALYSIS: "Website Analysis - technology, performance",
                QueryRoute.GENERAL_INQUIRY: "General Inquiry - needs clarification",
            }
        }

        return descriptions.get(language, descriptions["en"]).get(
            route,
            "Unknown route"
        )


# Singleton instance
query_router_service = QueryRouterService()
