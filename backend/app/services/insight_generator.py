"""
Insight Generator Agent Service

Analyzes collected company and market data to produce actionable insights,
recommendations, opportunities, and risk identification.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class InsightType(str, Enum):
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"
    COMPETITIVE = "competitive"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Impact(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Timeline(str, Enum):
    IMMEDIATE = "immediate"      # 0-3 months
    SHORT_TERM = "short_term"    # 3-12 months
    MEDIUM_TERM = "medium_term"  # 1-3 years
    LONG_TERM = "long_term"      # 3+ years


class InsightGeneratorService:
    """Service for generating actionable insights from company and market data."""

    def __init__(self):
        pass

    def analyze_financial_health(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze financial data and generate insights.

        Args:
            financial_data: Dictionary with financial metrics

        Returns:
            List of financial insights
        """
        insights = []

        revenue = financial_data.get("revenue")
        revenue_growth = financial_data.get("revenue_growth")
        profit_margin = financial_data.get("profit_margin")
        debt_to_equity = financial_data.get("debt_to_equity")
        liquidity_ratio = financial_data.get("liquidity_ratio")

        # Revenue growth analysis
        if revenue_growth is not None:
            if revenue_growth > 20:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Silny wzrost przychodów",
                    "description": f"Firma odnotowała wzrost przychodów o {revenue_growth}%, co znacznie przewyższa średnią branżową (5-10%). To świadczy o silnej pozycji rynkowej i efektywnej strategii sprzedaży.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"revenue_growth: {revenue_growth}%"
                })
            elif revenue_growth < 0:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Spadające przychody",
                    "description": f"Firma odnotowała spadek przychodów o {abs(revenue_growth)}%. Wymaga to natychmiastowej analizy przyczyn i działań naprawczych.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"revenue_growth: {revenue_growth}%"
                })
            elif 0 <= revenue_growth < 5:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Niski wzrost przychodów",
                    "description": f"Wzrost przychodów ({revenue_growth}%) jest poniżej średniej branżowej. Może to sygnalizować wyzwania konkurencyjne lub nasycenie rynku.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"revenue_growth: {revenue_growth}%"
                })

        # Profitability analysis
        if profit_margin is not None:
            if profit_margin > 15:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Wysoka rentowność",
                    "description": f"Marża zysku ({profit_margin}%) jest powyżej średniej branżowej, co wskazuje na efektywne zarządzanie kosztami i silną pozycję cenową.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"profit_margin: {profit_margin}%"
                })
            elif profit_margin < 5:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Niska rentowność",
                    "description": f"Marża zysku ({profit_margin}%) jest bardzo niska, co może oznaczać presję kosztową lub silną konkurencję cenową.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"profit_margin: {profit_margin}%"
                })

        # Debt analysis
        if debt_to_equity is not None:
            if debt_to_equity > 2.0:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Wysokie zadłużenie",
                    "description": f"Wskaźnik zadłużenia ({debt_to_equity:.2f}) przekracza bezpieczny poziom 2.0, co może ograniczać zdolność do inwestycji i zwiększać ryzyko finansowe.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"debt_to_equity: {debt_to_equity:.2f}"
                })
            elif debt_to_equity < 0.5:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Niska dźwignia finansowa",
                    "description": f"Wskaźnik zadłużenia ({debt_to_equity:.2f}) jest niski, co oznacza niewykorzystany potencjał do finansowania wzrostu poprzez dług.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"debt_to_equity: {debt_to_equity:.2f}"
                })

        # Liquidity analysis
        if liquidity_ratio is not None:
            if liquidity_ratio < 1.0:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Problemy z płynnością",
                    "description": f"Wskaźnik płynności ({liquidity_ratio:.2f}) poniżej 1.0 oznacza, że firma może mieć trudności z regulowaniem bieżących zobowiązań.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"liquidity_ratio: {liquidity_ratio:.2f}"
                })
            elif liquidity_ratio > 3.0:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Nadmierna płynność",
                    "description": f"Wskaźnik płynności ({liquidity_ratio:.2f}) jest bardzo wysoki, co może oznaczać niewykorzystane środki które mogłyby być zainwestowane w rozwój.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"liquidity_ratio: {liquidity_ratio:.2f}"
                })

        return insights

    def analyze_market_position(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze market position and generate insights.

        Args:
            market_data: Dictionary with market metrics

        Returns:
            List of market insights
        """
        insights = []

        market_share = market_data.get("market_share")
        market_growth = market_data.get("market_growth")
        competitor_count = market_data.get("competitor_count")
        market_size = market_data.get("market_size")

        # Market share analysis
        if market_share is not None:
            if market_share > 20:
                insights.append({
                    "type": InsightType.COMPETITIVE,
                    "title": "Dominująca pozycja rynkowa",
                    "description": f"Udział w rynku ({market_share}%) plasuje firmę w czołówce liderów branży, zapewniając silną pozycję negocjacyjną.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"market_share: {market_share}%"
                })
            elif market_share < 5:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Potencjał wzrostu udziału w rynku",
                    "description": f"Niski udział w rynku ({market_share}%) oznacza duży potencjał do ekspansji i zdobycia większego fragmentu rynku.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"market_share: {market_share}%"
                })

        # Market growth analysis
        if market_growth is not None:
            if market_growth > 10:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Dynamicznie rosnący rynek",
                    "description": f"Wzrost rynku ({market_growth}% rocznie) tworzy sprzyjające warunki dla ekspansji i pozyskania nowych klientów.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"market_growth: {market_growth}%"
                })
            elif market_growth < 0:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Kurczący się rynek",
                    "description": f"Spadek rynku ({abs(market_growth)}%) wymaga strategii defensywnej i poszukiwania alternatywnych segmentów.",
                    "impact": Impact.HIGH,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"market_growth: {market_growth}%"
                })

        # Competition intensity
        if competitor_count is not None and market_size is not None:
            avg_revenue_per_competitor = market_size / competitor_count if competitor_count > 0 else 0
            if competitor_count > 50:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Silnie sfragmentowany rynek",
                    "description": f"Wysoka liczba konkurentów ({competitor_count}) oznacza intensywną konkurencję i presję cenową.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"competitor_count: {competitor_count}"
                })
            elif competitor_count < 10:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Rynek oligopolistyczny",
                    "description": f"Niska liczba konkurentów ({competitor_count}) może oznaczać bariery wejścia i stabilniejsze środowisko biznesowe.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"competitor_count: {competitor_count}"
                })

        return insights

    def analyze_digital_presence(self, digital_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze digital presence and generate insights.

        Args:
            digital_data: Dictionary with digital metrics

        Returns:
            List of digital insights
        """
        insights = []

        website_traffic = digital_data.get("website_traffic")
        social_media_followers = digital_data.get("social_media_followers")
        seo_score = digital_data.get("seo_score")
        mobile_responsive = digital_data.get("mobile_responsive")

        # Website traffic analysis
        if website_traffic is not None:
            if website_traffic > 100000:
                insights.append({
                    "type": InsightType.OPPORTUNITY,
                    "title": "Silna obecność online",
                    "description": f"Wysoki ruch na stronie ({website_traffic:,} odwiedzin/miesiąc) świadczy o skutecznej strategii marketingu cyfrowego.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"website_traffic: {website_traffic}"
                })
            elif website_traffic < 1000:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Słaba widoczność online",
                    "description": f"Niski ruch na stronie ({website_traffic} odwiedzin/miesiąc) wymaga działań w zakresie SEO i marketingu cyfrowego.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"website_traffic: {website_traffic}"
                })

        # SEO analysis
        if seo_score is not None:
            if seo_score < 50:
                insights.append({
                    "type": InsightType.RISK,
                    "title": "Słabe SEO",
                    "description": f"Niska ocena SEO ({seo_score}/100) ogranicza organiczną widoczność w wyszukiwarkach.",
                    "impact": Impact.MEDIUM,
                    "confidence": "high",
                    "data_backed": True,
                    "source_metric": f"seo_score: {seo_score}"
                })

        # Mobile responsiveness
        if mobile_responsive is False:
            insights.append({
                "type": InsightType.RISK,
                "title": "Brak responsywności mobilnej",
                "description": "Strona nie jest zoptymalizowana pod urządzenia mobilne, co negatywnie wpływa na doświadczenie użytkownika i SEO.",
                "impact": Impact.HIGH,
                "confidence": "high",
                "data_backed": True,
                "source_metric": "mobile_responsive: false"
            })

        return insights

    def generate_recommendations(
        self,
        insights: List[Dict[str, Any]],
        company_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate specific, actionable recommendations based on insights.

        Args:
            insights: List of generated insights
            company_context: Additional company context (optional)

        Returns:
            List of recommendations with priority and timeline
        """
        recommendations = []

        # Count insights by type and impact
        # Check for critical liquidity risks (high impact + liquidity in title)
        critical_risks = [i for i in insights if i.get("type") == InsightType.RISK and i.get("impact") == Impact.HIGH and "płynność" in i.get("title", "").lower()]
        high_impact_risks = [i for i in insights if i.get("type") == InsightType.RISK and i.get("impact") == Impact.HIGH]
        high_impact_opportunities = [i for i in insights if i.get("type") == InsightType.OPPORTUNITY and i.get("impact") == Impact.HIGH]

        # Critical risks - immediate action required
        for risk in critical_risks:
            if "płynności" in risk.get("title", "").lower():
                recommendations.append({
                    "title": "Pilna poprawa płynności finansowej",
                    "description": "Negocjuj wydłużenie terminów płatności z dostawcami, przyspiesz windykację należności, rozważ krótkoterminowe finansowanie.",
                    "priority": Priority.CRITICAL,
                    "timeline": Timeline.IMMEDIATE,
                    "expected_impact": "Zapewnienie ciągłości operacyjnej i uniknięcie problemów z regulowaniem zobowiązań",
                    "related_insights": [risk.get("title")]
                })

        # High impact risks
        for risk in high_impact_risks:
            if "przychody" in risk.get("title", "").lower():
                recommendations.append({
                    "title": "Wdrożenie planu naprawczego dla sprzedaży",
                    "description": "Przeprowadź analizę przyczyn spadku, zidentyfikuj traconych klientów, uruchom kampanię retencyjną, rozważ nowe kanały sprzedaży.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.SHORT_TERM,
                    "expected_impact": "Zatrzymanie spadku przychodów i powrót do wzrostowej trajektorii",
                    "related_insights": [risk.get("title")]
                })
            elif "rentowność" in risk.get("title", "").lower():
                recommendations.append({
                    "title": "Optymalizacja struktury kosztów",
                    "description": "Przeprowadź audyt kosztów operacyjnych, zidentyfikuj nieefektywne procesy, renegocjuj kontrakty z dostawcami, rozważ outsourcing niestrategicznych funkcji.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.SHORT_TERM,
                    "expected_impact": "Poprawa marży o 3-5 punktów procentowych w ciągu 12 miesięcy",
                    "related_insights": [risk.get("title")]
                })
            elif "zadłużenie" in risk.get("title", "").lower():
                recommendations.append({
                    "title": "Restrukturyzacja zadłużenia",
                    "description": "Negocjuj z wierzycielami wydłużenie terminów spłaty, rozważ refinansowanie na lepszych warunkach, zwiększ kapitały własne.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.MEDIUM_TERM,
                    "expected_impact": "Redukcja ryzyka finansowego i poprawa wskaźnika zadłużenia do bezpiecznego poziomu",
                    "related_insights": [risk.get("title")]
                })
            elif "online" in risk.get("title", "").lower() or "seo" in risk.get("title", "").lower():
                recommendations.append({
                    "title": "Wzmocnienie obecności cyfrowej",
                    "description": "Audyt SEO i optymalizacja strony, kampanie content marketingu, aktywizacja social media, rozważenie e-commerce.",
                    "priority": Priority.MEDIUM,
                    "timeline": Timeline.SHORT_TERM,
                    "expected_impact": "Zwiększenie ruchu organicznego o 50-100% w ciągu 6 miesięcy",
                    "related_insights": [risk.get("title")]
                })
            elif "rynek" in risk.get("description", "").lower() and "kurczący" in risk.get("description", "").lower():
                recommendations.append({
                    "title": "Dywersyfikacja oferty i rynków",
                    "description": "Zidentyfikuj rosnące segmenty i regiony, rozważ nowe produkty/usługi, eksploruj rynki eksportowe.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.MEDIUM_TERM,
                    "expected_impact": "Zmniejszenie zależności od kurczącego się rynku i otwarcie nowych źródeł przychodów",
                    "related_insights": [risk.get("title")]
                })

        # High impact opportunities
        for opp in high_impact_opportunities:
            if "wzrost" in opp.get("title", "").lower() and "przychody" in opp.get("title", "").lower():
                recommendations.append({
                    "title": "Kapitalizacja momentum wzrostu",
                    "description": "Inwestuj w skalowanie operacji, zwiększ budżet marketingowy, rozbuduj zespół sprzedażowy, rozważ M&A mniejszych konkurentów.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.SHORT_TERM,
                    "expected_impact": "Utrzymanie tempa wzrostu i umocnienie pozycji lidera rynkowego",
                    "related_insights": [opp.get("title")]
                })
            elif "rentowność" in opp.get("title", "").lower():
                recommendations.append({
                    "title": "Reinwestycja w innowacje i rozwój",
                    "description": "Przeznacz część zysków na R&D, modernizację technologii, rozwój nowych produktów, które wzmocnią przewagę konkurencyjną.",
                    "priority": Priority.MEDIUM,
                    "timeline": Timeline.MEDIUM_TERM,
                    "expected_impact": "Utrzymanie wysokiej rentowności długoterminowo poprzez innowacje",
                    "related_insights": [opp.get("title")]
                })
            elif "udział w rynku" in opp.get("title", "").lower():
                recommendations.append({
                    "title": "Agresywna ekspansja rynkowa",
                    "description": "Uruchom kampanie akwizycyjne, ofertuj atrakcyjne warunki dla nowych klientów, rozważ przejęcia strategiczne.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.SHORT_TERM,
                    "expected_impact": "Zwiększenie udziału w rynku o 5-10 punktów procentowych",
                    "related_insights": [opp.get("title")]
                })
            elif "rosnący rynek" in opp.get("title", "").lower():
                recommendations.append({
                    "title": "Przyspieszona ekspansja na rosnącym rynku",
                    "description": "Zwiększ zdolności produkcyjne, rozbuduj sieć dystrybucji, zainwestuj w branding, by zyskać pierwszeństwo przed konkurencją.",
                    "priority": Priority.HIGH,
                    "timeline": Timeline.SHORT_TERM,
                    "expected_impact": "Zdobycie znaczącego udziału w dynamicznie rosnącym rynku",
                    "related_insights": [opp.get("title")]
                })

        # If no specific recommendations generated, add general ones
        if not recommendations:
            recommendations.append({
                "title": "Kontynuacja obecnej strategii",
                "description": "Brak krytycznych problemów - kontynuuj obecne działania z regularnym monitoringiem kluczowych wskaźników.",
                "priority": Priority.LOW,
                "timeline": Timeline.MEDIUM_TERM,
                "expected_impact": "Utrzymanie stabilnej pozycji biznesowej",
                "related_insights": []
            })

        return recommendations

    def identify_risks(
        self,
        insights: List[Dict[str, Any]],
        company_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract and categorize risks from insights.

        Args:
            insights: List of generated insights
            company_context: Additional company context (optional)

        Returns:
            List of identified risks with severity and mitigation strategies
        """
        risks = []

        risk_insights = [i for i in insights if i.get("type") == InsightType.RISK]

        for insight in risk_insights:
            risk_entry = {
                "title": insight.get("title"),
                "description": insight.get("description"),
                "severity": insight.get("impact"),
                "likelihood": "medium",  # Could be enhanced with historical data
                "data_backed": insight.get("data_backed", False),
                "source_metric": insight.get("source_metric"),
                "mitigation_strategies": self._generate_mitigation_strategies(insight)
            }
            risks.append(risk_entry)

        return risks

    def _generate_mitigation_strategies(self, risk_insight: Dict[str, Any]) -> List[str]:
        """Generate mitigation strategies for a specific risk."""
        strategies = []
        title = risk_insight.get("title", "").lower()

        if "płynności" in title:
            strategies = [
                "Ustanowienie linii kredytowej na wypadki awaryjne",
                "Wdrożenie systemu prognozowania cash flow",
                "Negocjacja lepszych warunków płatności",
            ]
        elif "przychody" in title or "sprzedaż" in title:
            strategies = [
                "Dywersyfikacja kanałów sprzedaży",
                "Program retencji klientów",
                "Ekspansja na nowe rynki geograficzne",
            ]
        elif "rentowność" in title or "koszt" in title:
            strategies = [
                "Automatyzacja procesów",
                "Renegocjacja kontraktów z dostawcami",
                "Lean management i eliminacja marnotrawstwa",
            ]
        elif "zadłużenie" in title:
            strategies = [
                "Plan systematycznej spłaty zadłużenia",
                "Refinansowanie na lepszych warunkach",
                "Zwiększenie kapitału własnego",
            ]
        elif "konkurencja" in title or "rynek" in title:
            strategies = [
                "Wzmocnienie unikalnej propozycji wartości",
                "Inwestycje w innowacje produktowe",
                "Budowanie lojalności klientów",
            ]
        else:
            strategies = [
                "Regularne monitorowanie sytuacji",
                "Przygotowanie planu awaryjnego",
                "Konsultacja z ekspertami branżowymi",
            ]

        return strategies

    def generate_insights_report(
        self,
        company_name: str,
        financial_data: Optional[Dict[str, Any]] = None,
        market_data: Optional[Dict[str, Any]] = None,
        digital_data: Optional[Dict[str, Any]] = None,
        competitor_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights report from all available data.

        Args:
            company_name: Name of the company
            financial_data: Financial metrics (optional)
            market_data: Market position data (optional)
            digital_data: Digital presence metrics (optional)
            competitor_data: Competitive intelligence (optional)

        Returns:
            Comprehensive insights report with recommendations and risks
        """
        all_insights = []

        # Analyze each data category
        if financial_data:
            all_insights.extend(self.analyze_financial_health(financial_data))

        if market_data:
            all_insights.extend(self.analyze_market_position(market_data))

        if digital_data:
            all_insights.extend(self.analyze_digital_presence(digital_data))

        # Count insights by type
        opportunities = [i for i in all_insights if i.get("type") == InsightType.OPPORTUNITY]
        risks = [i for i in all_insights if i.get("type") == InsightType.RISK]

        # Generate recommendations and risk assessment
        company_context = {
            "name": company_name,
            "financial_data": financial_data,
            "market_data": market_data
        }

        recommendations = self.generate_recommendations(all_insights, company_context)
        risk_assessment = self.identify_risks(all_insights, company_context)

        return {
            "insights_report": {
                "company": company_name,
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_insights": len(all_insights),
                    "opportunities_identified": len(opportunities),
                    "risks_identified": len(risks),
                    "recommendations_generated": len(recommendations)
                },
                "insights": all_insights,
                "opportunities": opportunities,
                "risks": risk_assessment,
                "recommendations": recommendations,
                "data_backed": all(i.get("data_backed", False) for i in all_insights)
            }
        }


# Singleton instance
insight_generator = InsightGeneratorService()
