"""
Fact Checker Agent Service

Verifies data accuracy through cross-referencing multiple sources,
assigns confidence scores, and detects conflicts.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class SourceType(str, Enum):
    OFFICIAL_REGISTRY = "official_registry"  # KRS, CEIDG, GUS
    FINANCIAL_REPORT = "financial_report"    # Audited statements
    PUBLIC_FILING = "public_filing"          # Press releases, SEC filings
    INDUSTRY_MEDIA = "industry_media"        # Trade publications
    COMPANY_WEBSITE = "company_website"      # Official company info
    SOCIAL_MEDIA = "social_media"            # LinkedIn, etc
    UNVERIFIED = "unverified"                # Forums, opinions


class IssueFlag(str, Enum):
    CONFLICT = "conflict"
    OUTDATED = "outdated"
    SINGLE_SOURCE = "single_source"
    ESTIMATED = "estimated"


# Source reliability scores (1-10)
SOURCE_RELIABILITY = {
    SourceType.OFFICIAL_REGISTRY: 10,
    SourceType.FINANCIAL_REPORT: 9,
    SourceType.PUBLIC_FILING: 8,
    SourceType.INDUSTRY_MEDIA: 6,
    SourceType.COMPANY_WEBSITE: 5,
    SourceType.SOCIAL_MEDIA: 4,
    SourceType.UNVERIFIED: 2,
}


class FactCheckerService:
    """Service for verifying data accuracy and assigning confidence scores."""

    def __init__(self):
        self.max_data_age_days = 365  # Data older than 1 year considered outdated

    def calculate_confidence(
        self,
        sources: List[Dict[str, Any]],
        verified_value: Any
    ) -> ConfidenceLevel:
        """
        Calculate confidence level based on sources.

        Rules:
        - HIGH: 3+ independent reliable sources OR 1 official registry
        - MEDIUM: 2 sources OR 1 official non-registry
        - LOW: 1 unofficial source
        - UNVERIFIED: no verification possible
        """
        if not sources:
            return ConfidenceLevel.UNVERIFIED

        # Count official registry sources
        official_registry_count = sum(
            1 for s in sources
            if s.get("type") == SourceType.OFFICIAL_REGISTRY
        )

        if official_registry_count >= 1:
            return ConfidenceLevel.HIGH

        # Count high-reliability sources (score >= 8)
        high_reliability_count = sum(
            1 for s in sources
            if SOURCE_RELIABILITY.get(s.get("type", SourceType.UNVERIFIED)) >= 8
        )

        if high_reliability_count >= 2:
            return ConfidenceLevel.HIGH

        # Count all reliable sources (score >= 5)
        reliable_count = sum(
            1 for s in sources
            if SOURCE_RELIABILITY.get(s.get("type", SourceType.UNVERIFIED)) >= 5
        )

        if reliable_count >= 3:
            return ConfidenceLevel.HIGH
        elif reliable_count >= 2:
            return ConfidenceLevel.MEDIUM
        elif reliable_count == 1:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNVERIFIED

    def detect_conflicts(
        self,
        fact_name: str,
        sources: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect conflicts between sources for a given fact.

        Returns conflict details if found, None otherwise.
        """
        if len(sources) < 2:
            return None

        # Extract values from sources
        values = {}
        for source in sources:
            value = source.get("value")
            source_name = source.get("name", "Unknown")
            if value is not None:
                if value not in values:
                    values[value] = []
                values[value].append(source_name)

        # If more than one unique value, we have a conflict
        if len(values) > 1:
            # Find the most reliable value
            most_reliable_value = None
            highest_reliability = 0

            for source in sources:
                reliability = SOURCE_RELIABILITY.get(
                    source.get("type", SourceType.UNVERIFIED),
                    0
                )
                if reliability > highest_reliability:
                    highest_reliability = reliability
                    most_reliable_value = source.get("value")

            # Create conflict report
            conflict_values = [
                {
                    "value": value,
                    "sources": source_list
                }
                for value, source_list in values.items()
            ]

            return {
                "fact": fact_name,
                "conflict_detected": True,
                "conflicting_values": conflict_values,
                "recommended_value": most_reliable_value,
                "resolution_note": "Using value from most reliable source"
            }

        return None

    def check_data_freshness(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if data is fresh or outdated.

        Returns freshness assessment.
        """
        data_date_str = source.get("date")
        if not data_date_str:
            return {
                "is_outdated": False,
                "age_days": None,
                "risk": "unknown",
                "note": "No date information available"
            }

        try:
            data_date = datetime.fromisoformat(data_date_str.replace('Z', '+00:00'))
            age = datetime.now() - data_date
            age_days = age.days

            is_outdated = age_days > self.max_data_age_days

            # Risk assessment
            if age_days < 90:
                risk = "low"
            elif age_days < 180:
                risk = "medium"
            else:
                risk = "high"

            return {
                "is_outdated": is_outdated,
                "age_days": age_days,
                "data_date": data_date_str,
                "risk": risk,
                "recommendation": "Verify with current data" if is_outdated else "Data is current"
            }
        except (ValueError, AttributeError):
            return {
                "is_outdated": False,
                "age_days": None,
                "risk": "unknown",
                "note": "Invalid date format"
            }

    def verify_fact(
        self,
        fact_name: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a single fact by cross-referencing sources.

        Args:
            fact_name: Name/description of the fact
            sources: List of sources with their data
                Each source should have: name, type, value, date (optional)

        Returns:
            Verification result with confidence and flags
        """
        # Calculate consensus value (most common or from most reliable source)
        if not sources:
            verified_value = None
            source_names = []
        else:
            # Find most reliable source
            most_reliable = max(
                sources,
                key=lambda s: SOURCE_RELIABILITY.get(
                    s.get("type", SourceType.UNVERIFIED),
                    0
                )
            )
            verified_value = most_reliable.get("value")
            source_names = [s.get("name", "Unknown") for s in sources]

        # Calculate confidence
        confidence = self.calculate_confidence(sources, verified_value)

        # Detect conflicts
        conflict = self.detect_conflicts(fact_name, sources)

        # Check for issues
        flags = []

        if conflict:
            flags.append(IssueFlag.CONFLICT)

        if len(sources) == 1:
            flags.append(IssueFlag.SINGLE_SOURCE)

        # Check freshness of most recent source
        if sources:
            recent_source = max(
                sources,
                key=lambda s: s.get("date", "1900-01-01")
            )
            freshness = self.check_data_freshness(recent_source)
            if freshness.get("is_outdated"):
                flags.append(IssueFlag.OUTDATED)

        # Check if value is estimated
        for source in sources:
            if "estimate" in str(source.get("value", "")).lower():
                flags.append(IssueFlag.ESTIMATED)
                break

        return {
            "fact": fact_name,
            "verified_value": verified_value,
            "sources": source_names,
            "source_count": len(sources),
            "confidence": confidence.value,
            "flags": [f.value for f in flags],
            "conflict": conflict,
            "notes": self._generate_notes(confidence, flags, sources)
        }

    def _generate_notes(
        self,
        confidence: ConfidenceLevel,
        flags: List[IssueFlag],
        sources: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable notes about the verification."""
        notes = []

        if confidence == ConfidenceLevel.HIGH:
            notes.append("High confidence - verified by multiple reliable sources")
        elif confidence == ConfidenceLevel.MEDIUM:
            notes.append("Medium confidence - limited source verification")
        elif confidence == ConfidenceLevel.LOW:
            notes.append("Low confidence - single source verification only")
        else:
            notes.append("Unverified - unable to confirm from reliable sources")

        if IssueFlag.CONFLICT in flags:
            notes.append("⚠️ Conflicting information detected between sources")

        if IssueFlag.SINGLE_SOURCE in flags:
            notes.append("⚠️ Only one source available")

        if IssueFlag.OUTDATED in flags:
            notes.append("⚠️ Data may be outdated - verification recommended")

        if IssueFlag.ESTIMATED in flags:
            notes.append("⚠️ Value is estimated")

        return " | ".join(notes)

    def check_company_profile(
        self,
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform fact checking on company profile data.

        Args:
            company_data: Dictionary with company information from multiple sources

        Returns:
            Comprehensive fact check report
        """
        verified_facts = []
        conflicts = []
        confidence_summary = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "unverified": 0
        }

        # Check each fact (skip company_name which is metadata)
        for fact_name, fact_data in company_data.items():
            if fact_name == "company_name":
                continue

            # Handle dict format (expected) or skip if not dict
            if not isinstance(fact_data, dict):
                continue

            sources = fact_data.get("sources", [])

            verification = self.verify_fact(fact_name, sources)
            verified_facts.append(verification)

            # Update confidence summary
            confidence_level = verification["confidence"]
            confidence_summary[confidence_level] += 1

            # Collect conflicts
            if verification.get("conflict"):
                conflicts.append(verification["conflict"])

        # Calculate overall data quality score (0-100)
        total_facts = len(verified_facts)
        if total_facts == 0:
            quality_score = 0
        else:
            weighted_score = (
                confidence_summary["high"] * 100 +
                confidence_summary["medium"] * 70 +
                confidence_summary["low"] * 40 +
                confidence_summary["unverified"] * 0
            )
            quality_score = int(weighted_score / total_facts)

        return {
            "fact_check_report": {
                "subject": company_data.get("company_name", "Unknown Company"),
                "check_date": datetime.utcnow().isoformat(),
                "total_facts_checked": total_facts,
                "confidence_summary": confidence_summary,
                "verified_facts": verified_facts,
                "conflicts_detected": conflicts,
                "data_quality_score": quality_score,
                "recommendations": self._generate_recommendations(
                    confidence_summary,
                    conflicts,
                    quality_score
                )
            }
        }

    def _generate_recommendations(
        self,
        confidence_summary: Dict[str, int],
        conflicts: List[Dict[str, Any]],
        quality_score: int
    ) -> List[str]:
        """Generate recommendations based on fact checking results."""
        recommendations = []

        if confidence_summary["unverified"] > 0:
            recommendations.append(
                f"Verify {confidence_summary['unverified']} unverified facts with additional sources"
            )

        if confidence_summary["low"] > confidence_summary["high"]:
            recommendations.append(
                "Seek additional reliable sources to improve data confidence"
            )

        if len(conflicts) > 0:
            recommendations.append(
                f"Resolve {len(conflicts)} data conflicts by consulting official sources"
            )

        if quality_score < 60:
            recommendations.append(
                "Overall data quality is low - consider comprehensive data refresh"
            )
        elif quality_score < 80:
            recommendations.append(
                "Data quality is moderate - targeted improvements recommended"
            )

        if not recommendations:
            recommendations.append(
                "Data quality is good - routine verification recommended"
            )

        return recommendations


# Singleton instance
fact_checker = FactCheckerService()
