"""
Unit Tests for FactCheckerAgent - Week 13 Implementation

Tests for fact verification, source credibility assessment, and multi-source validation.

Author: MI-Navigator Development Team
Created: 2026-01-25 (Week 13)
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from app.agents.fact_checker_agent import (
    FactCheckerAgent,
    FactCheckerOutput,
    Claim,
    Verification,
    Source,
    ClaimType,
    VerificationStatus,
    SourceType,
    CredibilityLevel,
    FactCheckerDomainKnowledge
)


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================

def test_claim_model_validation():
    """Test Claim model validation"""
    # Valid claim
    claim = Claim(
        claim_id="test_001",
        claim_text="Company revenue is 10M PLN",
        claim_type=ClaimType.FINANCIAL,
        claim_subject="Test Company",
        claimed_value="10000000",
        priority="high"
    )
    assert claim.claim_id == "test_001"
    assert claim.claim_type == ClaimType.FINANCIAL
    assert claim.priority == "high"

    # Test empty claim text validation
    with pytest.raises(ValueError):
        Claim(
            claim_id="test_002",
            claim_text="",
            claim_type=ClaimType.GENERAL,
            claim_subject="Test"
        )

    # Test claim text stripping
    claim_with_spaces = Claim(
        claim_id="test_003",
        claim_text="  Test claim with spaces  ",
        claim_type=ClaimType.GENERAL,
        claim_subject="Test"
    )
    assert claim_with_spaces.claim_text == "Test claim with spaces"


def test_source_model_validation():
    """Test Source model with credibility levels"""
    source = Source(
        source_name="KRS Registry",
        source_type=SourceType.OFFICIAL_REGISTRY,
        source_url="https://krs.gov.pl",
        credibility_score=95.0,
        credibility_level=CredibilityLevel.VERY_HIGH,
        retrieved_value="Test Value",
        is_primary_source=True,
        age_days=10,
        is_fresh=True
    )

    assert source.source_type == SourceType.OFFICIAL_REGISTRY
    assert source.credibility_score == 95.0
    assert source.credibility_level == CredibilityLevel.VERY_HIGH
    assert source.is_primary_source is True

    # Test credibility score bounds
    with pytest.raises(ValueError):
        Source(
            source_name="Invalid",
            source_type=SourceType.UNVERIFIED,
            credibility_score=150.0,  # Invalid: >100
            credibility_level=CredibilityLevel.VERY_LOW
        )


def test_verification_model_structure():
    """Test Verification model structure"""
    verification = Verification(
        claim_text="Test claim",
        claim_type=ClaimType.OPERATIONAL,
        verification_status=VerificationStatus.VERIFIED,
        confidence_score=85.5,
        total_sources_checked=3,
        reliability_assessment="reliable"
    )

    assert verification.claim_type == ClaimType.OPERATIONAL
    assert verification.verification_status == VerificationStatus.VERIFIED
    assert verification.confidence_score == 85.5
    assert verification.reliability_assessment == "reliable"
    assert len(verification.supporting_sources) == 0
    assert len(verification.contradicting_sources) == 0


def test_fact_checker_output_model():
    """Test FactCheckerOutput model"""
    output = FactCheckerOutput(
        target="NIP 1234567890",
        total_claims_checked=5,
        verified_claims_count=3,
        contradicted_claims_count=1,
        overall_confidence_score=72.5,
        confidence_score=72.5,
        data_sources=["KRS", "GUS", "Company Website"]
    )

    assert output.agent_type == "fact_checker"
    assert output.target == "NIP 1234567890"
    assert output.verified_claims_count == 3
    assert output.overall_confidence_score == 72.5
    assert len(output.data_sources) == 3


# ============================================================================
# DOMAIN KNOWLEDGE TESTS
# ============================================================================

def test_source_credibility_scores():
    """Test source credibility scoring system"""
    domain = FactCheckerDomainKnowledge()

    # Official registries should have highest credibility
    assert domain.SOURCE_CREDIBILITY_SCORES[SourceType.OFFICIAL_REGISTRY] == 95
    assert domain.SOURCE_CREDIBILITY_SCORES[SourceType.FINANCIAL_REPORT] == 85
    assert domain.SOURCE_CREDIBILITY_SCORES[SourceType.COMPANY_WEBSITE] == 60
    assert domain.SOURCE_CREDIBILITY_SCORES[SourceType.SOCIAL_MEDIA] == 30
    assert domain.SOURCE_CREDIBILITY_SCORES[SourceType.UNVERIFIED] == 15

    # All scores should be 0-100
    for score in domain.SOURCE_CREDIBILITY_SCORES.values():
        assert 0 <= score <= 100


def test_freshness_thresholds():
    """Test data freshness thresholds"""
    domain = FactCheckerDomainKnowledge()

    assert domain.FRESHNESS_THRESHOLDS[ClaimType.FINANCIAL] == 365
    assert domain.FRESHNESS_THRESHOLDS[ClaimType.OPERATIONAL] == 180
    assert domain.FRESHNESS_THRESHOLDS[ClaimType.MARKET] == 90
    assert domain.FRESHNESS_THRESHOLDS[ClaimType.LEGAL] == 730


def test_contradiction_thresholds():
    """Test contradiction detection thresholds"""
    domain = FactCheckerDomainKnowledge()

    # Financial claims allow 10% variance
    assert domain.CONTRADICTION_THRESHOLD[ClaimType.FINANCIAL] == 10.0

    # Legal and ownership must match exactly
    assert domain.CONTRADICTION_THRESHOLD[ClaimType.LEGAL] == 0.0
    assert domain.CONTRADICTION_THRESHOLD[ClaimType.OWNERSHIP] == 0.0

    # Market estimates allow 15% variance
    assert domain.CONTRADICTION_THRESHOLD[ClaimType.MARKET] == 15.0


# ============================================================================
# AGENT FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test FactCheckerAgent initialization"""
    agent = FactCheckerAgent()
    assert agent.domain_knowledge is not None
    assert isinstance(agent.domain_knowledge, FactCheckerDomainKnowledge)


@pytest.mark.asyncio
async def test_agent_execute_no_claims():
    """Test agent execution with no claims"""
    agent = FactCheckerAgent()
    result = await agent.execute(query="NIP 1234567890", context={})

    assert isinstance(result, FactCheckerOutput)
    assert result.target == "NIP 1234567890"
    assert result.total_claims_checked == 0
    assert len(result.warnings) > 0
    assert "No claims provided" in result.warnings[0]


@pytest.mark.asyncio
async def test_agent_execute_with_single_claim():
    """Test agent execution with a single claim"""
    agent = FactCheckerAgent()

    context = {
        "claims": [
            {
                "text": "Company has 50 employees",
                "type": "operational",
                "subject": "Test Company",
                "value": "50",
                "priority": "high"
            }
        ]
    }

    result = await agent.execute(query="NIP 1234567890", context=context)

    assert result.total_claims_checked == 1
    assert len(result.claims) == 1
    assert len(result.verifications) == 1
    assert result.claims[0].claim_type == ClaimType.OPERATIONAL
    assert result.verifications[0].claim_text == "Company has 50 employees"


@pytest.mark.asyncio
async def test_agent_execute_with_multiple_claims():
    """Test agent execution with multiple claims"""
    agent = FactCheckerAgent()

    context = {
        "claims": [
            {
                "text": "Revenue is 10M PLN",
                "type": "financial",
                "subject": "Test Company",
                "value": "10000000"
            },
            {
                "text": "Company employs 100 people",
                "type": "operational",
                "subject": "Test Company",
                "value": "100"
            },
            {
                "text": "Registered in Warsaw",
                "type": "legal",
                "subject": "Test Company",
                "value": "Warsaw"
            }
        ]
    }

    result = await agent.execute(query="KRS 0000123456", context=context)

    assert result.total_claims_checked == 3
    assert len(result.claims) == 3
    assert len(result.verifications) == 3
    assert result.overall_confidence_score > 0


@pytest.mark.asyncio
async def test_claim_creation():
    """Test _create_claim method"""
    agent = FactCheckerAgent()

    claim_data = {
        "text": "Test claim",
        "type": "financial",
        "subject": "Test Company",
        "value": "12345",
        "source": "Annual Report",
        "priority": "high"
    }

    claim = agent._create_claim(claim_data, 0)

    assert claim.claim_id == "claim_0"
    assert claim.claim_text == "Test claim"
    assert claim.claim_type == ClaimType.FINANCIAL
    assert claim.claim_subject == "Test Company"
    assert claim.claimed_value == "12345"
    assert claim.priority == "high"


@pytest.mark.asyncio
async def test_source_collection():
    """Test _collect_sources method"""
    agent = FactCheckerAgent()

    claim = Claim(
        claim_id="test_001",
        claim_text="Company is registered",
        claim_type=ClaimType.LEGAL,
        claim_subject="Test Company",
        claimed_value="Active"
    )

    sources = await agent._collect_sources(claim, "NIP 1234567890")

    assert len(sources) >= 1
    assert all(isinstance(s, Source) for s in sources)
    assert any(s.source_type == SourceType.OFFICIAL_REGISTRY for s in sources)


def test_source_supports_claim():
    """Test _source_supports_claim logic"""
    agent = FactCheckerAgent()

    source = Source(
        source_name="Test Source",
        source_type=SourceType.OFFICIAL_REGISTRY,
        credibility_score=90.0,
        credibility_level=CredibilityLevel.VERY_HIGH,
        retrieved_value="100"
    )

    claim = Claim(
        claim_id="test_001",
        claim_text="Company has 100 employees",
        claim_type=ClaimType.OPERATIONAL,
        claim_subject="Test Company",
        claimed_value="100"
    )

    # Should support when values match
    assert agent._source_supports_claim(source, claim) is True

    # Should not support when values differ
    claim.claimed_value = "200"
    assert agent._source_supports_claim(source, claim) is False


def test_source_contradicts_claim():
    """Test _source_contradicts_claim logic"""
    agent = FactCheckerAgent()

    # High credibility source with different value
    source = Source(
        source_name="KRS",
        source_type=SourceType.OFFICIAL_REGISTRY,
        credibility_score=95.0,
        credibility_level=CredibilityLevel.VERY_HIGH,
        retrieved_value="50"
    )

    claim = Claim(
        claim_id="test_001",
        claim_text="Employee count is 100",
        claim_type=ClaimType.OPERATIONAL,
        claim_subject="Test Company",
        claimed_value="100"
    )

    # Should contradict when high credibility + different values
    assert agent._source_contradicts_claim(source, claim) is True

    # Low credibility source should not contradict
    source.credibility_score = 30.0
    assert agent._source_contradicts_claim(source, claim) is False


def test_verification_confidence_calculation():
    """Test _calculate_verification_confidence method"""
    agent = FactCheckerAgent()

    # Verified claim with high credibility sources
    verification = Verification(
        claim_text="Test claim",
        claim_type=ClaimType.FINANCIAL,
        verification_status=VerificationStatus.VERIFIED,
        confidence_score=0.0,
        reliability_assessment="unknown"
    )

    verification.supporting_sources = [
        Source(
            source_name="KRS",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH
        ),
        Source(
            source_name="Financial Report",
            source_type=SourceType.FINANCIAL_REPORT,
            credibility_score=85.0,
            credibility_level=CredibilityLevel.HIGH
        )
    ]

    confidence = agent._calculate_verification_confidence(verification)

    assert 70.0 <= confidence <= 100.0  # High confidence for verified claims


def test_reliability_assessment():
    """Test _assess_reliability method"""
    agent = FactCheckerAgent()

    verification = Verification(
        claim_text="Test",
        claim_type=ClaimType.GENERAL,
        verification_status=VerificationStatus.VERIFIED,
        confidence_score=85.0,
        reliability_assessment="unknown"
    )

    # High confidence -> reliable
    assert agent._assess_reliability(verification) == "reliable"

    # Medium confidence -> partially_reliable
    verification.confidence_score = 60.0
    assert agent._assess_reliability(verification) == "partially_reliable"

    # Low confidence -> unreliable
    verification.confidence_score = 35.0
    assert agent._assess_reliability(verification) == "unreliable"

    # Very low confidence -> unknown
    verification.confidence_score = 15.0
    assert agent._assess_reliability(verification) == "unknown"


def test_overall_metrics_calculation():
    """Test _calculate_overall_metrics method"""
    agent = FactCheckerAgent()

    output = FactCheckerOutput(
        target="NIP 1234567890",
        confidence_score=0.0
    )

    # Add verifications
    output.verifications = [
        Verification(
            claim_text="Claim 1",
            claim_type=ClaimType.FINANCIAL,
            verification_status=VerificationStatus.VERIFIED,
            confidence_score=90.0,
            reliability_assessment="reliable"
        ),
        Verification(
            claim_text="Claim 2",
            claim_type=ClaimType.OPERATIONAL,
            verification_status=VerificationStatus.CONTRADICTED,
            confidence_score=20.0,
            reliability_assessment="unreliable"
        ),
        Verification(
            claim_text="Claim 3",
            claim_type=ClaimType.GENERAL,
            verification_status=VerificationStatus.UNVERIFIED,
            confidence_score=30.0,
            reliability_assessment="unreliable"
        )
    ]

    # Add claims to match verifications
    output.claims = [
        Claim(
            claim_id="claim_0",
            claim_text="Claim 1",
            claim_type=ClaimType.FINANCIAL,
            claim_subject="Test Company"
        ),
        Claim(
            claim_id="claim_1",
            claim_text="Claim 2",
            claim_type=ClaimType.OPERATIONAL,
            claim_subject="Test Company"
        ),
        Claim(
            claim_id="claim_2",
            claim_text="Claim 3",
            claim_type=ClaimType.GENERAL,
            claim_subject="Test Company"
        )
    ]

    # Add sources to verifications
    output.verifications[0].supporting_sources = [
        Source(
            source_name="KRS",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            is_primary_source=True,
            is_fresh=True
        )
    ]

    output.verifications[1].contradicting_sources = [
        Source(
            source_name="Website",
            source_type=SourceType.COMPANY_WEBSITE,
            credibility_score=60.0,
            credibility_level=CredibilityLevel.MEDIUM,
            is_fresh=True
        )
    ]

    result = agent._calculate_overall_metrics(output)

    assert result.total_claims_checked == 3
    assert result.verified_claims_count == 1
    assert result.contradicted_claims_count == 1
    assert result.unverified_claims_count == 1
    assert result.overall_confidence_score > 0
    assert result.confidence_score == result.overall_confidence_score
    assert result.primary_sources_used == 1
    assert len(result.critical_issues) > 0  # Should flag contradicted claims


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling with invalid input"""
    agent = FactCheckerAgent()

    # Test with invalid claim data (should handle gracefully)
    context = {
        "claims": [
            {
                # Missing required fields
                "text": "",  # Empty text
                "type": "financial"
            }
        ]
    }

    result = await agent.execute(query="Test", context=context)

    # Agent should handle errors and return output with error info
    assert isinstance(result, FactCheckerOutput)
    assert len(result.errors) > 0 or len(result.warnings) > 0


# ============================================================================
# ENUM TESTS
# ============================================================================

def test_claim_type_enum():
    """Test ClaimType enum values"""
    assert ClaimType.FINANCIAL == "financial"
    assert ClaimType.OPERATIONAL == "operational"
    assert ClaimType.LEGAL == "legal"
    assert ClaimType.OWNERSHIP == "ownership"
    assert ClaimType.MARKET == "market"
    assert ClaimType.GENERAL == "general"


def test_verification_status_enum():
    """Test VerificationStatus enum values"""
    assert VerificationStatus.VERIFIED == "verified"
    assert VerificationStatus.PARTIALLY_VERIFIED == "partially_verified"
    assert VerificationStatus.UNVERIFIED == "unverified"
    assert VerificationStatus.CONTRADICTED == "contradicted"
    assert VerificationStatus.INSUFFICIENT_DATA == "insufficient_data"


def test_source_type_enum():
    """Test SourceType enum values"""
    assert SourceType.OFFICIAL_REGISTRY == "official_registry"
    assert SourceType.FINANCIAL_REPORT == "financial_report"
    assert SourceType.COMPANY_WEBSITE == "company_website"
    assert SourceType.SOCIAL_MEDIA == "social_media"


def test_credibility_level_enum():
    """Test CredibilityLevel enum values"""
    assert CredibilityLevel.VERY_HIGH == "very_high"
    assert CredibilityLevel.HIGH == "high"
    assert CredibilityLevel.MEDIUM == "medium"
    assert CredibilityLevel.LOW == "low"
    assert CredibilityLevel.VERY_LOW == "very_low"


# ============================================================================
# WEEK 14: ADVANCED ANALYSIS TESTS
# ============================================================================

def test_cross_reference_validation():
    """Test cross-reference validation with multiple sources (Week 14)"""
    agent = FactCheckerAgent()
    
    # Create sources with agreeing values
    sources = [
        Source(
            source_name="Source 1",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            retrieved_value="100"
        ),
        Source(
            source_name="Source 2",
            source_type=SourceType.FINANCIAL_REPORT,
            credibility_score=85.0,
            credibility_level=CredibilityLevel.HIGH,
            retrieved_value="100"
        ),
        Source(
            source_name="Source 3",
            source_type=SourceType.COMPANY_WEBSITE,
            credibility_score=60.0,
            credibility_level=CredibilityLevel.MEDIUM,
            retrieved_value="95"
        )
    ]
    
    claim = Claim(
        claim_id="test_001",
        claim_text="Employee count is 100",
        claim_type=ClaimType.OPERATIONAL,
        claim_subject="Test Company"
    )
    
    result = agent._validate_cross_references(sources, claim)
    
    assert result["has_cross_references"] is True
    assert result["agreement_percentage"] > 0
    assert len(result["consistent_sources"]) == 2  # 2 sources agree on "100"
    assert result["total_unique_values"] == 2  # "100" and "95"
    assert len(result["discrepancies"]) > 0  # One source disagrees


def test_temporal_consistency_checking():
    """Test temporal consistency checking (Week 14)"""
    agent = FactCheckerAgent()
    
    # Create sources with different freshness
    sources = [
        Source(
            source_name="Fresh Source",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            age_days=30,
            is_fresh=True
        ),
        Source(
            source_name="Stale Source",
            source_type=SourceType.COMPANY_WEBSITE,
            credibility_score=60.0,
            credibility_level=CredibilityLevel.MEDIUM,
            age_days=400,
            is_fresh=False
        )
    ]
    
    claim = Claim(
        claim_id="test_001",
        claim_text="Company data",
        claim_type=ClaimType.FINANCIAL,
        claim_subject="Test Company"
    )
    
    result = agent._check_temporal_consistency(sources, claim)
    
    assert "freshness_score" in result
    assert result["fresh_sources"] == 1
    assert result["stale_sources"] == 1
    assert len(result["temporal_issues"]) > 0  # Should flag stale source


def test_detailed_contradiction_detection():
    """Test enhanced contradiction detection (Week 14)"""
    agent = FactCheckerAgent()
    
    supporting_sources = [
        Source(
            source_name="Support 1",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            retrieved_value="100"
        )
    ]
    
    contradicting_sources = [
        Source(
            source_name="Contradiction 1",
            source_type=SourceType.FINANCIAL_REPORT,
            credibility_score=85.0,
            credibility_level=CredibilityLevel.HIGH,
            retrieved_value="90"
        )
    ]
    
    claim = Claim(
        claim_id="test_001",
        claim_text="Employee count is 100",
        claim_type=ClaimType.OPERATIONAL,
        claim_subject="Test Company"
    )
    
    result = agent._detect_detailed_contradictions(
        supporting_sources,
        contradicting_sources,
        claim
    )
    
    assert result["has_contradictions"] is True
    assert result["contradiction_severity"] in ["high", "medium", "low"]
    assert result["high_credibility_contradictions"] == 1  # 1 source with credibility >= 70
    assert len(result["contradiction_details"]) == 1
    assert "resolution_confidence" in result


def test_enhanced_confidence_scoring():
    """Test enhanced confidence scoring algorithm (Week 14)"""
    agent = FactCheckerAgent()
    
    # Create verification with supporting sources
    verification = Verification(
        claim_text="Test claim",
        claim_type=ClaimType.FINANCIAL,
        verification_status=VerificationStatus.VERIFIED,
        confidence_score=0.0,
        reliability_assessment="unknown"
    )
    
    verification.supporting_sources = [
        Source(
            source_name="KRS",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            retrieved_value="100"
        ),
        Source(
            source_name="GUS",
            source_type=SourceType.OFFICIAL_REGISTRY,
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            retrieved_value="100"
        )
    ]
    
    # Simulate cross-reference analysis (high agreement)
    cross_ref_analysis = {
        "has_cross_references": True,
        "agreement_percentage": 100.0
    }
    
    # Simulate temporal analysis (consistent)
    temporal_analysis = {
        "is_temporally_consistent": True,
        "freshness_score": 100.0
    }
    
    # Simulate contradiction analysis (no contradictions)
    contradiction_analysis = {
        "has_contradictions": False,
        "contradiction_severity": "none"
    }
    
    confidence = agent._calculate_enhanced_confidence(
        verification,
        cross_ref_analysis,
        temporal_analysis,
        contradiction_analysis
    )
    
    # Enhanced confidence should be higher than base confidence
    base_confidence = agent._calculate_verification_confidence(verification)
    assert confidence > base_confidence
    assert confidence >= 85.0  # Should be high with perfect conditions


@pytest.mark.asyncio
async def test_week14_integration():
    """Integration test for Week 14 advanced analysis features"""
    agent = FactCheckerAgent()
    
    # Test with comprehensive context
    context = {
        "claims": [
            {
                "text": "Company has 100 employees",
                "type": "operational",
                "subject": "Test Company",
                "value": "100",
                "priority": "high"
            }
        ]
    }
    
    result = await agent.execute(query="KRS 0000123456", context=context)
    
    # Verify Week 14 enhancements are working
    assert result.total_claims_checked == 1
    assert len(result.verifications) == 1
    
    verification = result.verifications[0]
    
    # Should have enhanced confidence scoring applied
    assert verification.confidence_score >= 0.0
    assert verification.confidence_score <= 100.0
    
    # Should have notes about analysis (if applicable)
    # Notes may include temporal issues or contradiction severity
    assert isinstance(verification.notes, list)
    assert isinstance(verification.discrepancies, list)
