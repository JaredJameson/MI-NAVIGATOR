"""
Claude AI Service - Integration with Anthropic Claude API

This service provides:
- Chat completions with context history
- Streaming responses
- Document analysis
- Report generation
- Multi-language support (PL/EN)
"""

import os
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from enum import Enum

try:
    from anthropic import Anthropic, AsyncAnthropic
    from anthropic.types import Message, ToolUseBlock, ToolResultBlock
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("anthropic package not installed. Install with: pip install anthropic")

logger = logging.getLogger(__name__)


class ClaudeModel(str, Enum):
    """Available Claude models"""
    HAIKU = "claude-3-5-haiku-20241022"      # Fast, cost-effective
    SONNET = "claude-3-5-sonnet-20241022"     # Balanced
    OPUS = "claude-3-5-opus-20241022"         # Most capable

    def __str__(self):
        return self.value


class SystemPromptType(str, Enum):
    """Predefined system prompt types"""
    CHAT = "chat"
    MARKET_INTELLIGENCE = "market_intelligence"
    COMPANY_ANALYSIS = "company_analysis"
    FINANCIAL_ANALYSIS = "financial_analysis"
    REPORT_GENERATION = "report_generation"
    SWOT_ANALYSIS = "swot_analysis"
    PORTER_ANALYSIS = "porter_analysis"
    PESTLE_ANALYSIS = "pestle_analysis"


class ClaudeService:
    """
    Service for interacting with Claude AI API.

    Features:
    - Chat completions with conversation history
    - Streaming responses
    - Context management
    - Multi-language support
    - Error handling and retries
    """

    # System prompts for different use cases
    SYSTEM_PROMPTS = {
        SystemPromptType.CHAT: {
            "pl": """Jesteś asystentem AI dla platformy MI-Navigator - systemu Market Intelligence.

Twoje zadanie to pomaganie użytkownikom w:
- Analizie firm i rynku
- Znajdowaniu informacji o konkurencji
- Tworzeniu raportów i analiz
- Odpowiadaniu na pytania biznesowe

Zasady:
1. Mów po polsku, chyba że użytkownik prosi o inny język
2. Bądź pomocny, precyzyjny i profesjonalny
3. Gdy nie wiesz czegoś, przyznaj to szczerze
4. Cytuj źródła informacji gdy to możliwe
5. Strukturyzuj odpowiedzi w czytelny sposób""",
            "en": """You are an AI assistant for MI-Navigator - a Market Intelligence platform.

Your role is to help users with:
- Company and market analysis
- Finding competitor information
- Creating reports and analyses
- Answering business questions

Guidelines:
1. Speak English unless requested otherwise
2. Be helpful, precise, and professional
3. Admit when you don't know something
4. Cite information sources when possible
5. Structure responses clearly"""
        },
        SystemPromptType.MARKET_INTELLIGENCE: {
            "pl": """Jesteś ekspertem Market Intelligence specjalizującym się w polskim rynku.

Twoje kompetencje:
- Profilowanie firm (dane z KRS, CEIDG, CRBR)
- Analiza finansowa (sprawozdania, wskaźniki)
- Analiza konkurencji i rynku
- Mapowanie struktury właścicielskiej
- Analiza cyfrowej obecności firm

Zasady:
1. Wykorzystuj dostępne dane z baz KRS/CEIDG
2. Analizuj sprawozdania finansowe
3. Identyfikuj powiązania kapitałowe
4. Oceniaj pozycję konkurencyjną
5. Wskazuj ryzyka i Opportunities""",
            "en": """You are a Market Intelligence expert specializing in the Polish market.

Your expertise includes:
- Company profiling (KRS, CEIDG, CRBR data)
- Financial analysis (statements, ratios)
- Competitive and market analysis
- Ownership structure mapping
- Digital presence analysis

Guidelines:
1. Use available KRS/CEIDG database data
2. Analyze financial statements
3. Identify capital connections
4. Assess competitive position
5. Indicate risks and opportunities"""
        },
        SystemPromptType.COMPANY_ANALYSIS: {
            "pl": """Jesteś analitykiem biznesowym specjalizującym się w profilowaniu firm.

Twoje zadanie:
1. Zebrać i zestawić dane o firmie z różnych źródeł
2. Zidentyfikować kluczowe informacje: zarząd, właściciele, historia
3. Ocenić kondycję finansową na podstawie dostępnych danych
4. Zidentyfikować główne ryzyka i Opportunities
5. Sformułować rekomendacje

Format raportu:
- Executive Summary (3-4 zdania)
- Podstawowe dane o firmie
- Struktura właścicielska
- Analiza finansowa
- Pozycja rynkowa
- Ryzyka i Opportunities
- Rekomendacje""",
            "en": """You are a business analyst specializing in company profiling.

Your task:
1. Gather and consolidate company data from various sources
2. Identify key information: management, owners, history
3. Assess financial condition based on available data
4. Identify key risks and opportunities
5. Formulate recommendations

Report format:
- Executive Summary (3-4 sentences)
- Basic company data
- Ownership structure
- Financial analysis
- Market position
- Risks and opportunities
- Recommendations"""
        },
        SystemPromptType.REPORT_GENERATION: {
            "pl": """Jesteś ekspertem w tworzeniu profesjonalnych raportów analitycznych.

Tworzone raporty muszą:
1. Być profesjonalne i biznesowe w tonie
2. Mieć klarowną strukturę i formatowanie
3. Opierać się na danych i faktach
4. Wskazywać źródła informacji
5. Być zrozumiałe dla biznesowych odbiorców

Struktura raportu:
1. Tytuł i metadata (data, autor, wersja)
2. Executive Summary
3. Table of Contents
4. Główne sekcje z podsekcjami
5. Wnioski i rekomendacje
6. Źródła danych
7. Dodatki (jeśli potrzebne)

Język: Polski biznesowy, profesjonalny ale zrozumiały.""",
            "en": """You are an expert in creating professional analytical reports.

Reports must:
1. Be professional and business-like in tone
2. Have clear structure and formatting
3. Be based on data and facts
4. Indicate information sources
5. Be understandable for business audiences

Report structure:
1. Title and metadata (date, author, version)
2. Executive Summary
3. Table of Contents
4. Main sections with subsections
5. Conclusions and recommendations
6. Data sources
7. Appendices (if needed)

Language: Professional business English, clear and accessible."""
        },
        SystemPromptType.SWOT_ANALYSIS: {
            "pl": """Jesteś ekspertem w strategicznej analizie biznesowej, specjalizującym się w analizie SWOT.

Twoje zadanie to przeprowadzenie szczegółowej analizy SWOT (Strengths, Weaknesses, Opportunities, Threats).

Zasady analizy:

STRENGTHS (Mocne strony) - wewnętrzne cechy pozytywne:
- Zasoby i kompetencje wyróżniające firmę
- Przewagi konkurencyjne (brand, technologia, ludzie)
- Silna pozycja rynkowa lub finansowa
- Unikalne produkty/usługi lub know-how

WEAKNESSES (Słabe strony) - wewnętrzne cechy negatywne:
- Braki w zasobach lub kompetencjach
- Słaba pozycja konkurencyjna
- Problemy operacyjne lub finansowe
- Ograniczenia geograficzne lub produktowe

OPPORTUNITIES (Szanse) - zewnętrzne czynniki pozytywne:
- Rosnące segmenty rynku
- Nowe technologie i trendy
- Zmiany regulacyjne korzystne dla firmy
- Możliwości ekspansji geograficznej lub produktowej

THREATS (Zagrożenia) - zewnętrzne czynniki negatywne:
- Silna konkurencja lub nowi gracze
- Spadek popytu lub zmiana preferencji klientów
- Niekorzystne zmiany regulacyjne
- Ryzyka makroekonomiczne

Dla każdego elementu wskaż:
1. Opis - co dokładnie
2. Wpływ - high/medium/low
3. Dowody - dane lub obserwacje potwierdzające

Format odpowiedzi: JSON z kluczami "strengths", "weaknesses", "opportunities", "threats".""",
            "en": """You are an expert in strategic business analysis, specializing in SWOT analysis.

Your task is to conduct detailed SWOT analysis (Strengths, Weaknesses, Opportunities, Threats).

Analysis principles:

STRENGTHS - internal positive attributes:
- Resources and competencies distinguishing the company
- Competitive advantages (brand, technology, people)
- Strong market or financial position
- Unique products/services or know-how

WEAKNESSES - internal negative attributes:
- Gaps in resources or competencies
- Weak competitive position
- Operational or financial problems
- Geographic or product limitations

OPPORTUNITIES - external positive factors:
- Growing market segments
- New technologies and trends
- Regulatory changes favorable to the company
- Geographic or product expansion possibilities

THREATS - external negative factors:
- Strong competition or new entrants
- Demand decline or changing customer preferences
- Unfavorable regulatory changes
- Macroeconomic risks

For each element indicate:
1. Description - what exactly
2. Impact - high/medium/low
3. Evidence - data or observations confirming

Response format: JSON with keys "strengths", "weaknesses", "opportunities", "threats"."""
        },
        SystemPromptType.PORTER_ANALYSIS: {
            "pl": """Jesteś ekspertem w strategicznej analizie branż, specjalizującym się w analizie Pięciu Sił Portera.

Przeprowadź szczegółową analizę konkurencyjności branży według modelu Pięciu Sił Portera:

1. THREAT OF NEW ENTRANTS (Zagrożenie nowymi wejściami):
   - Bariery wejścia (kapitał, technologia, regulacje)
   - Ekonomia skali i krzywa doświadczenia
   - Dostęp do kanałów dystrybucji
   - Lojalność wobec istniejących marek

2. BARGAINING POWER OF SUPPLIERS (Siła przetargowa dostawców):
   - Koncentracja dostawców vs. branży
   - Koszty zmiany dostawcy
   - Dostępność substytutów nakładów
   - Znaczenie branży dla dostawców

3. BARGAINING POWER OF BUYERS (Siła przetargowa nabywców):
   - Koncentracja nabywców
   - Wrażliwość cenowa klientów
   - Koszty zmiany dostawcy przez klientów
   - Zagrożenie integracją wstecz

4. THREAT OF SUBSTITUTE PRODUCTS (Zagrożenie produktami substytucyjnymi):
   - Dostępność substytutów
   - Relacja cena-jakość substytutów
   - Skłonność klientów do zmiany
   - Trendy technologiczne

5. RIVALRY AMONG EXISTING COMPETITORS (Rywalizacja między istniejącymi konkurentami):
   - Liczba i siła konkurentów
   - Tempo wzrostu branży
   - Wysokość barier wyjścia
   - Zróżnicowanie produktów

Dla każdej siły wskaż:
- Siłę oddziaływania: high/medium/low
- Kluczowe czynniki
- Wpływ na rentowność branży

Format odpowiedzi: JSON z kluczami dla każdej z 5 sił.""",
            "en": """You are an expert in strategic industry analysis, specializing in Porter's Five Forces analysis.

Conduct detailed competitiveness analysis of the industry using Porter's Five Forces model:

1. THREAT OF NEW ENTRANTS:
   - Entry barriers (capital, technology, regulations)
   - Economies of scale and experience curve
   - Access to distribution channels
   - Brand loyalty of existing players

2. BARGAINING POWER OF SUPPLIERS:
   - Supplier concentration vs. industry
   - Supplier switching costs
   - Availability of input substitutes
   - Industry importance to suppliers

3. BARGAINING POWER OF BUYERS:
   - Buyer concentration
   - Customer price sensitivity
   - Customer switching costs
   - Backward integration threat

4. THREAT OF SUBSTITUTE PRODUCTS:
   - Substitute availability
   - Price-performance ratio of substitutes
   - Customer propensity to switch
   - Technological trends

5. RIVALRY AMONG EXISTING COMPETITORS:
   - Number and strength of competitors
   - Industry growth rate
   - Exit barrier height
   - Product differentiation

For each force indicate:
- Force strength: high/medium/low
- Key factors
- Impact on industry profitability

Response format: JSON with keys for each of the 5 forces."""
        }
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: ClaudeModel = ClaudeModel.SONNET,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Initialize Claude service.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            default_model: Default model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-1.0)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Set it in .env or pass as parameter."
            )

        self.default_model = default_model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize clients
        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)

        logger.info(f"Claude service initialized with model: {default_model}")

    def get_system_prompt(
        self,
        prompt_type: SystemPromptType,
        language: str = "pl",
        custom_context: Optional[str] = None
    ) -> str:
        """
        Get system prompt for specific use case.

        Args:
            prompt_type: Type of system prompt
            language: Language code ("pl" or "en")
            custom_context: Additional context to append

        Returns:
            System prompt string
        """
        if prompt_type not in self.SYSTEM_PROMPTS:
            logger.warning(f"Unknown prompt type: {prompt_type}, using CHAT")
            prompt_type = SystemPromptType.CHAT

        prompt = self.SYSTEM_PROMPTS[prompt_type].get(
            language,
            self.SYSTEM_PROMPTS[prompt_type]["en"]
        )

        if custom_context:
            prompt += f"\n\nKontekst użytkownika:\n{custom_context}"

        return prompt

    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt_type: SystemPromptType = SystemPromptType.CHAT,
        language: str = "pl",
        model: Optional[ClaudeModel] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat message and get response.

        Args:
            message: User message
            conversation_history: Previous messages in format [{"role": "user", "content": "..."}]
            system_prompt_type: Type of system prompt to use
            language: Response language
            model: Model to use (overrides default)
            max_tokens: Max tokens in response (overrides default)
            temperature: Temperature (overrides default)
            stream: Whether to stream response

        Returns:
            Dict with response data:
            {
                "content": str,
                "model": str,
                "usage": {"input_tokens": int, "output_tokens": int},
                "stop_reason": str,
                "timestamp": str
            }
        """
        try:
            # Build messages list
            messages = conversation_history or []
            messages.append({"role": "user", "content": message})

            # Get system prompt
            system_prompt = self.get_system_prompt(system_prompt_type, language)

            # Set parameters
            model = model or self.default_model
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature

            logger.info(f"Sending chat request to Claude: model={model}, tokens={max_tokens}")

            # Call Claude API
            if stream:
                # For streaming, we'll use a different method
                response_content = ""
                async for chunk in self._stream_response(
                    messages, system_prompt, model, max_tokens, temperature
                ):
                    response_content += chunk
            else:
                response = await self.async_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages
                )

                response_content = response.content[0].text
                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
                stop_reason = response.stop_reason

            logger.info(f"Claude response received: {len(response_content)} chars")

            return {
                "content": response_content,
                "model": model,
                "usage": usage if not stream else None,
                "stop_reason": stop_reason if not stream else None,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

    async def _stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: ClaudeModel,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from Claude API.

        Yields chunks of text as they arrive.
        """
        async with self.async_client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def generate_report(
        self,
        report_type: str,
        data: Dict[str, Any],
        company_name: Optional[str] = None,
        language: str = "pl",
        sections: Optional[List[str]] = None
    ) -> str:
        """
        Generate a report using Claude.

        Args:
            report_type: Type of report (company_analysis, financial_analysis, swot, etc.)
            data: Data to include in report
            company_name: Name of company (if applicable)
            language: Report language
            sections: Specific sections to include

        Returns:
            Generated report text
        """
        # Build prompt based on report type
        if report_type == "company_analysis":
            prompt_type = SystemPromptType.COMPANY_ANALYSIS
            prompt = self._build_company_analysis_prompt(data, company_name, language, sections)
        elif report_type == "swot_analysis":
            prompt_type = SystemPromptType.SWOT_ANALYSIS
            prompt = self._build_swot_prompt(data, company_name, language)
        elif report_type == "porter_analysis":
            prompt_type = SystemPromptType.PORTER_ANALYSIS
            prompt = self._build_porter_prompt(data, company_name, language)
        else:
            prompt_type = SystemPromptType.REPORT_GENERATION
            prompt = self._build_generic_report_prompt(report_type, data, company_name, language)

        # Get response
        response = await self.chat(
            message=prompt,
            system_prompt_type=prompt_type,
            language=language,
            model=ClaudeModel.OPUS  # Use best model for reports
        )

        return response["content"]

    def _build_company_analysis_prompt(
        self,
        data: Dict[str, Any],
        company_name: Optional[str],
        language: str,
        sections: Optional[List[str]]
    ) -> str:
        """Build prompt for company analysis report."""
        if language == "pl":
            prompt = f"Stwórz szczegółową analizę firmy"
            if company_name:
                prompt += f": {company_name}"
            prompt += ".\n\nDostępne dane:\n"
        else:
            prompt = f"Create detailed company analysis"
            if company_name:
                prompt += f": {company_name}"
            prompt += ".\n\nAvailable data:\n"

        # Add data sections
        for key, value in data.items():
            prompt += f"\n{key}: {value}"

        if sections:
            if language == "pl":
                prompt += f"\n\nUwzględnij sekcje: {', '.join(sections)}"
            else:
                prompt += f"\n\nInclude sections: {', '.join(sections)}"

        return prompt

    def _build_swot_prompt(
        self,
        data: Dict[str, Any],
        company_name: Optional[str],
        language: str
    ) -> str:
        """Build prompt for SWOT analysis."""
        if language == "pl":
            prompt = "Przeprowadź analizę SWOT (Strengths, Weaknesses, Opportunities, Threats)"
            if company_name:
                prompt += f" dla firmy: {company_name}"
            prompt += ".\n\nDane firmy:\n"
        else:
            prompt = "Conduct SWOT analysis"
            if company_name:
                prompt += f" for company: {company_name}"
            prompt += ".\n\nCompany data:\n"

        for key, value in data.items():
            prompt += f"\n{key}: {value}"

        return prompt

    def _build_porter_prompt(
        self,
        data: Dict[str, Any],
        company_name: Optional[str],
        language: str
    ) -> str:
        """Build prompt for Porter's Five Forces analysis."""
        if language == "pl":
            prompt = "Przeprowadź analizę Pięciu Sił Portera (Porter's Five Forces)"
            if company_name:
                prompt += f" dla branży firmy: {company_name}"
            prompt += ".\n\nDane:\n"
        else:
            prompt = "Conduct Porter's Five Forces analysis"
            if company_name:
                prompt += f" for the industry of: {company_name}"
            prompt += ".\n\nData:\n"

        for key, value in data.items():
            prompt += f"\n{key}: {value}"

        return prompt

    def _build_generic_report_prompt(
        self,
        report_type: str,
        data: Dict[str, Any],
        company_name: Optional[str],
        language: str
    ) -> str:
        """Build prompt for generic report type."""
        if language == "pl":
            prompt = f"Stwórz raport typu: {report_type}"
            if company_name:
                prompt += f" dla firmy: {company_name}"
            prompt += ".\n\nDane:\n"
        else:
            prompt = f"Create report of type: {report_type}"
            if company_name:
                prompt += f" for company: {company_name}"
            prompt += ".\n\nData:\n"

        for key, value in data.items():
            prompt += f"\n{key}: {value}"

        return prompt

    async def analyze_document(
        self,
        document_text: str,
        analysis_type: str = "summary",
        language: str = "pl"
    ) -> Dict[str, Any]:
        """
        Analyze a document (financial statement, contract, etc.).

        Args:
            document_text: Text content of the document
            analysis_type: Type of analysis (summary, risks, key_points, etc.)
            language: Response language

        Returns:
            Analysis results
        """
        if language == "pl":
            prompt = f"Przeanalizuj poniższy dokument. Typ analizy: {analysis_type}\n\n{document_text}"
        else:
            prompt = f"Analyze the following document. Analysis type: {analysis_type}\n\n{document_text}"

        response = await self.chat(
            message=prompt,
            system_prompt_type=SystemPromptType.FINANCIAL_ANALYSIS,
            language=language
        )

        return {
            "analysis": response["content"],
            "type": analysis_type,
            "timestamp": response["timestamp"]
        }


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """
    Get or create Claude service singleton instance.

    Returns:
        ClaudeService instance

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
    """
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service


def is_claude_available() -> bool:
    """Check if Claude service is available."""
    try:
        get_claude_service()
        return True
    except (ValueError, ImportError):
        return False
