"""
Market Search Agent

Intelligent agent for finding companies by industry and region.
Combines KRS API, web search, and web scraping.

Use case: "Find plastic processing companies in Kujawsko-Pomorskie"
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.agent_tools import ToolRegistry, get_tool_registry

logger = logging.getLogger(__name__)


class MarketSearchAgent:
    """
    Agent for finding companies in specific regions and industries.

    Capabilities:
    - Search web for companies by industry/region
    - Enrich results with KRS data
    - Scrape company websites
    - Filter and rank results
    """

    def __init__(self):
        self.tool_registry = get_tool_registry()

    async def search(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute market search based on natural language query.

        Args:
            query: Natural language query
                    e.g., "Find plastic companies in Kujawsko-Pomorskie"
            context: Additional context (filters, preferences, etc.)

        Returns:
            Search results with company data
        """
        start_time = datetime.utcnow()

        logger.info(f"MarketSearchAgent: Processing query: '{query}'")

        # Parse query to extract parameters
        params = self._parse_query(query, context)

        logger.info(f"MarketSearchAgent: Parsed parameters: {params}")

        # Execute search using tools
        result = await self.tool_registry.find_companies(
            industry=params['industry'],
            region=params.get('region'),
            limit=params.get('limit', 20),
            scrape_top_n=params.get('scrape_top_n', 5)
        )

        # Post-process and rank results
        ranked_results = self._rank_results(result['companies'], params)

        execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return {
            'query': query,
            'parameters': params,
            'companies': ranked_results,
            'total_found': len(ranked_results),
            'enriched': result['enriched'],
            'usage_stats': result.get('usage_stats'),
            'execution_time_ms': execution_time_ms,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'agent_type': 'market_search'
        }

    def _parse_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse natural language query to extract parameters.

        Extracts:
        - Industry (e.g., "plastic processing", "IT", "manufacturing")
        - Region (e.g., "Kujawsko-Pomorskie", "Warsaw")
        - Filters (e.g., company size, specific locations)

        Args:
            query: Natural language query
            context: Additional context

        Returns:
            Parsed parameters dict
        """
        params = {
            'industry': None,
            'region': None,
            'limit': 20,
            'scrape_top_n': 5,
            'filters': {}
        }

        query_lower = query.lower()

        # Extract industry
        industry_keywords = self._get_industry_keywords()
        for industry, keywords in industry_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                params['industry'] = industry
                break

        # Fallback: extract any industry-like terms
        if not params['industry']:
            # Look for common patterns
            if 'tworzyw' in query_lower or 'plastik' in query_lower:
                params['industry'] = 'przetwórstwo tworzyw sztucznych'
            elif 'it' in query_lower or 'software' in query_lower or 'oprogramowani' in query_lower:
                params['industry'] = 'informacja technologiczna'
            elif 'motoryzacja' in query_lower or 'samochod' in query_lower:
                params['industry'] = 'motoryzacja'
            elif 'budowlan' in query_lower or 'budownict' in query_lower:
                params['industry'] = 'budownictwo'

        # Extract region
        voivodeships = self._get_voivodeships()
        for voivodeship, variants in voivodeships.items():
            if any(variant in query_lower for variant in variants):
                params['region'] = voivodeship
                break

        # Check for cities
        cities = self._get_major_cities()
        for city, variants in cities.items():
            if any(variant in query_lower for variant in variants):
                # City is not in voivodeship, use it directly
                if not params['region']:
                    params['region'] = city
                break

        # Extract limits
        limit_match = re.search(r'(\d+)\s*(firm|compan|firmy|podmiot)', query_lower)
        if limit_match:
            params['limit'] = min(int(limit_match.group(1)), 100)

        # Override with context if provided
        if context:
            if 'region' in context:
                params['region'] = context['region']
            if 'industry' in context:
                params['industry'] = context['industry']
            if 'limit' in context:
                params['limit'] = context['limit']
            if 'filters' in context:
                params['filters'].update(context['filters'])

        return params

    def _get_industry_keywords(self) -> Dict[str, List[str]]:
        """Get industry keyword mappings."""
        return {
            'przetwórstwo tworzyw sztucznych': [
                'tworzyw', 'plastik', 'poliuretan', 'polimer', 'tworzywa sztuczne',
                'plastic', 'polymers', 'processing'
            ],
            'motoryzacja i napęd': [
                'motoryzacja', 'samochod', ' Automotive', 'silnik', 'części',
                'parts', 'vehicle'
            ],
            'informacja technologiczna': [
                'it', 'software', 'oprogramowani', 'komputer', 'technologia',
                'technology'
            ],
            'budownictwo': [
                'budowlan', 'budownict', 'construction', 'wykończeni', 'architekt'
            ],
            'produkcja mebli': [
                'mebl', 'furniture', 'meblarsk', 'stolar'
            ],
            'rolnictwo': [
                'roln', 'rolnic', 'agriculture', 'żywności', 'food'
            ],
            'handel': [
                'handl', 'detaliczn', 'hurt', 'sklep', 'trade', 'retail', 'wholesale'
            ],
            'transport i logistyka': [
                'transport', 'logistyka', 'logistics', 'przewóz', 'spedycj',
                'shipping', 'dostawa'
            ]
        }

    def _get_voivodeships(self) -> Dict[str, List[str]]:
        """Get Polish voivodeships with search variants."""
        return {
            'kujawsko-pomorskie': ['kujawsko-pomorskie', 'kujawsko pomorskie', 'bydgoszcz', 'toruń'],
            'dolnośląskie': ['dolnośląskie', 'dolnośląsk', 'wrocław'],
            'śląskie': ['śląskie', 'śląsk', 'katowice'],
            'mazowieckie': ['mazowieckie', 'mazowieck', 'warszawa'],
            'wielkopolskie': ['wielkopolskie', 'wielkopolsk', 'poznań'],
            'małopolskie': ['małopolskie', 'małopolsk', 'kraków'],
            'łódzkie': ['łódzkie', 'łódz'],
            'pomorskie': ['pomorskie', 'pomorze', 'gdańsk'],
            'lubelskie': ['lubelskie', 'lubel'],
            'podkarpackie': ['podkarpackie', 'podkarpacie'],
            'podlaskie': ['podlaskie', 'podlas'],
            'świętokrzyskie': ['świętokrzyskie', 'świętokrzys'],
            'lubuskie': ['lubuskie', 'lubusz'],
            'opolskie': ['opolskie', 'opolsk'],
            'zachodniopomorskie': ['zachodniopomorskie', 'zachodniopomor']
        }

    def _get_major_cities(self) -> Dict[str, List[str]]:
        """Get major cities with search variants."""
        return {
            'bydgoszcz': ['bydgoszcz'],
            'toruń': ['toruń'],
            'warszawa': ['warszawa', 'warsaw'],
            'kraków': ['kraków', 'krakow'],
            'wrocław': ['wrocław', 'wroclaw'],
            'poznań': ['poznań', 'poznán'],
            'łódź': ['łódź', 'lodz'],
            'gdańsk': ['gdańsk', 'gdansk'],
            'szczecin': ['szczecin', 'szczecin'],
            'lublin': ['lublin'],
            'katowice': ['katowice'],
            'białystok': ['białystok'],
            'gdynia': ['gdynia'],
            'sopot': ['sopot']
        }

    def _rank_results(
        self,
        companies: List[Dict[str, Any]],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank and sort results by relevance.

        Ranking factors:
        - Has KRS data (high quality)
        - Has website data
        - Name matches industry keywords
        - In target region

        Args:
            companies: List of company data
            params: Search parameters

        Returns:
            Ranked and sorted companies
        """
        scored_companies = []

        for company in companies:
            score = 0
            reasons = []

            # Score: Has KRS data (+50)
            if company.get('krs_data'):
                score += 50
                reasons.append('KRS data')

            # Score: Has website data (+30)
            if company.get('web_data'):
                score += 30
                reasons.append('Website scraped')

            # Score: Region match (+20)
            if params.get('region'):
                company_text = (
                    company.get('name', '') + ' ' +
                    company.get('snippet', '') + ' ' +
                    str(company.get('address', ''))
                ).lower()

                # Check if region appears in company data
                region_variants = self.tool_registry._get_region_search_terms(params['region'])
                if any(variant.lower() in company_text for variant in region_variants):
                    score += 20
                    reasons.append('Region match')

            # Score: Industry keyword in name/snippet (+10)
            if params.get('industry'):
                industry_lower = params['industry'].lower()
                company_text = (
                    company.get('name', '') + ' ' +
                    company.get('snippet', '') + ' ' +
                    company.get('web_data', {}).get('content', '')[:500]
                ).lower()

                # Extract key terms from industry
                industry_terms = industry_lower.split()[:3]  # First 3 terms
                if any(term in company_text for term in industry_terms):
                    score += 10
                    reasons.append('Industry match')

            company['relevance_score'] = score
            company['relevance_reasons'] = reasons

            scored_companies.append(company)

        # Sort by score descending
        scored_companies.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        logger.info(f"MarketSearchAgent: Ranked {len(scored_companies)} companies")

        return scored_companies


async def execute_market_search(
    query: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute market search agent (convenience function).

    Args:
        query: Natural language query
        context: Additional context

    Returns:
        Search results
    """
    agent = MarketSearchAgent()
    return await agent.search(query, context)
