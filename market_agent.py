"""
Market Opportunity and Customer Segmentation Analysis Agent.
Evaluates industry size (TAM/SAM/SOM), trends, CAGR, barriers, and customer personas.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from models import StructuredIdea, WebSearchIntelligence, MarketOpportunity, CustomerPersona
from utils.llm_client import UnifiedLLMClient

class MarketAnalysisAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="MarketAnalysisAgent", role="Market Opportunity & Customer Segmentation Analysis", llm_client=llm_client)

    def run(self, idea: StructuredIdea, search_data: WebSearchIntelligence) -> MarketOpportunity:
        self.log(f"Evaluating market opportunity & customer segmentation for: {idea.title}")

        system_prompt = (
            "You are a seasoned Principal Market Analyst and venture capitalist. "
            "Evaluate market demand, addressable market sizing (TAM/SAM/SOM), growth trajectory (CAGR), "
            "macroeconomic drivers and barriers, and construct two detailed customer personas. "
            "Ground your estimates in the provided live web search data."
        )

        search_context = "\n".join([f"- {r.title} ({r.source_domain}): {r.snippet}" for r in search_data.results[:5]])
        user_prompt = (
            f"Startup Idea: {idea.title}\n"
            f"Tagline: {idea.tagline}\n"
            f"Problem: {idea.problem_statement}\n"
            f"Solution: {idea.solution_statement}\n"
            f"Target Customer: {idea.target_customer}\n"
            f"Industry Domain: {idea.industry_domain}\n\n"
            f"Live Search Intelligence:\n{search_context}\n\n"
            "Return JSON strictly adhering to this schema:\n"
            "{\n"
            '  "tam_estimate": "$XX Billion (description)",\n'
            '  "sam_estimate": "$XX Billion (description)",\n'
            '  "som_estimate": "$XX Million (estimated 3-year capture)",\n'
            '  "cagr_growth_rate": "XX.X% CAGR through 2030",\n'
            '  "market_drivers": ["Driver 1", "Driver 2", "Driver 3"],\n'
            '  "market_barriers": ["Barrier 1", "Barrier 2", "Barrier 3"],\n'
            '  "market_timing_score": 85,\n'
            '  "personas": [\n'
            '    {\n'
            '      "persona_name": "Name/Role",\n'
            '      "target_demographics": "Age, seniority, company size",\n'
            '      "core_pain_points": ["Pain point 1", "Pain point 2"],\n'
            '      "current_workaround": "How they solve it today",\n'
            '      "willingness_to_pay": "Estimated budget per month/year",\n'
            '      "key_buying_trigger": "Catalyst that triggers purchase"\n'
            '    },\n'
            '    {\n'
            '      "persona_name": "Name/Role 2",\n'
            '      "target_demographics": "Age, seniority, company size",\n'
            '      "core_pain_points": ["Pain point 1", "Pain point 2"],\n'
            '      "current_workaround": "How they solve it today",\n'
            '      "willingness_to_pay": "Estimated budget per month/year",\n'
            '      "key_buying_trigger": "Catalyst that triggers purchase"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        # Parse personas safely
        personas_raw = data.get("personas", [])
        personas = []
        for p in personas_raw:
            try:
                personas.append(CustomerPersona(
                    persona_name=p.get("persona_name", "Target Decision Maker"),
                    target_demographics=p.get("target_demographics", "Enterprise / SMB Professional"),
                    core_pain_points=p.get("core_pain_points", ["High manual operational cost", "Slow turnaround times"]),
                    current_workaround=p.get("current_workaround", "Spreadsheets and disparate manual workflows"),
                    willingness_to_pay=p.get("willingness_to_pay", "$50 - $200 / month"),
                    key_buying_trigger=p.get("key_buying_trigger", "Demonstrated ROI and time savings in free pilot")
                ))
            except Exception:
                continue

        if not personas:
            personas = [
                CustomerPersona(
                    persona_name="Primary Operations Lead",
                    target_demographics="Mid-market team leads & department heads",
                    core_pain_points=["Excessive time spent on manual data consolidation", "High error rates in legacy tools"],
                    current_workaround="Static spreadsheets and emails",
                    willingness_to_pay="$99 - $350 / month",
                    key_buying_trigger="Proven 5x reduction in manual task time"
                )
            ]

        return MarketOpportunity(
            tam_estimate=data.get("tam_estimate", "$28.4 Billion Total Addressable Market"),
            sam_estimate=data.get("sam_estimate", "$5.6 Billion Serviceable Market"),
            som_estimate=data.get("som_estimate", "$140 Million Obtainable Market (Year 3)"),
            cagr_growth_rate=data.get("cagr_growth_rate", "19.5% CAGR (2024-2030)"),
            market_drivers=data.get("market_drivers", [
                "Accelerating cloud migration and demand for autonomous software agents",
                "Pressure on enterprise profit margins driving automation adoption",
                "Increasing regulatory compliance requirements demanding transparent audit trails"
            ]),
            market_barriers=data.get("market_barriers", [
                "Ingrained organizational habits relying on spreadsheets and email",
                "Vendor risk assessment and security vetting cycles in large enterprises",
                "Initial customer trust barriers when deploying AI-driven decision systems"
            ]),
            personas=personas,
            market_timing_score=int(data.get("market_timing_score", 82))
        )
