"""
Competitor Discovery and Comparison Agent.
Identifies existing players, compares feature offerings, highlights market gaps, and formulates defensibility.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from models import StructuredIdea, WebSearchIntelligence, MarketOpportunity, CompetitorAnalysis, Competitor
from utils.llm_client import UnifiedLLMClient

class CompetitorAnalysisAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="CompetitorAnalysisAgent", role="Competitor Discovery & Gap Analysis", llm_client=llm_client)

    def run(self, idea: StructuredIdea, search_data: WebSearchIntelligence, market: MarketOpportunity) -> CompetitorAnalysis:
        self.log(f"Conducting competitor discovery and gap analysis for: {idea.title}")

        system_prompt = (
            "You are a strategic competitive intelligence expert. Analyze the competitive landscape for this startup. "
            "Identify 3-4 distinct competitors across Direct, Indirect, and Substitute categories. "
            "Construct a comparative feature matrix, pinpoint unfilled white space opportunities, and articulate a sustainable defensibility moat."
        )

        search_context = "\n".join([f"- {r.title} ({r.source_domain}): {r.snippet}" for r in search_data.results[:5]])
        user_prompt = (
            f"Startup Title: {idea.title}\n"
            f"Core Value Prop: {idea.core_value_prop}\n"
            f"Target Customer: {idea.target_customer}\n"
            f"Domain: {idea.industry_domain}\n"
            f"Market Size: TAM {market.tam_estimate}, SAM {market.sam_estimate}\n\n"
            f"Web Intelligence Snippets:\n{search_context}\n\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            '  "market_saturation_level": "Low" | "Moderate" | "High" | "Saturated",\n'
            '  "competitors": [\n'
            '    {\n'
            '      "name": "Competitor Name",\n'
            '      "competitor_type": "Direct" | "Indirect" | "Substitute",\n'
            '      "description": "Overview of their offering",\n'
            '      "strengths": ["Strength 1", "Strength 2"],\n'
            '      "weaknesses": ["Weakness 1", "Weakness 2"],\n'
            '      "pricing_model": "Pricing details",\n'
            '      "estimated_market_position": "Market leader / Challenger / Niche"\n'
            '    }\n'
            '  ],\n'
            '  "feature_matrix": {\n'
            '    "Autonomous AI Workflows": {"Comp 1": false, "Comp 2": false, "This Startup": true},\n'
            '    "Real-time Data Integration": {"Comp 1": true, "Comp 2": false, "This Startup": true},\n'
            '    "Instant Self-Serve Setup": {"Comp 1": false, "Comp 2": true, "This Startup": true},\n'
            '    "Transparent SMB Pricing": {"Comp 1": false, "Comp 2": true, "This Startup": true}\n'
            '  },\n'
            '  "white_space_opportunities": [\n'
            '    "White space gap 1",\n'
            '    "White space gap 2",\n'
            '    "White space gap 3"\n'
            '  ],\n'
            '  "defensibility_moat": "Explanation of sustainable defensibility (data moat, switching costs, workflow lock-in)"\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        # Parse competitors safely
        competitors_raw = data.get("competitors", [])
        competitors = []
        for c in competitors_raw:
            try:
                competitors.append(Competitor(
                    name=c.get("name", "Industry Incumbent"),
                    competitor_type=c.get("competitor_type", "Direct"),
                    description=c.get("description", "Established provider in the space"),
                    strengths=c.get("strengths", ["Established customer base", "Brand recognition"]),
                    weaknesses=c.get("weaknesses", ["High enterprise cost", "Outdated user experience"]),
                    pricing_model=c.get("pricing_model", "Subscription or Enterprise Contract"),
                    estimated_market_position=c.get("estimated_market_position", "Incumbent")
                ))
            except Exception:
                continue

        if not competitors:
            competitors = [
                Competitor(
                    name="Legacy Enterprise Suite",
                    competitor_type="Direct",
                    description="Dominant incumbent software suite with comprehensive enterprise features.",
                    strengths=["Broad brand trust", "Deep regulatory certifications"],
                    weaknesses=["High upfront cost ($12k+/year)", "Requires extensive consultant onboarding"],
                    pricing_model="Annual enterprise contract",
                    estimated_market_position="Market Leader"
                ),
                Competitor(
                    name="Niche Point Solution",
                    competitor_type="Indirect",
                    description="Cloud tool addressing a single step of the broader workflow.",
                    strengths=["Simple onboarding", "Low starting price"],
                    weaknesses=["Lacks autonomous multi-step reasoning", "Isolated data silos"],
                    pricing_model="$49/month SaaS",
                    estimated_market_position="Niche Player"
                ),
                Competitor(
                    name="In-House Spreadsheets & Outsourced Contractors",
                    competitor_type="Substitute",
                    description="Internal manual processes using Google Sheets, email threads, and outsourced virtual assistants.",
                    strengths=["Zero software purchasing friction", "Customized to legacy team habits"],
                    weaknesses=["Completely unscalable", "Prone to high human error", "Slow turnaround"],
                    pricing_model="High hidden labor costs",
                    estimated_market_position="Default Inertia"
                )
            ]

        feature_matrix = data.get("feature_matrix", {})
        if not feature_matrix:
            c1_name = competitors[0].name
            c2_name = competitors[1].name if len(competitors) > 1 else "Competitor B"
            feature_matrix = {
                "Agentic AI Automation": {c1_name: False, c2_name: False, "This Startup": True},
                "Real-Time Data Verification": {c1_name: True, c2_name: False, "This Startup": True},
                "Instant Self-Serve Onboarding": {c1_name: False, c2_name: True, "This Startup": True},
                "Accessible SMB Pricing (<$50/mo)": {c1_name: False, c2_name: True, "This Startup": True},
                "End-to-End Orchestrated Workflow": {c1_name: False, c2_name: False, "This Startup": True}
            }

        return CompetitorAnalysis(
            competitors=competitors,
            market_saturation_level=data.get("market_saturation_level", "Moderate"),
            feature_matrix=feature_matrix,
            white_space_opportunities=data.get("white_space_opportunities", [
                "Underserved Mid-Market: Enterprise players ignore SMBs, while entry tools lack depth.",
                "Autonomous Execution: Competitors provide manual dashboards rather than agentic automated resolution.",
                "Rapid Time-to-Value: Getting users up and running in minutes rather than weeks."
            ]),
            defensibility_moat=data.get("defensibility_moat", "Compounding proprietary vertical workflow data, domain-tuned agent prompts, and high customer switching costs through daily operational lock-in.")
        )
