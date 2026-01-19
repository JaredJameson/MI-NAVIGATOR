"""
Report Composer Service

This service aggregates data from multiple analysis agents and composes
a cohesive, well-structured report with:
- Executive summary
- Table of contents
- Multiple sections from different agents
- Source citations
- Recommendations
- Professional formatting
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class ReportSection(str, Enum):
    """Report section types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_PROFILE = "company_profile"
    FINANCIAL_ANALYSIS = "financial_analysis"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    INSIGHTS = "insights"
    OPPORTUNITIES = "opportunities"
    RISKS = "risks"
    RECOMMENDATIONS = "recommendations"
    SOURCES = "sources"
    APPENDICES = "appendices"


class ReportComposerService:
    """
    Service for composing comprehensive reports from multiple agent outputs.

    Features:
    - Aggregates sections from different analysis agents
    - Generates executive summary
    - Creates table of contents
    - Formats source citations
    - Ensures language consistency
    - Maintains professional tone
    """

    def __init__(self):
        self.section_order = [
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.COMPANY_PROFILE,
            ReportSection.FINANCIAL_ANALYSIS,
            ReportSection.MARKET_ANALYSIS,
            ReportSection.COMPETITIVE_ANALYSIS,
            ReportSection.INSIGHTS,
            ReportSection.OPPORTUNITIES,
            ReportSection.RISKS,
            ReportSection.RECOMMENDATIONS,
            ReportSection.SOURCES,
            ReportSection.APPENDICES,
        ]

    def compose_report(
        self,
        company_name: str,
        sections: Dict[str, Any],
        include_sources: bool = True,
        language: str = "pl"
    ) -> Dict[str, Any]:
        """
        Compose a comprehensive report from multiple agent outputs.

        Args:
            company_name: Company name for the report
            sections: Dictionary of section data from various agents
            include_sources: Whether to include sources section
            language: Report language (pl/en)

        Returns:
            Complete report structure with all sections
        """

        # Generate executive summary from all sections
        executive_summary = self._generate_executive_summary(
            company_name, sections, language
        )

        # Organize sections in proper order
        ordered_sections = self._organize_sections(sections)

        # Generate table of contents
        table_of_contents = self._generate_table_of_contents(
            ordered_sections, language
        )

        # Collect and format all sources
        all_sources = self._collect_sources(sections) if include_sources else []

        # Build final report structure
        report = {
            "title": self._generate_title(company_name, sections, language),
            "subtitle": self._generate_subtitle(sections, language),
            "generated_at": datetime.utcnow().isoformat(),
            "company_name": company_name,
            "language": language,
            "executive_summary": executive_summary,
            "table_of_contents": table_of_contents,
            "sections": ordered_sections,
            "sources": all_sources,
            "metadata": {
                "section_count": len(ordered_sections),
                "source_count": len(all_sources),
                "word_count": self._estimate_word_count(ordered_sections),
                "analysis_depth": self._determine_analysis_depth(sections),
            }
        }

        return report

    def _generate_executive_summary(
        self,
        company_name: str,
        sections: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """
        Generate executive summary from all section data.

        Synthesizes key points from all sections into a concise overview.
        """

        key_findings = []
        key_metrics = {}

        # Extract key findings from company profile
        if "company_profile" in sections:
            profile = sections["company_profile"]
            if isinstance(profile, dict):
                key_findings.append({
                    "category": "Profil firmy",
                    "finding": f"{company_name} - {profile.get('legal_form', 'firma')} założona w {profile.get('founded_year', 'N/A')}"
                })
                if "industry" in profile:
                    key_findings.append({
                        "category": "Branża",
                        "finding": profile["industry"]
                    })

        # Extract key findings from financial analysis
        if "financial_analysis" in sections:
            financial = sections["financial_analysis"]
            if isinstance(financial, dict) and "metrics" in financial:
                metrics = financial["metrics"]
                if "revenue" in metrics:
                    key_metrics["revenue"] = metrics["revenue"]
                    key_findings.append({
                        "category": "Przychody",
                        "finding": f"Przychody: {self._format_currency(metrics['revenue'])}"
                    })
                if "revenue_growth" in metrics:
                    key_metrics["revenue_growth"] = metrics["revenue_growth"]
                    growth = metrics["revenue_growth"]
                    trend = "wzrost" if growth > 0 else "spadek"
                    key_findings.append({
                        "category": "Dynamika przychodów",
                        "finding": f"{trend.capitalize()} przychodów o {abs(growth):.1f}%"
                    })
                if "profit_margin" in metrics:
                    key_metrics["profit_margin"] = metrics["profit_margin"]

        # Extract key findings from insights
        insight_count = 0
        opportunity_count = 0
        risk_count = 0

        if "insights" in sections and isinstance(sections["insights"], list):
            insight_count = len(sections["insights"])

        if "opportunities" in sections and isinstance(sections["opportunities"], list):
            opportunity_count = len(sections["opportunities"])

        if "risks" in sections and isinstance(sections["risks"], list):
            risk_count = len(sections["risks"])

        if insight_count > 0:
            key_findings.append({
                "category": "Analiza",
                "finding": f"Zidentyfikowano {insight_count} kluczowych spostrzeżeń"
            })

        if opportunity_count > 0:
            key_findings.append({
                "category": "Szanse",
                "finding": f"Wykryto {opportunity_count} możliwości rozwoju"
            })

        if risk_count > 0:
            key_findings.append({
                "category": "Zagrożenia",
                "finding": f"Zidentyfikowano {risk_count} potencjalnych zagrożeń"
            })

        # Generate summary text
        summary_text = self._generate_summary_text(
            company_name, key_findings, key_metrics, language
        )

        return {
            "text": summary_text,
            "key_findings": key_findings,
            "key_metrics": key_metrics,
            "highlights": self._extract_highlights(sections, language)
        }

    def _generate_summary_text(
        self,
        company_name: str,
        key_findings: List[Dict],
        key_metrics: Dict,
        language: str
    ) -> str:
        """Generate cohesive summary text."""

        if language == "pl":
            text = f"Raport analizy dla {company_name}\n\n"
            text += "Kluczowe ustalenia:\n"
            for finding in key_findings[:5]:  # Top 5 findings
                text += f"• {finding['finding']}\n"

            if key_metrics:
                text += "\nKluczowe wskaźniki:\n"
                for metric, value in key_metrics.items():
                    text += f"• {metric}: {value}\n"

            return text
        else:
            text = f"Analysis Report for {company_name}\n\n"
            text += "Key Findings:\n"
            for finding in key_findings[:5]:
                text += f"• {finding['finding']}\n"

            if key_metrics:
                text += "\nKey Metrics:\n"
                for metric, value in key_metrics.items():
                    text += f"• {metric}: {value}\n"

            return text

    def _extract_highlights(
        self,
        sections: Dict[str, Any],
        language: str
    ) -> List[str]:
        """Extract top highlights from all sections."""

        highlights = []

        # Extract from insights
        if "insights" in sections and isinstance(sections["insights"], list):
            for insight in sections["insights"][:3]:  # Top 3 insights
                if isinstance(insight, dict) and "title" in insight:
                    highlights.append(insight["title"])

        # Extract from opportunities
        if "opportunities" in sections and isinstance(sections["opportunities"], list):
            for opp in sections["opportunities"][:2]:  # Top 2 opportunities
                if isinstance(opp, dict) and "title" in opp:
                    highlights.append(f"Szansa: {opp['title']}")

        # Extract from risks
        if "risks" in sections and isinstance(sections["risks"], list):
            high_risks = [r for r in sections["risks"] if isinstance(r, dict) and r.get("severity") == "high"]
            for risk in high_risks[:2]:  # Top 2 high risks
                if "title" in risk:
                    highlights.append(f"Ryzyko: {risk['title']}")

        return highlights

    def _organize_sections(self, sections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Organize sections according to predefined order.

        Filters out empty sections and maintains logical flow.
        """

        organized = []

        for section_type in self.section_order:
            section_key = section_type.value

            # Skip executive summary (handled separately)
            if section_type == ReportSection.EXECUTIVE_SUMMARY:
                continue

            # Check if section exists and has content
            if section_key in sections and sections[section_key]:
                section_data = sections[section_key]

                # Build section structure
                section = {
                    "id": section_key,
                    "title": self._get_section_title(section_type),
                    "type": section_type.value,
                    "content": section_data,
                    "order": len(organized) + 1
                }

                organized.append(section)

        return organized

    def _get_section_title(self, section_type: ReportSection) -> str:
        """Get human-readable title for section type."""

        titles = {
            ReportSection.COMPANY_PROFILE: "Profil firmy",
            ReportSection.FINANCIAL_ANALYSIS: "Analiza finansowa",
            ReportSection.MARKET_ANALYSIS: "Analiza rynku",
            ReportSection.COMPETITIVE_ANALYSIS: "Analiza konkurencji",
            ReportSection.INSIGHTS: "Kluczowe spostrzeżenia",
            ReportSection.OPPORTUNITIES: "Możliwości",
            ReportSection.RISKS: "Zagrożenia",
            ReportSection.RECOMMENDATIONS: "Rekomendacje",
            ReportSection.SOURCES: "Źródła",
            ReportSection.APPENDICES: "Załączniki",
        }

        return titles.get(section_type, section_type.value.replace("_", " ").title())

    def _generate_table_of_contents(
        self,
        sections: List[Dict[str, Any]],
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Generate table of contents from sections.

        Creates hierarchical TOC with section numbers and titles.
        """

        toc = []

        # Always include executive summary first
        toc.append({
            "number": "1",
            "title": "Streszczenie zarządcze" if language == "pl" else "Executive Summary",
            "section_id": "executive_summary",
            "page": 1
        })

        # Add all other sections
        for idx, section in enumerate(sections, start=2):
            toc.append({
                "number": str(idx),
                "title": section["title"],
                "section_id": section["id"],
                "page": idx
            })

        return toc

    def _collect_sources(self, sections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect and deduplicate all sources from sections.

        Aggregates sources from all sections and removes duplicates.
        """

        all_sources = []
        seen_sources = set()

        for section_key, section_data in sections.items():
            # Check if section has sources
            if isinstance(section_data, dict):
                # Look for sources in various formats
                sources = section_data.get("sources", [])

                if isinstance(sources, list):
                    for source in sources:
                        if isinstance(source, dict):
                            # Create unique identifier
                            source_id = f"{source.get('type', '')}_{source.get('url', '')}_{source.get('name', '')}"

                            if source_id not in seen_sources:
                                seen_sources.add(source_id)
                                all_sources.append({
                                    **source,
                                    "used_in_sections": [section_key]
                                })
                        else:
                            # Already exists - add section reference
                            for existing in all_sources:
                                if (existing.get("type") == source.get("type") and
                                    existing.get("url") == source.get("url")):
                                    if section_key not in existing.get("used_in_sections", []):
                                        existing["used_in_sections"].append(section_key)

        # Sort by reliability and type
        all_sources.sort(key=lambda x: (
            -x.get("confidence", 0),
            x.get("type", ""),
            x.get("name", "")
        ))

        # Add citation numbers
        for idx, source in enumerate(all_sources, start=1):
            source["citation_number"] = idx

        return all_sources

    def _generate_title(
        self,
        company_name: str,
        sections: Dict[str, Any],
        language: str
    ) -> str:
        """Generate report title."""

        if language == "pl":
            return f"Raport analizy: {company_name}"
        else:
            return f"Analysis Report: {company_name}"

    def _generate_subtitle(
        self,
        sections: Dict[str, Any],
        language: str
    ) -> str:
        """Generate report subtitle based on included sections."""

        section_types = []

        if "company_profile" in sections:
            section_types.append("profil firmy")
        if "financial_analysis" in sections:
            section_types.append("analiza finansowa")
        if "market_analysis" in sections:
            section_types.append("analiza rynku")
        if "competitive_analysis" in sections:
            section_types.append("analiza konkurencji")

        if language == "pl":
            if section_types:
                return f"Kompleksowa analiza obejmująca: {', '.join(section_types)}"
            else:
                return "Raport analityczny"
        else:
            return "Comprehensive analytical report"

    def _estimate_word_count(self, sections: List[Dict[str, Any]]) -> int:
        """Estimate total word count in report."""

        total = 0

        for section in sections:
            content = section.get("content", {})

            # Estimate based on content structure
            if isinstance(content, dict):
                # Count text fields
                for key, value in content.items():
                    if isinstance(value, str):
                        total += len(value.split())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for v in item.values():
                                    if isinstance(v, str):
                                        total += len(v.split())
            elif isinstance(content, str):
                total += len(content.split())

        return total

    def _determine_analysis_depth(self, sections: Dict[str, Any]) -> str:
        """Determine analysis depth based on section count and content."""

        section_count = len(sections)

        if section_count >= 6:
            return "deep"
        elif section_count >= 3:
            return "standard"
        else:
            return "quick"

    def _format_currency(self, amount: float, currency: str = "PLN") -> str:
        """Format currency value."""

        if amount >= 1_000_000_000:
            return f"{amount / 1_000_000_000:.2f} mld {currency}"
        elif amount >= 1_000_000:
            return f"{amount / 1_000_000:.2f} mln {currency}"
        elif amount >= 1_000:
            return f"{amount / 1_000:.2f} tys. {currency}"
        else:
            return f"{amount:.2f} {currency}"
