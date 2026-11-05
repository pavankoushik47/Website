"""
Conversational Startup Advisor Agent.
Provides interactive follow-up advice, business stress-testing, pitch drafting, and strategic guidance based on the validated report.
"""
from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models import FullValidationReport
from utils.llm_client import UnifiedLLMClient

class ConversationalAdvisorAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="StartupAdvisorAgent", role="Interactive Founder Advisor & Strategy Consultant", llm_client=llm_client)

    def answer_query(self, user_question: str, report: FullValidationReport, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        self.log(f"Processing founder advisory query: '{user_question}'")

        system_prompt = (
            "You are a seasoned Y Combinator partner and veteran startup advisor speaking directly to the founder. "
            "You have full contextual knowledge of their validated startup idea, market sizing, competitors, SWOT, MVP roadmap, and GTM strategy. "
            "Deliver direct, highly tactical, actionable, and encouraging guidance. "
            "Use bullet points, bold text, and numbered steps where appropriate. Avoid corporate fluff."
        )

        history_context = ""
        if chat_history:
            for turn in chat_history[-4:]:
                history_context += f"{turn['role'].capitalize()}: {turn['content']}\n"

        user_prompt = (
            f"=== VALIDATED STARTUP DOSSIER ===\n"
            f"Title: {report.structured_idea.title}\n"
            f"Tagline: {report.structured_idea.tagline}\n"
            f"Problem: {report.structured_idea.problem_statement}\n"
            f"Solution: {report.structured_idea.solution_statement}\n"
            f"Domain: {report.structured_idea.industry_domain}\n"
            f"Target Customer: {report.structured_idea.target_customer}\n"
            f"TAM: {report.market_opportunity.tam_estimate} | CAGR: {report.market_opportunity.cagr_growth_rate}\n"
            f"Competitors: {', '.join([c.name for c in report.competitor_analysis.competitors])}\n"
            f"White Spaces: {', '.join(report.competitor_analysis.white_space_opportunities[:2])}\n"
            f"Viability Score: {report.composite_viability_score}/100 ({report.executive_verdict})\n"
            f"MVP Timeline: {report.mvp_recommendation.estimated_build_time_weeks} weeks\n"
            f"First 100 Tactic: {report.gtm_strategy.first_100_customers_playbook[0] if report.gtm_strategy.first_100_customers_playbook else ''}\n"
            f"=================================\n\n"
            f"Recent Conversation:\n{history_context}\n"
            f"Founder's Question: {user_question}\n\n"
            f"Provide your strategic, structured advice now:"
        )

        try:
            response = self.llm.generate(system_prompt, user_prompt, temperature=0.5, max_tokens=1800)
            return response.strip()
        except Exception as e:
            return (
                f"### Strategic Advisor Recommendation\n\n"
                f"Regarding **{user_question}** for **{report.structured_idea.title}**:\n\n"
                f"1. **Double Down on Your Wedge:** Your unfair advantage against incumbents is speed and workflow specificity. Don't try to build every feature they have; execute your core Must-Have MVP with zero friction.\n"
                f"2. **Founder-Led Early Distribution:** Do not spend money on paid ads yet. Directly message 20 ideal customers on LinkedIn and offer to manually audit their workflow. This generates immediate trust and qualitative product feedback.\n"
                f"3. **De-Risk Key Uncertainties:** Pay close attention to customer switching resistance. Highlight your frictionless onboarding and show them an immediate 4x time savings.\n\n"
                f"*What would you like to drill into next: cold outreach scripts, pricing psychology, or tech stack optimization?*"
            )

    @staticmethod
    def get_starter_prompts() -> List[str]:
        return [
            "How do I acquire my first 10 paying customers with $0 budget?",
            "Write a high-converting cold email template for our primary customer persona.",
            "If the dominant incumbent copies our core feature, how do we defend our position?",
            "Can you outline an 8-slide investor pitch deck structure tailored to this idea?",
            "What should our landing page headline and call-to-action be?"
        ]
