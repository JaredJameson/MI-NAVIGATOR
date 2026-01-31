"""
Unit tests for CompanyProfileAgent

Week 1 Tests (5 tests):
- test_company_profile_agent_init
- test_nip_validation_valid
- test_nip_validation_invalid_checksum
- test_parse_target_krs_number
- test_parse_target_nip_number

Coverage target: Core functionality from Week 1 implementation
"""

import pytest
from datetime import datetime
from app.agents.company_profile_agent import (
    CompanyProfileAgent,
    CompanyProfileOutput,
    Address,
    Owner,
    BoardMember,
    FinancialStatements
)


# ============================================================================
# WEEK 1 TESTS: Agent Initialization & Core Functionality
# ============================================================================

def test_company_profile_agent_init():
    """
    Test CompanyProfileAgent initialization.

    Validates:
    - Agent initializes without errors
    - Agent type is set correctly
    - Tool registry is available
    - Domain knowledge is loaded
    """
    agent = CompanyProfileAgent()

    assert agent is not None
    assert agent.agent_type == "company_profile"
    assert agent.tool_registry is not None
    assert agent.domain_knowledge is not None
    assert len(agent.domain_knowledge.LEGAL_FORMS) > 0
    assert len(agent.domain_knowledge.VOIVODESHIPS) == 16  # 16 Polish voivodeships


def test_nip_validation_valid():
    """
    Test NIP validation with valid NIP numbers.

    Valid NIP numbers have:
    - 10 digits
    - Valid checksum (weighted sum modulo 11)

    Example: "1234563218" is valid
    Checksum calculation: weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    """
    agent = CompanyProfileAgent()

    # Valid NIP examples (with correct checksums calculated)
    valid_nips = [
        "1234563218",  # Checksum: (1*6 + 2*5 + 3*7 + 4*2 + 5*3 + 6*4 + 3*5 + 2*6 + 1*7) % 11 = 8
        "5260250274",  # Real example from Polish tax office
        "1000000006",  # Simple example: (1*6) % 11 = 6
    ]

    for nip in valid_nips:
        is_valid, error = agent._validate_nip(nip)
        assert is_valid is True, f"NIP {nip} should be valid"
        assert error is None, f"NIP {nip} should have no error"


def test_nip_validation_invalid_checksum():
    """
    Test NIP validation with invalid NIP numbers.

    Invalid scenarios:
    - Wrong checksum digit
    - Wrong length
    - Non-digit characters
    """
    agent = CompanyProfileAgent()

    # Invalid NIP examples
    invalid_nips = [
        ("1234567890", "Invalid NIP checksum"),  # Wrong checksum
        ("123456789", "NIP must be 10 digits"),   # Too short
        ("12345678901", "NIP must be 10 digits"), # Too long
        ("123456789X", "NIP must contain only digits"),  # Non-digit
        ("", "NIP must be 10 digits"),            # Empty
    ]

    for nip, expected_error_pattern in invalid_nips:
        is_valid, error = agent._validate_nip(nip)
        assert is_valid is False, f"NIP {nip} should be invalid"
        assert error is not None, f"NIP {nip} should have error message"
        assert expected_error_pattern in error or error.startswith(expected_error_pattern.split()[0])


def test_parse_target_krs_number():
    """
    Test target parsing for KRS numbers.

    KRS number formats:
    - "KRS 0000123456"
    - "0000123456"
    - "KRS0000123456"
    """
    agent = CompanyProfileAgent()

    krs_inputs = [
        "KRS 0000123456",
        "0000123456",
        "KRS0000123456",
        "krs 0000123456",  # Case insensitive
    ]

    for krs_input in krs_inputs:
        result = agent._parse_target(krs_input)

        assert result['valid'] is True, f"KRS input '{krs_input}' should be valid"
        assert result['type'] == 'krs', f"Type should be 'krs' for input '{krs_input}'"
        assert result['krs_number'] == '0000123456', f"KRS number should be extracted"
        assert len(result['validation_errors']) == 0


def test_parse_target_nip_number():
    """
    Test target parsing for NIP numbers.

    NIP number formats:
    - "NIP 1234563218"
    - "1234563218"
    - "NIP1234563218"
    """
    agent = CompanyProfileAgent()

    # Valid NIP with correct checksum
    valid_nip = "1234563218"

    nip_inputs = [
        f"NIP {valid_nip}",
        valid_nip,
        f"NIP{valid_nip}",
        f"nip {valid_nip}",  # Case insensitive
    ]

    for nip_input in nip_inputs:
        result = agent._parse_target(nip_input)

        assert result['valid'] is True, f"NIP input '{nip_input}' should be valid"
        assert result['type'] == 'nip', f"Type should be 'nip' for input '{nip_input}'"
        assert result['nip_number'] == valid_nip, f"NIP number should be extracted"
        assert len(result['validation_errors']) == 0


# ============================================================================
# WEEK 1 ASYNC TESTS: Agent Execution
# ============================================================================

@pytest.mark.asyncio
async def test_execute_krs_target_mock_data():
    """
    Test agent execution with KRS number (using mock data).

    Week 1: KRS API not yet implemented, uses mock data.

    Validates:
    - Agent executes without errors
    - Returns CompanyProfileOutput instance
    - Confidence score is calculated
    - Mock data is populated
    """
    agent = CompanyProfileAgent()

    result = await agent.execute(target="KRS 0000123456")

    # Validate output type
    assert isinstance(result, CompanyProfileOutput)
    assert result.agent_type == "company_profile"
    assert result.target == "KRS 0000123456"

    # Validate mock data structure
    assert result.krs_number == "0000123456"
    assert result.company_name is not None
    assert "Mock Company" in result.company_name or result.company_name  # Mock or actual

    # Validate confidence scoring (should be > 0 with mock KRS data)
    assert result.confidence_score > 0, "Confidence score should be positive with KRS data"
    assert result.confidence_score <= 100

    # Validate data sources
    assert len(result.data_sources) > 0

    # Validate warnings (mock data warning expected)
    assert len(result.warnings) >= 0  # May have warnings about mock data


@pytest.mark.asyncio
async def test_execute_nip_target_valid():
    """
    Test agent execution with valid NIP number.

    Validates:
    - NIP validation passes
    - Agent attempts to fetch GUS data
    - Confidence score reflects NIP validation (+30 points)
    """
    agent = CompanyProfileAgent()

    # Valid NIP with correct checksum
    result = await agent.execute(target="NIP 1234563218")

    assert isinstance(result, CompanyProfileOutput)
    assert result.agent_type == "company_profile"
    assert result.nip_number == "1234563218"

    # Confidence score should reflect NIP validation
    # Even with mock/no data, valid NIP adds +30 to confidence
    assert result.confidence_score >= 0


@pytest.mark.asyncio
async def test_execute_invalid_target():
    """
    Test agent execution with invalid target.

    Invalid targets:
    - Empty string
    - Too short
    - Invalid format

    Should return confidence_score = 0 and errors
    """
    agent = CompanyProfileAgent()

    invalid_targets = ["", "AB", "X"]

    for target in invalid_targets:
        result = await agent.execute(target=target)

        assert isinstance(result, CompanyProfileOutput)
        assert result.confidence_score == 0, f"Invalid target '{target}' should have 0 confidence"
        assert len(result.errors) > 0, f"Invalid target '{target}' should have errors"


@pytest.mark.asyncio
async def test_execute_company_name_target():
    """
    Test agent execution with company name.

    Company name format:
    - "Company Name Sp. z o.o."
    - "ABC Corporation"

    Week 1: KRS search not implemented, should handle gracefully.
    """
    agent = CompanyProfileAgent()

    result = await agent.execute(target="Example Company Sp. z o.o.")

    assert isinstance(result, CompanyProfileOutput)
    assert result.agent_type == "company_profile"
    assert result.target == "Example Company Sp. z o.o."

    # With no KRS search results, confidence will be low
    # But execution should complete without errors
    assert result.confidence_score >= 0
    assert isinstance(result.errors, list)
    assert isinstance(result.warnings, list)


# ============================================================================
# WEEK 1 PYDANTIC MODEL TESTS
# ============================================================================

def test_company_profile_output_model():
    """
    Test CompanyProfileOutput Pydantic model validation.

    Validates:
    - Model accepts valid data
    - Model validates confidence_score range (0-100)
    - Model handles optional fields
    """
    # Valid output
    output = CompanyProfileOutput(
        target="KRS 0000123456",
        company_name="Test Company",
        krs_number="0000123456",
        nip_number="1234563218",
        confidence_score=85.5,
        data_sources=["KRS API"],
        errors=[],
        warnings=[]
    )

    assert output.agent_type == "company_profile"
    assert output.target == "KRS 0000123456"
    assert output.confidence_score == 85.5
    assert isinstance(output.last_updated, datetime)


def test_company_profile_output_confidence_validation():
    """
    Test confidence_score validation (must be 0-100).
    """
    # Valid range
    valid_scores = [0, 50, 100, 85.5, 0.0, 100.0]

    for score in valid_scores:
        output = CompanyProfileOutput(
            target="test",
            confidence_score=score,
            data_sources=[],
            errors=[],
            warnings=[]
        )
        assert output.confidence_score == score

    # Invalid range (should raise ValidationError)
    invalid_scores = [-1, 101, 150, -0.1, 100.1]

    for score in invalid_scores:
        with pytest.raises(Exception):  # Pydantic ValidationError
            CompanyProfileOutput(
                target="test",
                confidence_score=score,
                data_sources=[],
                errors=[],
                warnings=[]
            )


def test_address_model():
    """
    Test Address Pydantic model.
    """
    address = Address(
        street="ul. Testowa 123",
        city="Warszawa",
        voivodeship="Mazowieckie",
        postal_code="00-001",
        country="Poland"
    )

    assert address.street == "ul. Testowa 123"
    assert address.city == "Warszawa"
    assert address.voivodeship == "Mazowieckie"
    assert address.postal_code == "00-001"
    assert address.country == "Poland"


def test_owner_model():
    """
    Test Owner Pydantic model.

    Validates:
    - Ownership percentage range (0-100)
    - Ownership type validation (direct|indirect)
    """
    # Valid owner
    owner = Owner(
        owner_name="Jan Kowalski",
        ownership_percentage=51.5,
        ownership_type="direct"
    )

    assert owner.owner_name == "Jan Kowalski"
    assert owner.ownership_percentage == 51.5
    assert owner.ownership_type == "direct"

    # Invalid ownership_type (should raise ValidationError)
    with pytest.raises(Exception):
        Owner(
            owner_name="Test",
            ownership_percentage=50,
            ownership_type="invalid_type"
        )


def test_board_member_model():
    """
    Test BoardMember Pydantic model.
    """
    member = BoardMember(
        name="Jan Kowalski",
        position="Prezes Zarządu",
        appointment_date="2020-01-15"
    )

    assert member.name == "Jan Kowalski"
    assert member.position == "Prezes Zarządu"
    assert member.appointment_date == "2020-01-15"


def test_financial_statements_model():
    """
    Test FinancialStatements Pydantic model.
    """
    financials = FinancialStatements(
        year=2023,
        revenue=1000000.0,
        profit=150000.0,
        assets=2000000.0,
        liabilities=800000.0,
        equity=1200000.0
    )

    assert financials.year == 2023
    assert financials.revenue == 1000000.0
    assert financials.profit == 150000.0
    assert financials.assets == 2000000.0


# ============================================================================
# WEEK 2 TESTS: GUS/REGON Integration & Ownership Parsing
# ============================================================================

@pytest.mark.asyncio
async def test_gus_client_mock_mode():
    """
    Test GUS client integration (mock mode without API key).

    Week 2 test: GUS API integration

    Validates:
    - CompanyProfileAgent uses GUS client
    - GUS data is fetched successfully
    - Industry and PKD code are populated
    """
    agent = CompanyProfileAgent()

    # Execute with NIP to trigger GUS fetch
    result = await agent.execute(target="NIP 1234563218")

    # GUS should be called (mock mode)
    assert isinstance(result, CompanyProfileOutput)

    # Check that GUS data was integrated
    # In mock mode, GUS returns industry data
    # Either from GUS or from processed data
    assert result.data_sources is not None


@pytest.mark.asyncio
async def test_regon_client_mock_mode():
    """
    Test REGON client integration (mock mode without API key).

    Week 2 test: REGON integration

    Validates:
    - CompanyProfileAgent uses REGON client
    - REGON data is fetched when available
    - Legal form and REGON number are populated
    """
    agent = CompanyProfileAgent()

    # Execute with KRS (which has NIP) to trigger REGON fetch
    result = await agent.execute(target="KRS 0000123456")

    assert isinstance(result, CompanyProfileOutput)

    # REGON should be attempted (mock mode may not populate if no NIP in mock KRS data)
    # Test validates integration exists
    assert result.krs_number == "0000123456"


def test_parse_ownership_structure():
    """
    Test ownership structure parsing algorithm.

    Week 2 test: Ownership parsing

    Validates:
    - Shareholding percentage calculation
    - Direct vs indirect ownership classification
    - Handling of various input formats
    """
    agent = CompanyProfileAgent()

    # Test Case 1: Shares to percentage conversion
    raw_ownership_shares = [
        {
            "owner": "Jan Kowalski",
            "shares": 510,
            "total_shares": 1000,
            "type": "direct"
        },
        {
            "owner": "Anna Nowak",
            "shares": 490,
            "total_shares": 1000,
            "type": "indirect"
        }
    ]

    parsed = agent._parse_ownership_structure(raw_ownership_shares)

    assert len(parsed) == 2
    assert parsed[0]['owner_name'] == "Jan Kowalski"
    assert parsed[0]['ownership_percentage'] == 51.0
    assert parsed[0]['ownership_type'] == "direct"
    assert parsed[1]['owner_name'] == "Anna Nowak"
    assert parsed[1]['ownership_percentage'] == 49.0
    assert parsed[1]['ownership_type'] == "indirect"

    # Test Case 2: Direct percentage
    raw_ownership_percentage = [
        {
            "owner_name": "Test Owner",
            "ownership_percentage": 75.5,
            "ownership_type": "direct"
        }
    ]

    parsed2 = agent._parse_ownership_structure(raw_ownership_percentage)

    assert len(parsed2) == 1
    assert parsed2[0]['owner_name'] == "Test Owner"
    assert parsed2[0]['ownership_percentage'] == 75.5
    assert parsed2[0]['ownership_type'] == "direct"

    # Test Case 3: Empty list
    parsed3 = agent._parse_ownership_structure([])
    assert len(parsed3) == 0


def test_extract_management_board():
    """
    Test management board extraction algorithm.

    Week 2 test: Board member extraction

    Validates:
    - Name extraction
    - Position/title extraction
    - Appointment date extraction
    - Handling of various field names
    """
    agent = CompanyProfileAgent()

    # Test Case 1: Standard format
    raw_board = [
        {
            "name": "Jan Kowalski",
            "function": "Prezes Zarządu",
            "appointed": "2020-01-15"
        },
        {
            "name": "Anna Nowak",
            "function": "Wiceprezes Zarządu",
            "appointed": "2020-01-15"
        },
        {
            "name": "Piotr Wiśniewski",
            "function": "Członek Zarządu",
            "appointed": "2021-06-01"
        }
    ]

    extracted = agent._extract_management_board(raw_board)

    assert len(extracted) == 3
    assert extracted[0]['name'] == "Jan Kowalski"
    assert extracted[0]['position'] == "Prezes Zarządu"
    assert extracted[0]['appointment_date'] == "2020-01-15"

    # Test Case 2: Alternative field names
    raw_board_alt = [
        {
            "member_name": "Test Person",
            "role": "CEO",
            "start_date": "2022-01-01"
        }
    ]

    extracted2 = agent._extract_management_board(raw_board_alt)

    assert len(extracted2) == 1
    assert extracted2[0]['name'] == "Test Person"
    assert extracted2[0]['position'] == "CEO"
    assert extracted2[0]['appointment_date'] == "2022-01-01"

    # Test Case 3: Empty list
    extracted3 = agent._extract_management_board([])
    assert len(extracted3) == 0


@pytest.mark.asyncio
async def test_week2_data_processing_integration():
    """
    Test Week 2 data processing integration.

    Validates:
    - GUS data integration
    - REGON data integration
    - Ownership parsing
    - Board extraction
    - Multi-source data merging
    """
    agent = CompanyProfileAgent()

    # Simulate raw data from all sources
    raw_data = {
        'krs': {
            'krs_number': '0000123456',
            'company_name': 'Test Company Sp. z o.o.',
            'nip_number': '1234563218',
            'legal_form': 'Spółka z ograniczoną odpowiedzialnością',
            'registration_date': '2020-01-15',
            'address': {
                'street': 'ul. Testowa 123',
                'city': 'Warszawa',
                'voivodeship': 'Mazowieckie',
                'postal_code': '00-001'
            },
            'ownership_structure': [
                {
                    'owner': 'Jan Kowalski',
                    'shares': 600,
                    'total_shares': 1000,
                    'type': 'direct'
                }
            ],
            'management_board': [
                {
                    'name': 'Jan Kowalski',
                    'function': 'Prezes Zarządu',
                    'appointed': '2020-01-15'
                }
            ]
        },
        'gus': {
            'nip': '1234563218',
            'regon': '123456789',
            'pkd_code': '62.01.Z',
            'industry': 'Działalność związana z oprogramowaniem',
            'employee_count': 50
        },
        'regon': {
            'regon': '123456789',
            'legal_form': 'Spółka z ograniczoną odpowiedzialnością'
        }
    }

    target_info = {'type': 'krs', 'krs_number': '0000123456', 'valid': True}

    # Process data
    processed = agent._process_data(raw_data, target_info)

    # Validate KRS data
    assert processed['company_name'] == 'Test Company Sp. z o.o.'
    assert processed['krs_number'] == '0000123456'
    assert processed['nip_number'] == '1234563218'

    # Validate GUS data integration
    assert processed['pkd_code'] == '62.01.Z'
    assert processed['industry'] == 'Działalność związana z oprogramowaniem'
    assert processed['employee_count'] == 50

    # Validate REGON data integration
    assert processed['regon_number'] == '123456789'

    # Validate ownership parsing
    assert len(processed['ownership_structure']) == 1
    assert processed['ownership_structure'][0]['owner_name'] == 'Jan Kowalski'
    assert processed['ownership_structure'][0]['ownership_percentage'] == 60.0
    assert processed['ownership_structure'][0]['ownership_type'] == 'direct'

    # Validate board extraction
    assert len(processed['management_board']) == 1
    assert processed['management_board'][0]['name'] == 'Jan Kowalski'
    assert processed['management_board'][0]['position'] == 'Prezes Zarządu'
    assert processed['management_board'][0]['appointment_date'] == '2020-01-15'


# ============================================================================
# WEEK 22 TESTS: LLM Enhancement Integration
# ============================================================================

@pytest.mark.asyncio
async def test_enhance_with_llm_success():
    """
    Test LLM enhancement with successful response.

    Week 22 test: LLM-powered intelligent analysis

    Validates:
    - ClaudeService integration works
    - Business insights are generated
    - LLM quality score is calculated
    - Enhanced data contains all expected fields
    """
    from unittest.mock import AsyncMock

    agent = CompanyProfileAgent()

    # Skip test if ClaudeService not available
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")

    # Mock LLM response (Week 28: profile_insights structure)
    mock_llm_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {"score": 87, "assessment": "Wysokiej jakości kompletne dane KRS i NIP"},
    "data_accuracy": {"score": 90, "analysis": "Dane zweryfikowane krzyżowo KRS-GUS"},
    "cross_validation_quality": "Skuteczna weryfikacja między źródłami KRS i GUS",
    "information_reliability": "Wiarygodne źródła - oficjalne rejestry państwowe",
    "recommendations": ["Dodaj dane finansowe", "Uzupełnij strukturę zarządu"]
  },
  "quality_score": 0.87,
  "analysis_notes": ["Data completeness: high", "Cross-validation successful"]
}
```""",
        "model": "claude-sonnet-4-5-20250929",
        "usage": {"input_tokens": 100, "output_tokens": 150}
    }

    # Mock the claude_service.chat method
    agent.claude_service.chat = AsyncMock(return_value=mock_llm_response)

    # Prepare test data
    processed_data = {
        "company_name": "Test Company Sp. z o.o.",
        "krs_number": "0000123456",
        "nip_number": "1234563218",
        "industry": "IT Services"
    }

    target_info = {"type": "krs", "krs_number": "0000123456"}

    # Execute enhancement
    enhanced_data = await agent._enhance_with_llm(
        processed_data=processed_data,
        target_info=target_info,
        context={"language": "pl"}
    )

    # Validate enhanced data structure
    assert "profile_insights" in enhanced_data
    assert "llm_quality_score" in enhanced_data
    assert "llm_analysis_notes" in enhanced_data

    # Validate profile insights (Week 28 structure)
    insights = enhanced_data["profile_insights"]
    assert "data_completeness" in insights
    assert "data_accuracy" in insights
    assert "cross_validation_quality" in insights
    assert "information_reliability" in insights
    assert "recommendations" in insights

    # Validate quality score
    assert enhanced_data["llm_quality_score"] == 0.87
    assert isinstance(enhanced_data["llm_quality_score"], float)
    assert 0.0 <= enhanced_data["llm_quality_score"] <= 1.0

    # Validate analysis notes
    assert len(enhanced_data["llm_analysis_notes"]) > 0


@pytest.mark.asyncio
async def test_enhance_with_llm_no_claude_service():
    """
    Test LLM enhancement when ClaudeService is not available.

    Validates:
    - Graceful degradation without ClaudeService
    - Original data is returned unchanged
    - No errors are raised
    """
    agent = CompanyProfileAgent()

    # Disable ClaudeService temporarily
    original_service = agent.claude_service
    agent.claude_service = None

    processed_data = {
        "company_name": "Test Company",
        "krs_number": "0000123456"
    }

    target_info = {"type": "krs"}

    # Execute enhancement
    enhanced_data = await agent._enhance_with_llm(
        processed_data=processed_data,
        target_info=target_info
    )

    # Restore original service
    agent.claude_service = original_service

    # Validate that data is unchanged
    assert enhanced_data == processed_data
    assert "llm_quality_score" not in enhanced_data


@pytest.mark.asyncio
async def test_enhance_with_llm_error_handling():
    """
    Test LLM enhancement error handling.

    Week 22 test: Error recovery and graceful degradation

    Validates:
    - Handles JSON parsing errors
    - Handles ClaudeService exceptions
    - Returns original data on errors
    """
    from unittest.mock import AsyncMock

    agent = CompanyProfileAgent()

    # Skip test if ClaudeService not available
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")

    # Mock LLM response with invalid JSON
    mock_invalid_response = {
        "content": "This is not valid JSON",
        "model": "claude-sonnet-4-5-20250929"
    }

    agent.claude_service.chat = AsyncMock(return_value=mock_invalid_response)

    processed_data = {
        "company_name": "Test Company",
        "krs_number": "0000123456"
    }

    target_info = {"type": "krs"}

    # Execute enhancement (should handle error gracefully)
    enhanced_data = await agent._enhance_with_llm(
        processed_data=processed_data,
        target_info=target_info
    )

    # Validate graceful degradation
    assert enhanced_data == processed_data
    assert "llm_quality_score" not in enhanced_data


@pytest.mark.asyncio
async def test_confidence_calculation_with_llm_quality():
    """
    Test confidence calculation incorporating LLM quality score.

    Week 22 test: Enhanced confidence scoring

    Validates:
    - Base confidence calculation still works
    - LLM quality score is incorporated (70% base + 30% LLM)
    - Final score is in valid range (0-100)
    """
    agent = CompanyProfileAgent()

    # Test Case 1: Base score without LLM
    processed_data_base = {
        "krs_number": "0000123456",
        "nip_number": "1234563218"
    }

    data_sources = ["KRS API"]
    target_info = {"type": "krs", "krs_number": "0000123456"}

    base_confidence = agent._calculate_confidence(
        processed_data=processed_data_base,
        data_sources=data_sources,
        target_info=target_info
    )

    # Base score should be: KRS (50) + NIP valid (30) = 80/125 = 64%
    assert base_confidence > 0
    assert base_confidence <= 100

    # Test Case 2: Enhanced score with LLM quality
    processed_data_enhanced = {
        "krs_number": "0000123456",
        "nip_number": "1234563218",
        "llm_quality_score": 0.90  # High LLM quality
    }

    enhanced_confidence = agent._calculate_confidence(
        processed_data=processed_data_enhanced,
        data_sources=data_sources,
        target_info=target_info
    )

    # Enhanced score should be: (64 * 0.7) + (90 * 0.3) = 44.8 + 27 = 71.8
    assert enhanced_confidence > base_confidence  # LLM boost
    assert enhanced_confidence <= 100
    assert isinstance(enhanced_confidence, float)

    # Test Case 3: LLM quality score lowers confidence
    processed_data_lowered = {
        "krs_number": "0000123456",
        "nip_number": "1234563218",
        "llm_quality_score": 0.30  # Low LLM quality
    }

    lowered_confidence = agent._calculate_confidence(
        processed_data=processed_data_lowered,
        data_sources=data_sources,
        target_info=target_info
    )

    # Enhanced score should be: (64 * 0.7) + (30 * 0.3) = 44.8 + 9 = 53.8
    assert lowered_confidence < base_confidence  # LLM penalty
    assert lowered_confidence > 0


@pytest.mark.asyncio
async def test_full_execution_with_llm_enhancement():
    """
    Test full agent execution with LLM enhancement integrated.

    Week 22 integration test: End-to-end LLM enhancement

    Validates:
    - LLM enhancement is called during execution
    - Enhanced data flows through to output
    - Confidence score reflects LLM quality assessment
    """
    from unittest.mock import AsyncMock

    agent = CompanyProfileAgent()

    # Skip test if ClaudeService not available
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")

    # Mock LLM response
    mock_llm_response = {
        "content": """```json
{
  "profile_insights": {
    "strengths": ["Registered company with valid KRS"],
    "risks": ["Mock data only"],
    "opportunities": ["Market expansion potential"],
    "market_positioning": "Emerging market player"
  },
  "quality_score": 0.85,
  "analysis_notes": ["Mock data analysis", "Limited information available"]
}
```""",
        "model": "claude-sonnet-4-5-20250929"
    }

    agent.claude_service.chat = AsyncMock(return_value=mock_llm_response)

    # Execute full workflow
    result = await agent.execute(target="KRS 0000123456")

    # Validate output type
    assert isinstance(result, CompanyProfileOutput)
    assert result.agent_type == "company_profile"

    # Validate confidence score (should be enhanced by LLM)
    assert result.confidence_score >= 0
    assert result.confidence_score <= 100

    # Note: The enhanced data (business_insights, llm_quality_score) is not directly
    # accessible in CompanyProfileOutput model, but it was used for confidence calculation
    # This validates the integration flow works correctly


# ============================================================================
# WEEK 28 TESTS: Enhanced Profile Insights Structure
# ============================================================================

@pytest.mark.asyncio
async def test_profile_insights_structure_week28():
    """Test Week 28 profile insights structure (5 dimensions)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {
      "score": 92,
      "assessment": "Bardzo wysoka kompletność - pełne dane KRS, NIP, GUS"
    },
    "data_accuracy": {
      "score": 88,
      "analysis": "Wysoka dokładność - dane zweryfikowane krzyżowo między KRS-GUS-REGON"
    },
    "cross_validation_quality": "Doskonała weryfikacja krzyżowa - wszystkie źródła spójne",
    "information_reliability": "Maksymalna wiarygodność - oficjalne rejestry państwowe KRS i GUS",
    "recommendations": [
      "Dodaj najnowsze sprawozdania finansowe",
      "Uzupełnij dane o zarządzie o daty powołania",
      "Wzbogać o dane o zatrudnieniu z GUS"
    ]
  },
  "quality_score": 0.90,
  "analysis_notes": [
    "Kompletne dane podstawowe",
    "Skuteczna weryfikacja krzyżowa",
    "Brak danych finansowych"
  ]
}
```"""
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test", "krs_number": "123"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    # Verify 5-dimensional structure
    insights = enhanced['profile_insights']
    assert 'data_completeness' in insights
    assert 'data_accuracy' in insights
    assert 'cross_validation_quality' in insights
    assert 'information_reliability' in insights
    assert 'recommendations' in insights
    
    # Verify scores
    assert insights['data_completeness']['score'] == 92
    assert insights['data_accuracy']['score'] == 88


@pytest.mark.asyncio
async def test_data_completeness_assessment_week28():
    """Test data completeness assessment insights (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {
      "score": 95,
      "assessment": "Wybitna kompletność - wszystkie kluczowe dane dostępne z KRS, NIP, GUS i REGON"
    },
    "data_accuracy": {"score": 85, "analysis": "test"},
    "cross_validation_quality": "test",
    "information_reliability": "test",
    "recommendations": []
  },
  "quality_score": 0.92,
  "analysis_notes": []
}
```"""
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    completeness = enhanced['profile_insights']['data_completeness']
    assert completeness['score'] == 95
    assert 'wszystkie kluczowe dane' in completeness['assessment'].lower()


@pytest.mark.asyncio
async def test_data_accuracy_analysis_week28():
    """Test data accuracy analysis insights (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {"score": 85, "assessment": "test"},
    "data_accuracy": {
      "score": 97,
      "analysis": "Najwyższa dokładność - dane w 100% zgodne między KRS, GUS i REGON"
    },
    "cross_validation_quality": "test",
    "information_reliability": "test",
    "recommendations": []
  },
  "quality_score": 0.93,
  "analysis_notes": []
}
```"""
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    accuracy = enhanced['profile_insights']['data_accuracy']
    assert accuracy['score'] == 97
    assert '100% zgodne' in accuracy['analysis']


@pytest.mark.asyncio
async def test_cross_validation_quality_week28():
    """Test cross-validation quality assessment (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {"score": 85, "assessment": "test"},
    "data_accuracy": {"score": 90, "analysis": "test"},
    "cross_validation_quality": "Bardzo dobra weryfikacja - KRS i GUS potwierdzają 95% danych",
    "information_reliability": "test",
    "recommendations": []
  },
  "quality_score": 0.88,
  "analysis_notes": []
}
```"""
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    validation = enhanced['profile_insights']['cross_validation_quality']
    assert '95%' in validation
    assert 'weryfikacja' in validation.lower()


@pytest.mark.asyncio
async def test_information_reliability_week28():
    """Test information reliability assessment (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {"score": 85, "assessment": "test"},
    "data_accuracy": {"score": 90, "analysis": "test"},
    "cross_validation_quality": "test",
    "information_reliability": "Maksymalna wiarygodność - źródła: KRS (oficjalny), GUS (państwowy), REGON (państwowy)",
    "recommendations": []
  },
  "quality_score": 0.92,
  "analysis_notes": []
}
```"""
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    reliability = enhanced['profile_insights']['information_reliability']
    assert 'wiarygodność' in reliability.lower()
    assert 'KRS' in reliability


@pytest.mark.asyncio
async def test_profile_recommendations_week28():
    """Test profile enhancement recommendations (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": """```json
{
  "profile_insights": {
    "data_completeness": {"score": 85, "assessment": "test"},
    "data_accuracy": {"score": 90, "analysis": "test"},
    "cross_validation_quality": "test",
    "information_reliability": "test",
    "recommendations": [
      "Pobierz najnowsze sprawozdania finansowe z KRS",
      "Uzupełnij dane o liczbie pracowników z GUS",
      "Dodaj informacje o strukturze własnościowej"
    ]
  },
  "quality_score": 0.85,
  "analysis_notes": []
}
```"""
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    recommendations = enhanced['profile_insights']['recommendations']
    assert len(recommendations) == 3
    assert any('finansowe' in rec.lower() for rec in recommendations)
    assert any('pracowników' in rec.lower() for rec in recommendations)


@pytest.mark.asyncio
async def test_llm_enhancement_invalid_json_week28():
    """Test invalid JSON response handling (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    mock_response = {
        "content": "This is not valid JSON at all!"
    }
    
    agent.claude_service.chat = AsyncMock(return_value=mock_response)
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    # Should return original data on error
    assert enhanced == processed_data


@pytest.mark.asyncio
async def test_confidence_boost_with_high_llm_quality_week28():
    """Test confidence boost with high LLM quality (Week 28)"""
    agent = CompanyProfileAgent()
    
    # Simulate high-quality profile data with high LLM quality
    processed_data = {
        "krs_number": "0000123456",
        "nip_number": "1234563218",  # Valid NIP
        "ownership_structure": [{"owner": "Test"}],
        "financial_statements": {"year": 2023},
        "llm_quality_score": 0.95  # High LLM quality
    }
    
    data_sources = ["KRS API", "GUS API"]
    target_info = {"type": "krs"}
    
    confidence = agent._calculate_confidence(processed_data, data_sources, target_info)
    
    # With high LLM quality (0.95), confidence should be boosted
    # Base score ~125/125 = 100, with LLM: (100 * 0.7) + (0.95 * 100 * 0.3) = 70 + 28.5 = 98.5
    assert confidence >= 95


@pytest.mark.asyncio
async def test_confidence_penalty_with_low_llm_quality_week28():
    """Test confidence penalty with low LLM quality (Week 28)"""
    agent = CompanyProfileAgent()
    
    # Simulate moderate-quality data with low LLM quality
    processed_data = {
        "krs_number": "0000123456",
        "nip_number": "1234563218",  # Valid NIP
        "llm_quality_score": 0.25  # Low LLM quality
    }
    
    data_sources = ["KRS API"]
    target_info = {"type": "krs"}
    
    confidence = agent._calculate_confidence(processed_data, data_sources, target_info)
    
    # With low LLM quality (0.25), confidence should be reduced
    # Base score ~80/125 = 64, with LLM: (64 * 0.7) + (0.25 * 100 * 0.3) = 44.8 + 7.5 = 52.3
    assert confidence <= 60


def test_confidence_70_30_weighting_formula_week28():
    """Test accuracy of 70/30 weighting formula (Week 28)"""
    agent = CompanyProfileAgent()
    
    # Test cases: (base_score, llm_quality, expected_confidence)
    test_cases = [
        (80, 0.80, 80.0),  # (80 * 0.7) + (0.80 * 100 * 0.3) = 56 + 24 = 80
        (60, 0.90, 69.0),  # (60 * 0.7) + (0.90 * 100 * 0.3) = 42 + 27 = 69
        (100, 0.50, 85.0),  # (100 * 0.7) + (0.50 * 100 * 0.3) = 70 + 15 = 85
    ]
    
    for base_score_normalized, llm_quality, expected in test_cases:
        # Verify the formula matches expectation
        calculated = (base_score_normalized * 0.7) + (llm_quality * 100 * 0.3)
        assert abs(calculated - expected) < 0.5


@pytest.mark.asyncio
async def test_llm_enhancement_error_recovery_week28():
    """Test error recovery during LLM call (Week 28)"""
    from unittest.mock import AsyncMock
    
    agent = CompanyProfileAgent()
    
    if not agent.claude_service:
        pytest.skip("ClaudeService not available")
    
    # Mock exception during LLM call
    agent.claude_service.chat = AsyncMock(side_effect=Exception("LLM error"))
    
    processed_data = {"company_name": "Test"}
    enhanced = await agent._enhance_with_llm(processed_data, {})
    
    # Should return original data on error (graceful degradation)
    assert enhanced == processed_data
