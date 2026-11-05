"""
Go-To-Market (GTM) Strategy Agent.
Formulates positioning, customer acquisition channels, First 100 Customers playbook, pricing tiers, and unit economics.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from models import StructuredIdea, MarketOpportunity, CompetitorAnalysis, MVPRecommendation, GTMStrategy
from utils.llm_client import UnifiedLLMClient

class GTMStrategyAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="GTMStrategyAgent", role="Go-To-Market & Growth Strategy Formulation", llm_client=llm_client)

    def run(self, idea: StructuredIdea, market: MarketOpportunity, competitors: CompetitorAnalysis, mvp: MVPRecommendation) -> GTMStrategy:
        self.log(f"Formulating Go-To-Market strategy for: {idea.title}")

        system_prompt = (
            "You are an elite Chief Commercial Officer and B2B growth marketing strategist. "
            "Formulate an actionable, zero-bullshit Go-To-Market (GTM) strategy for this startup. "
            "Specify the Ideal Customer Profile (ICP), a compelling positioning statement (Geoffrey Moore framework), "
            "3 specific acquisition channels with execution playbooks, a tactical step-by-step 'First 100 Customers' plan, "
            "recommended pricing tiers, and projected unit economics (CAC, LTV, Payback period)."
        )

        user_prompt = (
            f"Startup: {idea.title}\n"
            f"Value Proposition: {idea.core_value_prop}\n"
            f"Target Customer: {idea.target_customer}\n"
            f"Industry: {idea.industry_domain}\n"
            f"TAM: {market.tam_estimate}, SAM: {market.sam_estimate}\n"
            f"Competitor White Space: {', '.join(competitors.white_space_opportunities[:2])}\n"
            f"MVP Launch Time: {mvp.estimated_build_time_weeks} weeks\n\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            '  "ideal_customer_profile": "Detailed ICP definition",\n'
            '  "positioning_statement": "For [target audience] who [need/opportunity], [Product] is a [category] that [benefit]. Unlike [competitors], our product [primary differentiator].",\n'
            '  "primary_acquisition_channels": [\n'
            '    {\n'
            '      "channel": "Channel name",\n'
            '      "details": "Specific execution tactic and strategy"\n'
            '    }\n'
            '  ],\n'
            '  "first_100_customers_playbook": [\n'
            '    "Week 1: Tactic",\n'
            '    "Week 2: Tactic",\n'
            '    "Week 3: Tactic",\n'
            '    "Week 4: Tactic"\n'
            '  ],\n'
            '  "pricing_strategy": {\n'
            '    "model": "Freemium / Tiered SaaS",\n'
            '    "recommended_tiers": [\n'
            '      {"tier": "Starter", "price": "$0 / month", "target": "Trial users"},\n'
            '      {"tier": "Pro", "price": "$39 / month", "target": "Individual professionals"},\n'
            '      {"tier": "Team", "price": "$129 / month", "target": "Growing teams"}\n'
            '    ]\n'
            '  },\n'
            '  "unit_economics_estimate": {\n'
            '    "Target CAC": "$35 - $65",\n'
            '    "Estimated LTV": "$300 - $550",\n'
            '    "LTV / CAC Ratio": "5.2x (Highly Favorable)",\n'
            '    "Target Payback Period": "< 60 Days"\n'
            '  }\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        channels = data.get("primary_acquisition_channels", [
            {
                "channel": "Community-Led Organic Distribution (Product Hunt, IndieHackers, Reddit)",
                "details": "Share transparent build-in-public case studies, teardowns of incumbent tools, and offer 50 free validation audits to founders."
            },
            {
                "channel": "Strategic Incubator & Accelerator Partnerships",
                "details": "Partner with regional startup studios, university entrepreneurship hubs, and angel syndicates to become their recommended idea evaluation tool."
            },
            {
                "channel": "Targeted Outbound & Interactive Micro-Tools",
                "details": "Launch a free standalone 'Startup TAM Calculator' web utility that drives organic SEO traffic and converts 8-12% into full platform signups."
            }
        ])

        playbook = data.get("first_100_customers_playbook", [
            "Week 1: Direct outreach to 100 active founders on Twitter/LinkedIn, offering a personalized 5-page validation report on their current venture.",
            "Week 2: Public launch on Product Hunt and Hacker News Show HN with demo video and live interactive examples.",
            "Week 3: Host a live teardown session analyzing submitted startup ideas in founder Slack/Discord communities.",
            "Week 4: Activate user referral loop: users who refer 2 fellow entrepreneurs unlock premium investor export features."
        ])

        pricing = data.get("pricing_strategy", {
            "model": "Freemium + Tiered SaaS",
            "recommended_tiers": [
                {"tier": "Explorer (Free)", "price": "$0", "target": "1 Full Validation + Basic Overview"},
                {"tier": "Founder Pro", "price": "$29 / month", "target": "Unlimited validations, PDF exports & Conversational Advisor"},
                {"tier": "Studio / Venture", "price": "$119 / month", "target": "Batch processing, team collaboration & custom branding"}
            ]
        })

        unit_economics = data.get("unit_economics_estimate", {
            "Target CAC": "$28 - $50 (Blended Organic/Outbound)",
            "Estimated LTV": "$260 - $480",
            "LTV / CAC Ratio": "5.6x (Healthy Growth Engine)",
            "Target Payback Period": "< 45 Days"
        })

        return GTMStrategy(
            ideal_customer_profile=data.get("ideal_customer_profile", f"Early-stage venture builders, solo technical founders, startup incubators, and boutique consultancies in {idea.industry_domain}."),
            positioning_statement=data.get("positioning_statement", f"For entrepreneurs who need rapid, rigorous market validation, {idea.title} provides comprehensive, data-backed viability reports in under 3 minutes, unlike slow, expensive manual consulting agencies."),
            primary_acquisition_channels=channels,
            first_100_customers_playbook=playbook,
            pricing_strategy=pricing,
            unit_economics_estimate=unit_economics
        )
