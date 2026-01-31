"""
Company Profile Agent

Autonomous agent for comprehensive company profile analysis.
Integrates KRS, NIP, GUS, and REGON APIs for Polish company data.

Week 1-3 Implementation: Foundation agent for the MI-Navigator system.

Use case: "Get profile for company with KRS 0000123456"
         "Analyze ownership structure of company with NIP 1234567890"
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.services.agent_tools import ToolRegistry, get_tool_registry

# Week 22: Import PromptLoader for MD prompt integration
try:
    from app.services.prompt_loader import prompt_loader
    PROMPTS_AVAILABLE = True
except ImportError:
    PROMPTS_AVAILABLE = False
    logger.warning("PromptLoader not available, using fallback behavior")

# Week 22: Import ClaudeService for LLM-enhanced analysis
try:
    from app.services.claude_service import ClaudeService
    CLAUDE_SERVICE_AVAILABLE = True
except ImportError:
    CLAUDE_SERVICE_AVAILABLE = False
    logger.warning("ClaudeService not available, using basic analysis only")

# Week 2: Import GUS and REGON clients
try:
    from app.integrations.gus_client import GUSClient
    from app.integrations.regon_client import REGONClient
    GUS_AVAILABLE = True
    REGON_AVAILABLE = True
except ImportError:
    GUS_AVAILABLE = False
    REGON_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

class Address(BaseModel):
    """Company address structure"""
    street: Optional[str] = None
    city: Optional[str] = None
    voivodeship: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Poland"


class Owner(BaseModel):
    """Ownership structure entry"""
    owner_name: str
    ownership_percentage: float = Field(..., ge=0, le=100)
    ownership_type: str = Field(..., pattern="^(direct|indirect)$")


class BoardMember(BaseModel):
    """Management board member"""
    name: str
    position: str
    appointment_date: Optional[str] = None


class FinancialStatements(BaseModel):
    """Financial statements data"""
    year: int
    revenue: Optional[float] = None
    profit: Optional[float] = None
    assets: Optional[float] = None
    liabilities: Optional[float] = None
    equity: Optional[float] = None


class CompanyProfileOutput(BaseModel):
    """Structured output for CompanyProfileAgent"""
    agent_type: str = "company_profile"
    target: str = Field(..., description="Target identifier (KRS, NIP, company name)")

    # Core company data
    company_name: Optional[str] = None
    krs_number: Optional[str] = None
    nip_number: Optional[str] = None
    regon_number: Optional[str] = None
    legal_form: Optional[str] = None
    industry: Optional[str] = None
    registration_date: Optional[str] = None

    # Structured data
    address: Optional[Address] = None
    ownership_structure: List[Owner] = Field(default_factory=list)
    management_board: List[BoardMember] = Field(default_factory=list)
    financial_statements: Optional[FinancialStatements] = None

    # Agent metadata
    confidence_score: float = Field(..., ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "company_profile",
                "target": "KRS 0000123456",
                "company_name": "Example Sp. z o.o.",
                "krs_number": "0000123456",
                "nip_number": "1234567890",
                "confidence_score": 85.5,
                "data_sources": ["KRS API", "GUS API"],
                "last_updated": "2026-01-24T10:00:00Z"
            }
        }


# ============================================================================
# DOMAIN KNOWLEDGE
# ============================================================================

class CompanyProfileDomainKnowledge:
    """
    Domain knowledge for Polish company data.
    Based on KRS, NIP, GUS, REGON standards.
    """

    # Polish legal forms (from KRS)
    LEGAL_FORMS = [
        "Spółka z ograniczoną odpowiedzialnością",  # Sp. z o.o.
        "Spółka akcyjna",  # S.A.
        "Spółka komandytowa",  # S.K.
        "Spółka komandytowo-akcyjna",  # S.K.A.
        "Spółka jawna",  # S.J.
        "Spółka partnerska",  # S.P.
        "Przedsiębiorca zagraniczny",
        "Fundacja",
        "Stowarzyszenie"
    ]

    # Polish voivodeships (administrative regions)
    VOIVODESHIPS = [
        "Mazowieckie", "Śląskie", "Wielkopolskie", "Małopolskie",
        "Dolnośląskie", "Łódzkie", "Pomorskie", "Kujawsko-Pomorskie",
        "Zachodniopomorskie", "Lubelskie", "Podkarpackie", "Warmińsko-Mazurskie",
        "Podlaskie", "Świętokrzyskie", "Lubuskie", "Opolskie"
    ]

    # PKD codes - Polish Classification of Activities (sample)
    PKD_INDUSTRIES = {
        "01": "Rolnictwo, leśnictwo, łowiectwo i rybactwo",
        "10": "Produkcja artykułów spożywczych",
        "46": "Handel hurtowy",
        "47": "Handel detaliczny",
        "62": "Działalność związana z oprogramowaniem",
        "68": "Działalność związana z obsługą rynku nieruchomości",
        "70": "Działalność firm centralnych (head offices)"
    }

    # NIP checksum weights (for validation)
    NIP_WEIGHTS = [6, 5, 7, 2, 3, 4, 5, 6, 7]


# ============================================================================
# COMPANY PROFILE AGENT
# ============================================================================

class CompanyProfileAgent:
    """
    Autonomous agent for comprehensive company profile analysis.

    Capabilities:
    - KRS API integration (company registry data)
    - NIP validation and verification
    - GUS statistical data integration
    - REGON database queries
    - Ownership structure parsing
    - Management board extraction
    - Financial statements analysis
    - Confidence scoring algorithm

    Confidence Scoring Algorithm:
        score = 0
        if krs_data: score += 50
        if nip_valid: score += 30
        if gus_data: score += 20
        if ownership_structure: score += 10
        if financial_statements: score += 15
        # Max: 125, normalized to 0-100
    """

    def __init__(self):
        """Initialize CompanyProfileAgent with tool registry, system prompt, and LLM service."""
        self.agent_type = "company_profile"
        self.tool_registry = get_tool_registry()
        self.domain_knowledge = CompanyProfileDomainKnowledge()

        # Week 22: Load system prompt from MD files
        self.system_prompt = None
        if PROMPTS_AVAILABLE:
            try:
                self.system_prompt = prompt_loader.load_prompt("company_profile")
                if self.system_prompt:
                    logger.info(f"✅ {self.agent_type} agent initialized with MD prompt ({len(self.system_prompt)} chars)")
                else:
                    logger.warning(f"⚠️ {self.agent_type} agent: MD prompt empty, using fallback behavior")
            except Exception as e:
                logger.error(f"❌ Error loading prompt for {self.agent_type}: {e}")
                logger.info(f"{self.agent_type} agent initialized with fallback behavior")
        else:
            logger.info(f"{self.agent_type} agent initialized without prompts (PromptLoader not available)")

        # Week 22: Initialize ClaudeService for LLM-enhanced analysis
        self.claude_service = None
        if CLAUDE_SERVICE_AVAILABLE:
            try:
                self.claude_service = ClaudeService()
                logger.info(f"✅ {self.agent_type} agent: ClaudeService initialized for intelligent analysis")
            except Exception as e:
                logger.error(f"❌ Error initializing ClaudeService for {self.agent_type}: {e}")
                logger.info(f"{self.agent_type} agent: Using basic analysis without LLM enhancement")
        else:
            logger.info(f"{self.agent_type} agent: ClaudeService not available, using basic analysis")


    def get_prompt_instructions(self) -> Optional[str]:
        """
        Get system prompt instructions for this agent.

        Week 22: Added for MD prompt integration.
        Future use: Can be passed to LLM calls for enhanced agent behavior.

        Returns:
            System prompt string or None if not available
        """
        return self.system_prompt

    def get_prompt_guidelines(self, task_type: str = "general") -> str:
        """
        Get prompt-based guidelines for specific task types.

        Week 22: Helper method to extract relevant guidelines from system prompt.
        Useful for LLM-based enhancements in future iterations.

        Args:
            task_type: Type of task (general, krs, nip, company_name)

        Returns:
            Relevant guidelines or fallback instructions
        """
        if not self.system_prompt:
            return "Use available tools and domain knowledge to analyze company profile."

        # Return full prompt for now, can be enhanced to extract specific sections
        return self.system_prompt

    async def execute(
        self,
        target: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CompanyProfileOutput:
        """
        Execute company profile analysis.

        Args:
            target: Company identifier (KRS number, NIP, or company name)
                   Examples: "KRS 0000123456", "NIP 1234567890", "Company Name Sp. z o.o."
            context: Optional context with additional parameters

        Returns:
            CompanyProfileOutput: Structured company profile with confidence score

        Example:
            agent = CompanyProfileAgent()
            result = await agent.execute(target="KRS 0000123456")
        """
        start_time = datetime.utcnow()
        logger.info(f"CompanyProfileAgent: Executing for target: '{target}'")

        errors = []
        warnings = []
        data_sources = []

        try:
            # Step 1: Input Validation & Target Type Detection
            target_info = self._parse_target(target)

            if not target_info['valid']:
                errors.append(f"Invalid target: {target}")
                return self._build_output(
                    target=target,
                    data={},
                    confidence_score=0,
                    data_sources=data_sources,
                    errors=errors,
                    warnings=warnings
                )

            logger.info(f"CompanyProfileAgent: Target type: {target_info['type']}")

            # Step 2: Data Collection from multiple sources
            collected_data = await self._collect_data(target_info, context)

            if collected_data.get("errors"):
                errors.extend(collected_data["errors"])
            if collected_data.get("warnings"):
                warnings.extend(collected_data["warnings"])
            if collected_data.get("data_sources"):
                data_sources.extend(collected_data["data_sources"])

            # Step 3: Data Processing & Aggregation
            processed_data = self._process_data(collected_data.get("data", {}), target_info)

            # Step 3.5: LLM-Enhanced Analysis (Week 22)
            enhanced_data = await self._enhance_with_llm(
                processed_data=processed_data,
                target_info=target_info,
                context=context
            )

            # Step 4: Confidence Scoring (enhanced with LLM quality assessment)
            confidence_score = self._calculate_confidence(
                processed_data=enhanced_data,
                data_sources=data_sources,
                target_info=target_info
            )

            # Step 5: Build Structured Output
            result = self._build_output(
                target=target,
                data=enhanced_data,
                confidence_score=confidence_score,
                data_sources=data_sources,
                errors=errors,
                warnings=warnings
            )

            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.info(
                f"CompanyProfileAgent: Completed in {execution_time_ms}ms "
                f"(confidence: {confidence_score:.1f}%)"
            )

            return result

        except Exception as e:
            logger.error(f"CompanyProfileAgent: Execution error: {str(e)}", exc_info=True)
            errors.append(f"Execution error: {str(e)}")
            return self._build_output(
                target=target,
                data={},
                confidence_score=0,
                data_sources=data_sources,
                errors=errors,
                warnings=warnings
            )


    def _parse_target(self, target: str) -> Dict[str, Any]:
        """
        Parse target identifier and determine type.

        Target types:
        - KRS number: "KRS 0000123456" or "0000123456"
        - NIP number: "NIP 1234567890" or "1234567890"
        - Company name: "Company Name Sp. z o.o."

        Parsing priority:
        1. Check for explicit "NIP" keyword first (to avoid KRS regex matching NIP)
        2. Check for explicit "KRS" keyword
        3. Try NIP validation if 10 digits (has checksum)
        4. Fall back to KRS if 10 digits but not valid NIP
        5. Assume company name for other inputs

        Args:
            target: Target identifier string

        Returns:
            Dict with target info: {type, value, valid, validation_errors}
        """
        target_clean = target.strip()

        result = {
            'type': 'unknown',
            'value': target_clean,
            'valid': False,
            'validation_errors': []
        }

        # Priority 1: Explicit "NIP" keyword
        if re.search(r'\bNIP\b', target_clean, re.IGNORECASE):
            nip_match = re.search(r'(?:NIP\s*)?(\d{10})', target_clean, re.IGNORECASE)
            if nip_match:
                nip_number = nip_match.group(1)
                is_valid, error = self._validate_nip(nip_number)
                result['type'] = 'nip'
                result['value'] = nip_number
                result['valid'] = is_valid
                result['nip_number'] = nip_number
                if not is_valid:
                    result['validation_errors'].append(error)
                return result

        # Priority 2: Explicit "KRS" keyword
        if re.search(r'\bKRS\b', target_clean, re.IGNORECASE):
            krs_match = re.search(r'(?:KRS\s*)?(\d{10})', target_clean, re.IGNORECASE)
            if krs_match:
                krs_number = krs_match.group(1)
                result['type'] = 'krs'
                result['value'] = krs_number
                result['valid'] = True
                result['krs_number'] = krs_number
                return result

        # Priority 3: 10 digits → try NIP validation first
        digit_match = re.search(r'(\d{10})', target_clean)
        if digit_match:
            number = digit_match.group(1)

            # Try NIP validation (has checksum)
            is_valid_nip, nip_error = self._validate_nip(number)
            if is_valid_nip:
                result['type'] = 'nip'
                result['value'] = number
                result['valid'] = True
                result['nip_number'] = number
                return result

            # Fall back to KRS (no checksum, all 10-digit numbers are valid)
            result['type'] = 'krs'
            result['value'] = number
            result['valid'] = True
            result['krs_number'] = number
            return result

        # Priority 4: Company name
        if len(target_clean) >= 3:  # Minimum 3 characters for company name
            result['type'] = 'company_name'
            result['value'] = target_clean
            result['valid'] = True
            result['company_name'] = target_clean
            return result

        result['validation_errors'].append("Target too short or invalid format")
        return result


    def _validate_nip(self, nip: str) -> tuple[bool, Optional[str]]:
        """
        Validate NIP (Polish Tax Identification Number).

        NIP format: 10 digits with checksum validation
        Algorithm: weighted sum modulo 11

        Args:
            nip: 10-digit NIP number

        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])

        Example:
            _validate_nip("1234563218") -> (True, None)
            _validate_nip("1234567890") -> (False, "Invalid NIP checksum")
        """
        if not nip or len(nip) != 10:
            return False, "NIP must be 10 digits"

        if not nip.isdigit():
            return False, "NIP must contain only digits"

        # Calculate checksum
        weights = self.domain_knowledge.NIP_WEIGHTS
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11

        if checksum == 10:
            return False, "Invalid NIP (checksum = 10)"

        if checksum != int(nip[9]):
            return False, f"Invalid NIP checksum (expected {checksum}, got {nip[9]})"

        return True, None


    async def _collect_data(
        self,
        target_info: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Collect data from multiple sources (KRS, GUS, REGON).

        Data collection strategy:
        1. If KRS number → fetch KRS data directly
        2. If NIP number → fetch GUS data, then KRS if available
        3. If company name → search KRS, then fetch details

        Args:
            target_info: Parsed target information
            context: Additional context

        Returns:
            Dict with: {data, data_sources, errors, warnings}
        """
        data = {}
        data_sources = []
        errors = []
        warnings = []

        target_type = target_info['type']

        try:
            # Strategy 1: KRS number → direct KRS fetch
            if target_type == 'krs':
                krs_number = target_info['krs_number']
                krs_data = await self._fetch_krs_data(krs_number)

                if krs_data:
                    data['krs'] = krs_data
                    data_sources.append("KRS API")
                else:
                    errors.append(f"KRS data not found for: {krs_number}")

            # Strategy 2: NIP number → GUS fetch, then KRS lookup
            elif target_type == 'nip':
                nip_number = target_info['nip_number']

                # Fetch GUS data
                gus_data = await self._fetch_gus_data(nip_number)
                if gus_data:
                    data['gus'] = gus_data
                    data_sources.append("GUS API")

                    # Try to get KRS from GUS data
                    if 'krs_number' in gus_data:
                        krs_data = await self._fetch_krs_data(gus_data['krs_number'])
                        if krs_data:
                            data['krs'] = krs_data
                            data_sources.append("KRS API")
                else:
                    warnings.append(f"GUS data not found for NIP: {nip_number}")

            # Strategy 3: Company name → KRS search
            elif target_type == 'company_name':
                company_name = target_info['company_name']
                krs_search_results = await self._search_krs_by_name(company_name)

                if krs_search_results:
                    # Take first result (most relevant)
                    best_match = krs_search_results[0]
                    krs_data = await self._fetch_krs_data(best_match['krs_number'])

                    if krs_data:
                        data['krs'] = krs_data
                        data_sources.append("KRS API")
                else:
                    warnings.append(f"No KRS results found for: {company_name}")

            # REGON data (if NIP or KRS available)
            if 'krs' in data and data['krs'].get('nip_number'):
                regon_data = await self._fetch_regon_data(data['krs']['nip_number'])
                if regon_data:
                    data['regon'] = regon_data
                    data_sources.append("REGON")

        except Exception as e:
            logger.error(f"CompanyProfileAgent: Data collection error: {str(e)}", exc_info=True)
            errors.append(f"Data collection error: {str(e)}")

        return {
            "data": data,
            "data_sources": data_sources,
            "errors": errors,
            "warnings": warnings
        }


    async def _fetch_krs_data(self, krs_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from KRS API.

        Week 1 implementation: Uses tool registry KRS client.

        Args:
            krs_number: 10-digit KRS number

        Returns:
            KRS data dict or None if not found
        """
        try:
            # TODO Week 1: Implement actual KRS API integration
            # For now, return mock data structure
            logger.warning(f"KRS API not yet implemented, using mock data for: {krs_number}")

            return {
                "krs_number": krs_number,
                "company_name": f"Mock Company KRS {krs_number}",
                "nip_number": None,
                "regon_number": None,
                "legal_form": "Spółka z ograniczoną odpowiedzialnością",
                "registration_date": "2020-01-15",
                "address": {
                    "street": "ul. Testowa 123",
                    "city": "Warszawa",
                    "voivodeship": "Mazowieckie",
                    "postal_code": "00-001"
                },
                "management_board": [
                    {
                        "name": "Jan Kowalski",
                        "position": "Prezes Zarządu",
                        "appointment_date": "2020-01-15"
                    }
                ],
                "ownership_structure": []
            }
        except Exception as e:
            logger.error(f"KRS API error for {krs_number}: {str(e)}")
            return None


    async def _fetch_gus_data(self, nip_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from GUS (Central Statistical Office) API.

        Week 2 implementation: GUS statistical data integration.

        Args:
            nip_number: 10-digit NIP number

        Returns:
            GUS data dict or None if not found
        """
        try:
            if GUS_AVAILABLE:
                async with GUSClient() as gus_client:
                    data = await gus_client.get_company_data(nip=nip_number)

                    if data:
                        logger.info(f"GUS data retrieved for NIP: {nip_number}")
                        return data
                    else:
                        logger.warning(f"GUS data not found for NIP: {nip_number}")
                        return None
            else:
                logger.warning(f"GUS client not available, using mock data for: {nip_number}")

                return {
                    "nip": nip_number,
                    "regon": None,
                    "company_name": f"Mock Company (GUS) NIP {nip_number}",
                    "pkd_code": "62.01.Z",
                    "industry": "Działalność związana z oprogramowaniem",
                    "employee_count": 50,
                    "voivodeship": "Mazowieckie"
                }

        except Exception as e:
            logger.error(f"GUS API error for {nip_number}: {str(e)}")
            return None


    async def _search_krs_by_name(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search KRS database by company name.

        Args:
            company_name: Company name to search

        Returns:
            List of search results (sorted by relevance)
        """
        try:
            # TODO Week 1: Implement KRS search endpoint
            logger.warning(f"KRS search not yet implemented for: {company_name}")
            return []
        except Exception as e:
            logger.error(f"KRS search error for {company_name}: {str(e)}")
            return []


    async def _fetch_regon_data(self, nip_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from REGON database.

        Week 2 implementation: REGON integration.

        Args:
            nip_number: NIP number for REGON lookup

        Returns:
            REGON data dict or None if not found
        """
        try:
            if REGON_AVAILABLE:
                async with REGONClient() as regon_client:
                    data = await regon_client.get_entity_data(nip=nip_number)

                    if data:
                        logger.info(f"REGON data retrieved for NIP: {nip_number}")
                        return data
                    else:
                        logger.warning(f"REGON data not found for NIP: {nip_number}")
                        return None
            else:
                logger.warning(f"REGON client not available for NIP: {nip_number}")
                return None

        except Exception as e:
            logger.error(f"REGON error for {nip_number}: {str(e)}")
            return None


    def _process_data(
        self,
        raw_data: Dict[str, Any],
        target_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process and merge data from multiple sources into unified structure.

        Data merging priority:
        1. KRS data (highest quality, official registry)
        2. GUS data (statistical office, verified)
        3. REGON data (business registry)

        Week 2 Enhancement: Added ownership parsing and board extraction.

        Args:
            raw_data: Raw data from all sources {krs, gus, regon}
            target_info: Original target information

        Returns:
            Processed, unified company profile dict
        """
        processed = {}

        # Priority 1: KRS data (most authoritative)
        if 'krs' in raw_data:
            krs = raw_data['krs']
            processed.update({
                'company_name': krs.get('company_name'),
                'krs_number': krs.get('krs_number'),
                'nip_number': krs.get('nip_number'),
                'regon_number': krs.get('regon_number'),
                'legal_form': krs.get('legal_form'),
                'registration_date': krs.get('registration_date'),
                'address': krs.get('address')
            })

            # Week 2: Parse ownership structure
            raw_ownership = krs.get('ownership_structure', [])
            processed['ownership_structure'] = self._parse_ownership_structure(raw_ownership)

            # Week 2: Extract management board
            raw_board = krs.get('management_board', [])
            processed['management_board'] = self._extract_management_board(raw_board)

        # Priority 2: GUS data (fill gaps, add industry info)
        if 'gus' in raw_data:
            gus = raw_data['gus']
            if not processed.get('nip_number'):
                processed['nip_number'] = gus.get('nip')
            if not processed.get('regon_number'):
                processed['regon_number'] = gus.get('regon')
            if not processed.get('industry'):
                processed['industry'] = gus.get('industry')
            if not processed.get('company_name'):
                processed['company_name'] = gus.get('company_name')

            # Add PKD code and employee data
            processed['pkd_code'] = gus.get('pkd_code')
            processed['employee_count'] = gus.get('employee_count')

        # Priority 3: REGON data (additional details)
        if 'regon' in raw_data:
            regon = raw_data['regon']
            if not processed.get('regon_number'):
                processed['regon_number'] = regon.get('regon')
            if not processed.get('legal_form'):
                processed['legal_form'] = regon.get('legal_form')
            if not processed.get('pkd_code'):
                processed['pkd_code'] = regon.get('pkd_main')

        # Preserve target info if not found in APIs
        if not processed.get('company_name') and target_info.get('company_name'):
            processed['company_name'] = target_info['company_name']

        return processed


    async def _enhance_with_llm(
        self,
        processed_data: Dict[str, Any],
        target_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance company profile data with LLM-powered intelligent analysis.

        Week 28 implementation: Uses ClaudeService to provide profile quality insights,
        data completeness assessment, and cross-validation quality analysis.

        Args:
            processed_data: Normalized company data from APIs
            target_info: Target identification info
            context: Optional additional context

        Returns:
            Enhanced data dict with:
            - profile_insights: {data_completeness, data_accuracy, cross_validation_quality, information_reliability, recommendations}
            - llm_quality_score: Float 0.0-1.0 quality assessment
            - llm_analysis_notes: List of insights from LLM

        Example Enhancement:
            Input: {"company_name": "ABC Sp. z o.o.", "industry": "IT"}
            Output: {
                ...original data...,
                "profile_insights": {
                    "data_completeness": {"score": 85, "assessment": "Wysokiej jakości kompletne dane"},
                    "data_accuracy": {"score": 90, "analysis": "Dane zweryfikowane krzyżowo"},
                    "cross_validation_quality": "Skuteczna weryfikacja KRS-GUS-REGON",
                    "information_reliability": "Wiarygodne źródła - oficjalne rejestry",
                    "recommendations": ["Dodaj dane finansowe", "Uzupełnij strukturę zarządu"]
                },
                "llm_quality_score": 0.87,
                "llm_analysis_notes": ["Data completeness: high", "Cross-validation: successful"]
            }
        """
        # If ClaudeService not available, return data unchanged
        if not self.claude_service:
            logger.info("CompanyProfileAgent: ClaudeService not available, skipping LLM enhancement")
            return processed_data

        try:
            # Use pre-loaded system prompt
            system_prompt = self.system_prompt if self.system_prompt else (
                "You are an intelligent business analyst specializing in Polish company analysis. "
                "Analyze company data and provide structured business insights in Polish."
            )

            # Prepare data summary for LLM
            data_summary = {
                "company_name": processed_data.get("company_name", "Unknown"),
                "krs_number": processed_data.get("krs_number"),
                "nip_number": processed_data.get("nip_number"),
                "legal_form": processed_data.get("legal_form"),
                "industry": processed_data.get("industry"),
                "pkd_code": processed_data.get("pkd_code"),
                "employee_count": processed_data.get("employee_count"),
                "registration_date": processed_data.get("registration_date"),
                "has_ownership_data": len(processed_data.get("ownership_structure", [])) > 0,
                "has_management_data": len(processed_data.get("management_board", [])) > 0,
                "has_financial_data": processed_data.get("financial_statements") is not None
            }

            # Build analysis request (Week 28: profile_insights structure)
            analysis_request = (
                f"Przeanalizuj profil firmy i dostarcz ocenę jakości danych:\n\n"
                f"```json\n{json.dumps(data_summary, indent=2, ensure_ascii=False)}\n```\n\n"
                f"Wygeneruj analizę w formacie JSON:\n"
                f"{{\n"
                f"  \"profile_insights\": {{\n"
                f"    \"data_completeness\": {{\"score\": 0-100, \"assessment\": \"ocena kompletności danych firmy\"}},\n"
                f"    \"data_accuracy\": {{\"score\": 0-100, \"analysis\": \"dokładność i spójność danych z różnych źródeł\"}},\n"
                f"    \"cross_validation_quality\": \"ocena jakości weryfikacji krzyżowej między KRS-GUS-REGON\",\n"
                f"    \"information_reliability\": \"ocena wiarygodności informacji z dostępnych źródeł\",\n"
                f"    \"recommendations\": [\"lista rekomendacji wzbogacenia profilu\"]\n"
                f"  }},\n"
                f"  \"quality_score\": 0.0-1.0,\n"
                f"  \"analysis_notes\": [\"lista uwag analitycznych\"]\n"
                f"}}\n"
            )

            # Call ClaudeService
            logger.info("CompanyProfileAgent: Requesting LLM enhancement...")
            response = await self.claude_service.chat(
                message=analysis_request,
                conversation_history=[],
                system_prompt=system_prompt,
                language=context.get("language", "pl") if context else "pl",
                model=self.claude_service.default_model
            )

            # Extract and parse LLM response
            llm_content = response.get("content", "")

            # Extract JSON from markdown if present
            import re
            json_match = re.search(r'```(?:json)?\s*\n?([\s\S]+?)\n?```', llm_content)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                json_str = llm_content.strip()

            llm_analysis = json.loads(json_str)

            # Merge LLM insights into processed data (Week 28: profile_insights)
            enhanced_data = processed_data.copy()
            enhanced_data['profile_insights'] = llm_analysis.get('profile_insights', {})
            enhanced_data['llm_quality_score'] = llm_analysis.get('quality_score', 0.0)
            enhanced_data['llm_analysis_notes'] = llm_analysis.get('analysis_notes', [])

            logger.info(
                f"CompanyProfileAgent: LLM enhancement complete "
                f"(quality score: {enhanced_data.get('llm_quality_score', 0.0):.2f})"
            )

            return enhanced_data

        except json.JSONDecodeError as e:
            logger.error(f"CompanyProfileAgent: Failed to parse LLM response: {e}")
            logger.debug(f"Raw LLM response: {llm_content}")
            return processed_data

        except Exception as e:
            logger.error(f"CompanyProfileAgent: LLM enhancement error: {str(e)}", exc_info=True)
            # Return original data if LLM enhancement fails (graceful degradation)
            return processed_data


    def _parse_ownership_structure(self, raw_ownership: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse ownership structure with shareholding percentages.

        Week 2 implementation: Ownership parsing algorithms.

        Args:
            raw_ownership: Raw ownership data from KRS

        Returns:
            List of standardized ownership entries

        Example Input:
            [
                {
                    "owner": "Jan Kowalski",
                    "shares": 510,
                    "total_shares": 1000,
                    "type": "direct"
                }
            ]

        Example Output:
            [
                {
                    "owner_name": "Jan Kowalski",
                    "ownership_percentage": 51.0,
                    "ownership_type": "direct"
                }
            ]
        """
        parsed_ownership = []

        for entry in raw_ownership:
            try:
                # Calculate percentage if shares provided
                if 'shares' in entry and 'total_shares' in entry:
                    total = entry['total_shares']
                    if total > 0:
                        percentage = (entry['shares'] / total) * 100
                    else:
                        percentage = 0.0
                else:
                    # Use direct percentage if provided
                    percentage = entry.get('ownership_percentage', entry.get('percentage', 0.0))

                # Determine ownership type
                ownership_type = entry.get('type', entry.get('ownership_type', 'direct'))
                if ownership_type not in ['direct', 'indirect']:
                    ownership_type = 'direct'

                # Owner name
                owner_name = entry.get('owner', entry.get('owner_name', entry.get('name', 'Unknown')))

                parsed_ownership.append({
                    'owner_name': owner_name,
                    'ownership_percentage': round(percentage, 2),
                    'ownership_type': ownership_type
                })

            except Exception as e:
                logger.warning(f"Error parsing ownership entry: {entry}, error: {e}")
                continue

        return parsed_ownership


    def _extract_management_board(self, raw_board: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract management board with names, positions, and dates.

        Week 2 implementation: Board member extraction.

        Args:
            raw_board: Raw board data from KRS

        Returns:
            List of standardized board member entries

        Example Input:
            [
                {
                    "name": "Jan Kowalski",
                    "function": "Prezes Zarządu",
                    "appointed": "2020-01-15"
                }
            ]

        Example Output:
            [
                {
                    "name": "Jan Kowalski",
                    "position": "Prezes Zarządu",
                    "appointment_date": "2020-01-15"
                }
            ]
        """
        extracted_board = []

        for entry in raw_board:
            try:
                # Extract name
                name = entry.get('name', entry.get('member_name', 'Unknown'))

                # Extract position (various field names)
                position = entry.get(
                    'position',
                    entry.get('function', entry.get('role', entry.get('title', 'Member')))
                )

                # Extract appointment date
                appointment_date = entry.get(
                    'appointment_date',
                    entry.get('appointed', entry.get('start_date', None))
                )

                extracted_board.append({
                    'name': name,
                    'position': position,
                    'appointment_date': appointment_date
                })

            except Exception as e:
                logger.warning(f"Error extracting board member: {entry}, error: {e}")
                continue

        return extracted_board


    def _calculate_confidence(
        self,
        processed_data: Dict[str, Any],
        data_sources: List[str],
        target_info: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score based on data quality.

        Week 22 Enhancement: Incorporates LLM quality assessment for intelligent scoring.

        Confidence Scoring Algorithm (from AGENT_IMPLEMENTATION_GUIDE.md):
            Base score (0-125):
            - if krs_data: score += 50
            - if nip_valid: score += 30
            - if gus_data: score += 20
            - if ownership_structure: score += 10
            - if financial_statements: score += 15

            Enhanced formula (Week 22):
            - base_score = normalized to 0-100
            - if llm_quality_score available:
                final = (base_score * 0.7) + (llm_quality_score * 100 * 0.3)
            - else:
                final = base_score

        Args:
            processed_data: Processed company data (may include llm_quality_score)
            data_sources: List of data sources used
            target_info: Original target info with validation results

        Returns:
            Confidence score (0-100)
        """
        score = 0
        max_score = 125

        # KRS data available (+50)
        if "KRS API" in data_sources and processed_data.get('krs_number'):
            score += 50

        # NIP validated (+30)
        if processed_data.get('nip_number'):
            is_valid, _ = self._validate_nip(processed_data['nip_number'])
            if is_valid:
                score += 30

        # GUS data available (+20)
        if "GUS API" in data_sources:
            score += 20

        # Ownership structure parsed (+10)
        if processed_data.get('ownership_structure') and len(processed_data['ownership_structure']) > 0:
            score += 10

        # Financial statements available (+15)
        if processed_data.get('financial_statements'):
            score += 15

        # Normalize base score to 0-100
        base_score = min(100, (score / max_score) * 100)

        # Week 22: Incorporate LLM quality assessment if available
        llm_quality_score = processed_data.get('llm_quality_score')
        if llm_quality_score is not None and isinstance(llm_quality_score, (int, float)):
            # Weighted combination: 70% base data quality + 30% LLM assessment
            # This balances objective data availability with LLM's qualitative evaluation
            final_score = (base_score * 0.7) + (llm_quality_score * 100 * 0.3)
            logger.debug(
                f"Confidence calculation: base={base_score:.2f}, "
                f"llm={llm_quality_score:.2f}, final={final_score:.2f}"
            )
            return round(min(100, final_score), 2)
        else:
            # Fallback to base score if LLM enhancement not available
            return round(base_score, 2)


    def _build_output(
        self,
        target: str,
        data: Dict[str, Any],
        confidence_score: float,
        data_sources: List[str],
        errors: List[str],
        warnings: List[str]
    ) -> CompanyProfileOutput:
        """
        Build structured output using CompanyProfileOutput model.

        Args:
            target: Original target identifier
            data: Processed company data
            confidence_score: Calculated confidence score
            data_sources: List of data sources used
            errors: List of errors encountered
            warnings: List of warnings

        Returns:
            CompanyProfileOutput: Pydantic model with structured data
        """
        # Parse address if available
        address_data = data.get('address')
        address = Address(**address_data) if address_data else None

        # Parse ownership structure
        ownership_structure = []
        for owner_data in data.get('ownership_structure', []):
            try:
                ownership_structure.append(Owner(**owner_data))
            except Exception as e:
                logger.warning(f"Invalid owner data: {owner_data}, error: {e}")

        # Parse management board
        management_board = []
        for member_data in data.get('management_board', []):
            try:
                management_board.append(BoardMember(**member_data))
            except Exception as e:
                logger.warning(f"Invalid board member data: {member_data}, error: {e}")

        # Parse financial statements
        financial_data = data.get('financial_statements')
        financial_statements = FinancialStatements(**financial_data) if financial_data else None

        return CompanyProfileOutput(
            agent_type=self.agent_type,
            target=target,
            company_name=data.get('company_name'),
            krs_number=data.get('krs_number'),
            nip_number=data.get('nip_number'),
            regon_number=data.get('regon_number'),
            legal_form=data.get('legal_form'),
            industry=data.get('industry'),
            registration_date=data.get('registration_date'),
            address=address,
            ownership_structure=ownership_structure,
            management_board=management_board,
            financial_statements=financial_statements,
            confidence_score=confidence_score,
            data_sources=data_sources,
            errors=errors,
            warnings=warnings,
            last_updated=datetime.utcnow()
        )


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

async def execute_company_profile(
    target: str,
    context: Optional[Dict[str, Any]] = None
) -> CompanyProfileOutput:
    """
    Execute company profile agent (convenience function).

    Args:
        target: Company identifier (KRS, NIP, or company name)
        context: Optional additional context

    Returns:
        CompanyProfileOutput: Structured company profile

    Example:
        result = await execute_company_profile(target="KRS 0000123456")
        print(f"Company: {result.company_name}")
        print(f"Confidence: {result.confidence_score}%")
    """
    agent = CompanyProfileAgent()
    return await agent.execute(target, context)
