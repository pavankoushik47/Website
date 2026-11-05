"""
SWOT and Risk Analysis Agent.
Generates structured SWOT matrix, categorized execution risk register, and feasibility/viability scores.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from models import StructuredIdea, MarketOpportunity, CompetitorAnalysis, SWOTAndRiskReport, RiskItem
from utils.llm_client import UnifiedLLMClient

class SWOTAndRiskAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="SWOTAndRiskAgent", role="SWOT & Execution Risk Assessment", llm_client=llm_client)

    def run(self, idea: StructuredIdea, market: MarketOpportunity, competitors: CompetitorAnalysis) -> SWOTAndRiskReport:
        self.log(f"Conducting SWOT & Risk assessment for: {idea.title}")

        system_prompt = (
            "You are a rigorous startup venture partner and risk officer. "
            "Analyze the startup idea, market sizing, and competitive landscape. "
            "Formulate a balanced 4-quadrant SWOT matrix. "
            "Identify 4-5 concrete, severe risks across Execution, Regulatory/Legal, Technical/AI, Financial/Runway, and Market Adoption, "
            "specifying likelihood, severity, and actionable mitigations. "
            "Provide quantitative feasibility and viability scores (0-100)."
        )

        user_prompt = (
            f"Startup: {idea.title}\n"
            f"Value Proposition: {idea.core_value_prop}\n"
            f"Target Customer: {idea.target_customer}\n"
            f"Domain: {idea.industry_domain}\n"
            f"Market Size: TAM {market.tam_estimate}, CAGR {market.cagr_growth_rate}\n"
            f"Competitor Saturation: {competitors.market_saturation_level}\n"
            f"White Space: {', '.join(competitors.white_space_opportunities[:2])}\n\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            '  "strengths": ["Strength 1", "Strength 2", "Strength 3", "Strength 4"],\n'
            '  "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],\n'
            '  "opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3"],\n'
            '  "threats": ["Threat 1", "Threat 2", "Threat 3"],\n'
            '  "feasibility_score": 82,\n'
            '  "market_viability_score": 85,\n'
            '  "execution_complexity": "Moderate" | "Low" | "High" | "Extreme",\n'
            '  "overall_risk_rating": "Low" | "Moderate" | "High" | "Critical",\n'
            '  "risk_items": [\n'
            '    {\n'
            '      "category": "Market Adoption",\n'
            '      "risk_title": "Risk name",\n'
            '      "description": "Why this risk exists",\n'
            '      "likelihood": "Low" | "Medium" | "High",\n'
            '      "severity": "Low" | "Medium" | "High",\n'
            '      "mitigation_strategy": "Actionable tactic to de-risk"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        # Parse risk items safely
        risks_raw = data.get("risk_items", [])
        risk_items: List[RiskItem] = []
        for r in risks_raw:
            try:
                risk_items.append(RiskItem(
                    category=r.get("category", "Execution"),
                    risk_title=r.get("risk_title", "Operational Execution Friction"),
                    description=r.get("description", "Challenges in rolling out feature set efficiently."),
                    likelihood=r.get("likelihood", "Medium"),
                    severity=r.get("severity", "Medium"),
                    mitigation_strategy=r.get("mitigation_strategy", "Prioritize lean MVP sprint and early customer feedback loops.")
                ))
            except Exception:
                continue

        if not risk_items:
            risk_items = [
                RiskItem(
                    category="Market Adoption",
                    risk_title="Customer habit inertia towards legacy spreadsheets",
                    description="Prospective buyers may hesitate to migrate established workflows.",
                    likelihood="Medium",
                    severity="High",
                    mitigation_strategy="Provide zero-friction self-serve onboarding, one-click spreadsheet imports, and instant value demonstration."
                ),
                RiskItem(
                    category="Technical/AI",
                    risk_title="LLM hallucination & output reliability",
                    description="Domain-critical validation requires reliable reasoning; inaccurate data can hurt founder trust.",
                    likelihood="Medium",
                    severity="High",
                    mitigation_strategy="Implement multi-agent cross-verification, structured JSON schemas, and confidence scoring."
                ),
                RiskItem(
                    category="Financial/Runway",
                    risk_title="High Customer Acquisition Cost prior to PMF",
                    description="Paid acquisition can burn cash prematurely before conversion funnels are optimized.",
                    likelihood="Medium",
                    severity="Medium",
                    mitigation_strategy="Rely strictly on organic founder communities, content-led growth, and interactive free micro-tools."
                ),
                RiskItem(
                    category="Regulatory/Legal",
                    risk_title="Data security and client confidentiality compliance",
                    description="Commercial users require strict privacy standards and assurance that proprietary ideas are not leaked.",
                    likelihood="Low",
                    severity="High",
                    mitigation_strategy="Ensure zero-data-retention enterprise agreements with LLM providers and local-first data encryption."
                )
            ]

        # Enforce valid scores
        feasibility = int(data.get("feasibility_score", 82))
        viability = int(data.get("market_viability_score", 85))
        feasibility = max(10, min(99, feasibility))
        viability = max(10, min(99, viability))

        return SWOTAndRiskReport(
            strengths=data.get("strengths", [
                "Sharp vertical value proposition tailored directly to acute user friction",
                "Lightweight modern architecture delivering 10x faster execution than legacy incumbents",
                "Significantly lower infrastructure and customer operating cost structure",
                "Autonomous agentic workflow execution eliminating repetitive manual labor"
            ]),
            weaknesses=data.get("weaknesses", [
                "Early-stage brand lacking established case studies and industry references",
                "Initial dependence on third-party API providers and token rate limits",
                "Limited initial marketing budget requiring high-efficiency organic distribution"
            ]),
            opportunities=data.get("opportunities", [
                "Vast underserved mid-market priced out by $15,000+ enterprise legacy contracts",
                "Global scalability enabled by cloud-native deployment with minimal marginal cost",
                "Platform expansion: opening APIs and agentic workflows to third-party developers"
            ]),
            threats=data.get("threats", [
                "Incumbents rapidly bundling basic generative AI features into existing suites",
                "Potential fluctuations in underlying foundation model API pricing",
                "Risk of market noise and generic AI tools causing prospective buyer fatigue"
            ]),
            risk_items=risk_items,
            feasibility_score=feasibility,
            market_viability_score=viability,
            execution_complexity=data.get("execution_complexity", "Moderate"),
            overall_risk_rating=data.get("overall_risk_rating", "Moderate")
        )
