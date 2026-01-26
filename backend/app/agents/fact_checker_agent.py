"""
Fact Checker Agent

Autonomous agent for multi-source fact verification and credibility assessment.
Verifies claims through cross-referencing multiple data sources and assigns confidence scores.

Week 13 Implementation: Foundation agent for fact verification.
Week 14 Enhancement: Advanced analysis with cross-reference validation, temporal consistency,
                     enhanced contradiction detection, and improved confidence scoring.

Use case: "Verify company revenue claim of 10M PLN for Company XYZ"
         "Check accuracy of employee count reported as 50 for NIP 1234567890"
         "Validate ownership structure claims for KRS 0000123456"
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class ClaimType(str, Enum):
    """Types of claims that can be verified"""
    FINANCIAL = "financial"  # Revenue, profit, assets
    OPERATIONAL = "operational"  # Employee count, office locations
    LEGAL = "legal"  # Registration status, legal form
    OWNERSHIP = "ownership"  # Shareholders, board members
    MARKET = "market"  # Market share, customer count
    GENERAL = "general"  # Other factual claims


class VerificationStatus(str, Enum):
    """Verification outcome"""
    VERIFIED = "verified"  # Confirmed by multiple reliable sources
    PARTIALLY_VERIFIED = "partially_verified"  # Some sources confirm
    UNVERIFIED = "unverified"  # No sources confirm
    CONTRADICTED = "contradicted"  # Sources contradict the claim
    INSUFFICIENT_DATA = "insufficient_data"  # Not enough data to verify


class SourceType(str, Enum):
    """Types of information sources"""
    OFFICIAL_REGISTRY = "official_registry"  # KRS, CEIDG, GUS, REGON
    FINANCIAL_REPORT = "financial_report"  # Audited financial statements
    PUBLIC_FILING = "public_filing"  # Court filings, official announcements
    COMPANY_WEBSITE = "company_website"  # Official company information
    INDUSTRY_MEDIA = "industry_media"  # Trade publications, news
    SOCIAL_MEDIA = "social_media"  # LinkedIn, company social profiles
    THIRD_PARTY_DATABASE = "third_party_database"  # Business databases
    UNVERIFIED = "unverified"  # Forums, blogs, user content


class CredibilityLevel(str, Enum):
    """Source credibility classification"""
    VERY_HIGH = "very_high"  # 90-100: Official registries
    HIGH = "high"  # 70-89: Audited reports
    MEDIUM = "medium"  # 50-69: Company websites, industry media
    LOW = "low"  # 30-49: Social media, third-party databases
    VERY_LOW = "very_low"  # 0-29: Unverified sources


# ============================================================================
# DOMAIN KNOWLEDGE
# ============================================================================

class FactCheckerDomainKnowledge:
    """
    Domain knowledge for fact verification and source credibility assessment.
    Based on journalism fact-checking standards and information science best practices.
    """

    # Source credibility scores (0-100)
    SOURCE_CREDIBILITY_SCORES = {
        SourceType.OFFICIAL_REGISTRY: 95,  # KRS, GUS, REGON - highest credibility
        SourceType.FINANCIAL_REPORT: 85,  # Audited statements
        SourceType.PUBLIC_FILING: 75,  # Court documents
        SourceType.COMPANY_WEBSITE: 60,  # Official but potentially biased
        SourceType.INDUSTRY_MEDIA: 55,  # Professional journalism
        SourceType.THIRD_PARTY_DATABASE: 45,  # Aggregated data
        SourceType.SOCIAL_MEDIA: 30,  # User-generated, unverified
        SourceType.UNVERIFIED: 15,  # Lowest credibility
    }

    # Source freshness decay (days)
    FRESHNESS_THRESHOLDS = {
        ClaimType.FINANCIAL: 365,  # Financial data valid for 1 year
        ClaimType.OPERATIONAL: 180,  # Operational data valid for 6 months
        ClaimType.LEGAL: 730,  # Legal status valid for 2 years
        ClaimType.OWNERSHIP: 365,  # Ownership changes annually
        ClaimType.MARKET: 90,  # Market data valid for 3 months
        ClaimType.GENERAL: 365,  # General claims valid for 1 year
    }

    # Minimum sources required for verification
    MIN_SOURCES_FOR_VERIFICATION = {
        VerificationStatus.VERIFIED: 2,  # At least 2 sources must agree
        VerificationStatus.PARTIALLY_VERIFIED: 1,
        VerificationStatus.UNVERIFIED: 0,
    }

    # Contradiction detection threshold (% difference)
    CONTRADICTION_THRESHOLD = {
        ClaimType.FINANCIAL: 10.0,  # 10% difference in financial data
        ClaimType.OPERATIONAL: 5.0,  # 5% difference in operational metrics
        ClaimType.LEGAL: 0.0,  # Legal data must match exactly
        ClaimType.OWNERSHIP: 0.0,  # Ownership must match exactly
        ClaimType.MARKET: 15.0,  # 15% difference in market estimates
        ClaimType.GENERAL: 10.0,  # 10% difference for general claims
    }


# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

class Source(BaseModel):
    """Individual information source"""
    source_name: str = Field(..., description="Name of the source (e.g., 'KRS', 'Company Website')")
    source_type: SourceType
    source_url: Optional[str] = None
    credibility_score: float = Field(..., ge=0, le=100, description="Credibility score 0-100")
    credibility_level: CredibilityLevel

    # Data retrieved
    retrieved_value: Optional[str] = Field(None, description="Value found in this source")
    retrieved_date: datetime = Field(default_factory=datetime.utcnow)

    # Source metadata
    publication_date: Optional[datetime] = None
    author: Optional[str] = None
    is_primary_source: bool = False

    # Freshness
    age_days: Optional[int] = None
    is_fresh: bool = True

    class Config:
        use_enum_values = True


class Verification(BaseModel):
    """Verification result for a specific claim"""
    claim_text: str = Field(..., description="Original claim being verified")
    claim_type: ClaimType

    # Verification outcome
    verification_status: VerificationStatus
    confidence_score: float = Field(..., ge=0, le=100, description="Overall confidence 0-100")

    # Supporting evidence
    supporting_sources: List[Source] = Field(default_factory=list)
    contradicting_sources: List[Source] = Field(default_factory=list)
    total_sources_checked: int = 0

    # Analysis
    verified_value: Optional[str] = Field(None, description="Verified value if confirmed")
    discrepancies: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

    # Recommendations
    reliability_assessment: str = Field(..., pattern="^(reliable|partially_reliable|unreliable|unknown)$")
    recommended_action: Optional[str] = None

    class Config:
        use_enum_values = True


class Claim(BaseModel):
    """Individual claim to be fact-checked"""
    claim_id: str = Field(..., description="Unique identifier for the claim")
    claim_text: str = Field(..., min_length=3, description="The claim to be verified")
    claim_type: ClaimType
    claim_subject: str = Field(..., description="Subject of the claim (e.g., company name, NIP)")

    # Claim metadata
    claimed_value: Optional[str] = None
    claim_source: Optional[str] = None  # Where the claim was made
    claim_date: datetime = Field(default_factory=datetime.utcnow)

    # Priority
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")

    class Config:
        use_enum_values = True

    @field_validator('claim_text')
    @classmethod
    def validate_claim_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Claim text cannot be empty")
        return v.strip()


class FactCheckerOutput(BaseModel):
    """Structured output for FactCheckerAgent"""
    agent_type: str = "fact_checker"
    target: str = Field(..., description="Target company or entity identifier")

    # Claims analyzed
    claims: List[Claim] = Field(default_factory=list)
    verifications: List[Verification] = Field(default_factory=list)
    total_claims_checked: int = 0

    # Overall assessment
    overall_confidence_score: float = Field(0.0, ge=0, le=100)
    verified_claims_count: int = 0
    contradicted_claims_count: int = 0
    unverified_claims_count: int = 0

    # Data quality
    primary_sources_used: int = 0
    average_source_credibility: float = Field(0.0, ge=0, le=100)
    data_freshness_score: float = Field(0.0, ge=0, le=100)

    # Issues and warnings
    critical_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Agent metadata
    confidence_score: float = Field(..., ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "fact_checker",
                "target": "NIP 1234567890",
                "total_claims_checked": 3,
                "verified_claims_count": 2,
                "overall_confidence_score": 78.5,
                "confidence_score": 78.5,
                "data_sources": ["KRS API", "GUS", "Company Website"],
                "last_updated": "2026-01-25T14:00:00Z"
            }
        }


# ============================================================================
# AGENT CLASS
# ============================================================================

class FactCheckerAgent:
    """
    Autonomous agent for multi-source fact verification.

    Capabilities:
    - Multi-source claim verification
    - Source credibility assessment
    - Contradiction detection
    - Confidence scoring (0-100)
    - Freshness validation

    Example usage:
        agent = FactCheckerAgent()
        result = await agent.execute(
            query="NIP 1234567890",
            context={"claims": [{"text": "Revenue is 10M PLN", "type": "financial"}]}
        )
    """

    def __init__(self):
        self.domain_knowledge = FactCheckerDomainKnowledge()
        logger.info("FactCheckerAgent initialized")

    async def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> FactCheckerOutput:
        """
        Execute fact-checking analysis for the given query.

        Args:
            query: Company identifier (NIP, KRS, or company name)
            context: Optional context with claims to verify

        Returns:
            FactCheckerOutput with verification results
        """
        logger.info(f"FactCheckerAgent executing for query: {query}")

        try:
            # Extract context parameters
            context = context or {}
            claims_to_verify = context.get("claims", [])

            # Initialize output
            output = FactCheckerOutput(
                target=query,
                confidence_score=0.0
            )

            # If no claims provided, return empty result
            if not claims_to_verify:
                output.warnings.append("No claims provided for verification")
                logger.warning(f"No claims to verify for {query}")
                return output

            # Process each claim
            for idx, claim_data in enumerate(claims_to_verify):
                claim = self._create_claim(claim_data, idx)
                verification = await self._verify_claim(claim, query)

                output.claims.append(claim)
                output.verifications.append(verification)

            # Calculate overall metrics
            output = self._calculate_overall_metrics(output)

            logger.info(
                f"FactChecker completed for {query}: "
                f"{output.verified_claims_count}/{output.total_claims_checked} verified, "
                f"confidence {output.confidence_score:.1f}%"
            )

            return output

        except Exception as e:
            logger.error(f"FactCheckerAgent error for {query}: {str(e)}", exc_info=True)
            return FactCheckerOutput(
                target=query,
                confidence_score=0.0,
                errors=[f"Agent execution failed: {str(e)}"]
            )

    def _create_claim(self, claim_data: Dict[str, Any], index: int) -> Claim:
        """Create a Claim object from dictionary data"""
        return Claim(
            claim_id=f"claim_{index}",
            claim_text=claim_data.get("text", ""),
            claim_type=ClaimType(claim_data.get("type", "general")),
            claim_subject=claim_data.get("subject", ""),
            claimed_value=claim_data.get("value"),
            claim_source=claim_data.get("source"),
            priority=claim_data.get("priority", "medium")
        )

    async def _verify_claim(self, claim: Claim, target: str) -> Verification:
        """
        Verify a single claim against multiple sources.

        Args:
            claim: Claim to verify
            target: Target identifier

        Returns:
            Verification result
        """
        verification = Verification(
            claim_text=claim.claim_text,
            claim_type=claim.claim_type,
            verification_status=VerificationStatus.INSUFFICIENT_DATA,
            confidence_score=0.0,
            reliability_assessment="unknown"
        )

        # Collect sources (placeholder - will be implemented with real integrations)
        sources = await self._collect_sources(claim, target)
        verification.total_sources_checked = len(sources)

        if not sources:
            verification.notes.append("No sources found to verify this claim")
            return verification

        # Analyze sources
        for source in sources:
            # Check if source supports or contradicts the claim
            if self._source_supports_claim(source, claim):
                verification.supporting_sources.append(source)
            elif self._source_contradicts_claim(source, claim):
                verification.contradicting_sources.append(source)

        # Determine verification status
        verification = self._determine_verification_status(verification, claim)

        # Week 14: Perform advanced analysis
        all_sources = verification.supporting_sources + verification.contradicting_sources

        # Cross-reference validation
        cross_ref_analysis = self._validate_cross_references(all_sources, claim)
        if cross_ref_analysis.get("discrepancies"):
            for discrepancy in cross_ref_analysis["discrepancies"]:
                verification.discrepancies.append(discrepancy)

        # Temporal consistency checking
        temporal_analysis = self._check_temporal_consistency(all_sources, claim)
        if not temporal_analysis.get("is_temporally_consistent"):
            for issue in temporal_analysis.get("temporal_issues", []):
                verification.notes.append(f"Temporal issue: {issue}")

        # Enhanced contradiction detection
        contradiction_analysis = self._detect_detailed_contradictions(
            verification.supporting_sources,
            verification.contradicting_sources,
            claim
        )
        if contradiction_analysis.get("has_contradictions"):
            verification.notes.append(
                f"Contradiction severity: {contradiction_analysis['contradiction_severity']}"
            )

        # Calculate enhanced confidence score (Week 14)
        verification.confidence_score = self._calculate_enhanced_confidence(
            verification,
            cross_ref_analysis,
            temporal_analysis,
            contradiction_analysis
        )

        # Assess reliability
        verification.reliability_assessment = self._assess_reliability(verification)

        # Add recommendation
        verification.recommended_action = self._generate_recommendation(verification)

        return verification

    async def _collect_sources(self, claim: Claim, target: str) -> List[Source]:
        """
        Collect sources relevant to the claim.
        Week 13: Placeholder implementation returning mock sources.
        Week 14: Will integrate with real data sources (KRS, GUS, etc.)
        """
        sources = []

        # Mock source 1: Official Registry (KRS)
        if claim.claim_type in [ClaimType.LEGAL, ClaimType.OWNERSHIP, ClaimType.OPERATIONAL]:
            sources.append(Source(
                source_name="KRS (Court Registry)",
                source_type=SourceType.OFFICIAL_REGISTRY,
                source_url=f"https://krs-api.gov.pl/companies/{target}",
                credibility_score=self.domain_knowledge.SOURCE_CREDIBILITY_SCORES[SourceType.OFFICIAL_REGISTRY],
                credibility_level=CredibilityLevel.VERY_HIGH,
                retrieved_value=claim.claimed_value,
                is_primary_source=True,
                age_days=30,
                is_fresh=True
            ))

        # Mock source 2: Company Website
        sources.append(Source(
            source_name="Company Official Website",
            source_type=SourceType.COMPANY_WEBSITE,
            credibility_score=self.domain_knowledge.SOURCE_CREDIBILITY_SCORES[SourceType.COMPANY_WEBSITE],
            credibility_level=CredibilityLevel.MEDIUM,
            retrieved_value=claim.claimed_value,
            age_days=15,
            is_fresh=True
        ))

        return sources

    def _source_supports_claim(self, source: Source, claim: Claim) -> bool:
        """Check if source supports the claim"""
        # Simple placeholder: if retrieved value matches claimed value
        if source.retrieved_value and claim.claimed_value:
            return str(source.retrieved_value).strip().lower() == str(claim.claimed_value).strip().lower()
        return False

    def _source_contradicts_claim(self, source: Source, claim: Claim) -> bool:
        """Check if source contradicts the claim"""
        # Placeholder: if values are different and credibility is high
        if source.retrieved_value and claim.claimed_value:
            values_different = str(source.retrieved_value).strip().lower() != str(claim.claimed_value).strip().lower()
            high_credibility = source.credibility_score >= 70
            return values_different and high_credibility
        return False

    def _determine_verification_status(self, verification: Verification, claim: Claim) -> Verification:
        """Determine the verification status based on sources"""
        supporting_count = len(verification.supporting_sources)
        contradicting_count = len(verification.contradicting_sources)

        if contradicting_count > 0:
            verification.verification_status = VerificationStatus.CONTRADICTED
            verification.discrepancies.append(
                f"{contradicting_count} source(s) contradict the claim"
            )
        elif supporting_count >= 2:
            verification.verification_status = VerificationStatus.VERIFIED
            # Use most credible supporting source value
            if verification.supporting_sources:
                best_source = max(verification.supporting_sources, key=lambda s: s.credibility_score)
                verification.verified_value = best_source.retrieved_value
        elif supporting_count == 1:
            verification.verification_status = VerificationStatus.PARTIALLY_VERIFIED
            verification.notes.append("Only one source confirms this claim")
        else:
            verification.verification_status = VerificationStatus.UNVERIFIED
            verification.notes.append("No sources confirm this claim")

        return verification

    def _calculate_verification_confidence(self, verification: Verification) -> float:
        """Calculate confidence score for verification"""
        if verification.verification_status == VerificationStatus.INSUFFICIENT_DATA:
            return 0.0

        # Base score on verification status
        status_scores = {
            VerificationStatus.VERIFIED: 80.0,
            VerificationStatus.PARTIALLY_VERIFIED: 50.0,
            VerificationStatus.UNVERIFIED: 20.0,
            VerificationStatus.CONTRADICTED: 10.0,
        }
        base_score = status_scores.get(verification.verification_status, 0.0)

        # Boost based on source credibility
        if verification.supporting_sources:
            avg_credibility = sum(s.credibility_score for s in verification.supporting_sources) / len(verification.supporting_sources)
            credibility_boost = (avg_credibility / 100) * 20  # Up to +20 points
            base_score += credibility_boost

        # Penalty for contradictions
        if verification.contradicting_sources:
            contradiction_penalty = len(verification.contradicting_sources) * 10
            base_score -= contradiction_penalty

        return max(0.0, min(100.0, base_score))

    def _assess_reliability(self, verification: Verification) -> str:
        """Assess overall reliability"""
        if verification.confidence_score >= 75:
            return "reliable"
        elif verification.confidence_score >= 50:
            return "partially_reliable"
        elif verification.confidence_score >= 25:
            return "unreliable"
        else:
            return "unknown"

    def _generate_recommendation(self, verification: Verification) -> str:
        """Generate action recommendation"""
        if verification.verification_status == VerificationStatus.VERIFIED:
            return "Claim verified - can be used with confidence"
        elif verification.verification_status == VerificationStatus.PARTIALLY_VERIFIED:
            return "Claim partially verified - seek additional sources"
        elif verification.verification_status == VerificationStatus.CONTRADICTED:
            return "Claim contradicted - do not use without clarification"
        elif verification.verification_status == VerificationStatus.UNVERIFIED:
            return "Claim unverified - treat as unconfirmed"
        else:
            return "Insufficient data - gather more information"

    def _calculate_overall_metrics(self, output: FactCheckerOutput) -> FactCheckerOutput:
        """Calculate overall metrics for the fact-checking session"""
        output.total_claims_checked = len(output.claims)

        # Count verifications by status
        for verification in output.verifications:
            if verification.verification_status == VerificationStatus.VERIFIED:
                output.verified_claims_count += 1
            elif verification.verification_status == VerificationStatus.CONTRADICTED:
                output.contradicted_claims_count += 1
            elif verification.verification_status == VerificationStatus.UNVERIFIED:
                output.unverified_claims_count += 1

        # Calculate overall confidence
        if output.verifications:
            total_confidence = sum(v.confidence_score for v in output.verifications)
            output.overall_confidence_score = total_confidence / len(output.verifications)
            output.confidence_score = output.overall_confidence_score

        # Calculate source metrics
        all_sources = []
        for verification in output.verifications:
            all_sources.extend(verification.supporting_sources)
            all_sources.extend(verification.contradicting_sources)

        if all_sources:
            output.primary_sources_used = sum(1 for s in all_sources if s.is_primary_source)
            output.average_source_credibility = sum(s.credibility_score for s in all_sources) / len(all_sources)
            output.data_freshness_score = sum(100.0 if s.is_fresh else 50.0 for s in all_sources) / len(all_sources)

        # Collect unique data sources
        unique_sources = set()
        for source in all_sources:
            unique_sources.add(source.source_name)
        output.data_sources = list(unique_sources)

        # Add critical issues
        if output.contradicted_claims_count > 0:
            output.critical_issues.append(
                f"{output.contradicted_claims_count} claim(s) contradicted by sources"
            )

        if output.overall_confidence_score < 50:
            output.warnings.append("Overall confidence below 50% - verification quality is low")

        return output

    # ========================================================================
    # WEEK 14: ADVANCED ANALYSIS METHODS
    # ========================================================================

    def _validate_cross_references(
        self,
        sources: List[Source],
        claim: Claim
    ) -> Dict[str, Any]:
        """
        Validate consistency across multiple sources (Week 14).

        Cross-references multiple sources to identify:
        - Value consistency across sources
        - Discrepancy patterns
        - Source agreement percentage

        Args:
            sources: List of sources to cross-reference
            claim: The claim being verified

        Returns:
            Dictionary with cross-reference analysis results
        """
        if len(sources) < 2:
            return {
                "has_cross_references": False,
                "agreement_percentage": 0.0,
                "consistent_sources": [],
                "discrepancies": []
            }

        # Extract values from sources
        source_values = {}
        for source in sources:
            if source.retrieved_value:
                val = source.retrieved_value.strip().lower()
                if val not in source_values:
                    source_values[val] = []
                source_values[val].append(source)

        # Calculate agreement
        if not source_values:
            return {
                "has_cross_references": True,
                "agreement_percentage": 0.0,
                "consistent_sources": [],
                "discrepancies": ["No values retrieved from sources"]
            }

        # Find most common value
        most_common_value = max(source_values.items(), key=lambda x: len(x[1]))
        total_sources = len(sources)
        agreeing_sources = len(most_common_value[1])
        agreement_percentage = (agreeing_sources / total_sources) * 100

        # Identify discrepancies
        discrepancies = []
        for value, value_sources in source_values.items():
            if value != most_common_value[0]:
                source_names = [s.source_name for s in value_sources]
                discrepancies.append(
                    f"Value '{value}' reported by {', '.join(source_names)}"
                )

        return {
            "has_cross_references": True,
            "agreement_percentage": agreement_percentage,
            "consistent_value": most_common_value[0],
            "consistent_sources": [s.source_name for s in most_common_value[1]],
            "discrepancies": discrepancies,
            "total_unique_values": len(source_values)
        }

    def _check_temporal_consistency(
        self,
        sources: List[Source],
        claim: Claim
    ) -> Dict[str, Any]:
        """
        Check temporal consistency of data (Week 14).

        Validates:
        - Source data freshness
        - Publication date consistency
        - Temporal ordering logic

        Args:
            sources: List of sources with timestamps
            claim: The claim being verified

        Returns:
            Dictionary with temporal consistency analysis
        """
        temporal_issues = []
        freshness_threshold = self.domain_knowledge.FRESHNESS_THRESHOLDS.get(
            claim.claim_type,
            365
        )

        now = datetime.utcnow()
        fresh_sources = 0
        stale_sources = 0

        for source in sources:
            # Check data freshness
            if source.age_days is not None:
                if source.age_days <= freshness_threshold:
                    fresh_sources += 1
                else:
                    stale_sources += 1
                    temporal_issues.append(
                        f"{source.source_name} data is {source.age_days} days old "
                        f"(threshold: {freshness_threshold} days)"
                    )

            # Check publication vs retrieval dates
            if source.publication_date and source.retrieved_date:
                if source.publication_date > source.retrieved_date:
                    temporal_issues.append(
                        f"{source.source_name} has publication date after retrieval date"
                    )

                # Check if publication is in the future
                if source.publication_date > now:
                    temporal_issues.append(
                        f"{source.source_name} has future publication date"
                    )

        total_sources = len(sources)
        freshness_score = (fresh_sources / total_sources * 100) if total_sources > 0 else 0.0

        return {
            "is_temporally_consistent": len(temporal_issues) == 0,
            "freshness_score": freshness_score,
            "fresh_sources": fresh_sources,
            "stale_sources": stale_sources,
            "temporal_issues": temporal_issues
        }

    def _detect_detailed_contradictions(
        self,
        supporting_sources: List[Source],
        contradicting_sources: List[Source],
        claim: Claim
    ) -> Dict[str, Any]:
        """
        Enhanced contradiction detection (Week 14).

        Analyzes:
        - Contradiction severity (based on source credibility)
        - Contradiction patterns
        - Resolution confidence

        Args:
            supporting_sources: Sources that support the claim
            contradicting_sources: Sources that contradict the claim
            claim: The claim being analyzed

        Returns:
            Dictionary with detailed contradiction analysis
        """
        if not contradicting_sources:
            return {
                "has_contradictions": False,
                "contradiction_severity": "none",
                "high_credibility_contradictions": 0,
                "contradiction_details": []
            }

        # Calculate contradiction severity
        high_credibility_contradictions = sum(
            1 for s in contradicting_sources
            if s.credibility_score >= 70
        )

        avg_contradiction_credibility = (
            sum(s.credibility_score for s in contradicting_sources) / len(contradicting_sources)
        )

        # Determine severity
        if high_credibility_contradictions > 0:
            severity = "high"
        elif avg_contradiction_credibility >= 50:
            severity = "medium"
        else:
            severity = "low"

        # Build contradiction details
        contradiction_details = []
        for source in contradicting_sources:
            detail = {
                "source": source.source_name,
                "credibility": source.credibility_score,
                "value": source.retrieved_value or "unknown",
                "impact": "high" if source.credibility_score >= 70 else "medium" if source.credibility_score >= 50 else "low"
            }
            contradiction_details.append(detail)

        # Assess resolution confidence
        if not supporting_sources:
            resolution_confidence = "low"
        else:
            avg_support_credibility = sum(s.credibility_score for s in supporting_sources) / len(supporting_sources)
            if avg_support_credibility > avg_contradiction_credibility + 20:
                resolution_confidence = "high"
            elif avg_support_credibility > avg_contradiction_credibility:
                resolution_confidence = "medium"
            else:
                resolution_confidence = "low"

        return {
            "has_contradictions": True,
            "contradiction_severity": severity,
            "high_credibility_contradictions": high_credibility_contradictions,
            "average_contradiction_credibility": avg_contradiction_credibility,
            "contradiction_details": contradiction_details,
            "resolution_confidence": resolution_confidence
        }

    def _calculate_enhanced_confidence(
        self,
        verification: Verification,
        cross_ref_analysis: Dict[str, Any],
        temporal_analysis: Dict[str, Any],
        contradiction_analysis: Dict[str, Any]
    ) -> float:
        """
        Enhanced confidence scoring with Week 14 factors.

        Incorporates:
        - Base verification confidence
        - Cross-reference agreement
        - Temporal consistency
        - Contradiction severity

        Args:
            verification: The verification result
            cross_ref_analysis: Cross-reference validation results
            temporal_analysis: Temporal consistency results
            contradiction_analysis: Contradiction analysis results

        Returns:
            Enhanced confidence score (0-100)
        """
        # Start with base confidence
        base_confidence = self._calculate_verification_confidence(verification)

        # Cross-reference factor (up to +15)
        cross_ref_boost = 0.0
        if cross_ref_analysis.get("has_cross_references"):
            agreement_pct = cross_ref_analysis.get("agreement_percentage", 0)
            if agreement_pct >= 90:
                cross_ref_boost = 15.0
            elif agreement_pct >= 75:
                cross_ref_boost = 10.0
            elif agreement_pct >= 60:
                cross_ref_boost = 5.0

        # Temporal consistency factor (up to +10)
        temporal_boost = 0.0
        if temporal_analysis.get("is_temporally_consistent"):
            temporal_boost = 10.0
        else:
            # Penalty for temporal issues
            freshness = temporal_analysis.get("freshness_score", 0)
            if freshness >= 80:
                temporal_boost = 5.0
            elif freshness >= 50:
                temporal_boost = 0.0
            else:
                temporal_boost = -5.0

        # Contradiction severity penalty (up to -20)
        contradiction_penalty = 0.0
        if contradiction_analysis.get("has_contradictions"):
            severity = contradiction_analysis.get("contradiction_severity")
            if severity == "high":
                contradiction_penalty = -20.0
            elif severity == "medium":
                contradiction_penalty = -10.0
            else:
                contradiction_penalty = -5.0

        # Calculate final confidence
        final_confidence = base_confidence + cross_ref_boost + temporal_boost + contradiction_penalty

        # Ensure bounds [0, 100]
        return max(0.0, min(100.0, final_confidence))
