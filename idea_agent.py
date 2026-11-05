"""
Idea Extraction Agent.
Parses a founder's raw 2-3 line startup submission into a structured, formalized idea schema.
"""
from typing import Optional
from agents.base_agent import BaseAgent
from models import IdeaSubmission, StructuredIdea
from utils.llm_client import UnifiedLLMClient

class IdeaExtractionAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="IdeaExtractionAgent", role="Structured Startup Idea Extraction", llm_client=llm_client)

    def run(self, submission: IdeaSubmission) -> StructuredIdea:
        self.log(f"Extracting structured startup parameters from raw idea...")

        system_prompt = (
            "You are a startup incubator director and venture analyst. "
            "A founder has submitted a raw 2-3 line startup idea. "
            "Extract and formalize this into a structured venture concept: working title, elevator tagline, "
            "precise problem statement, innovative solution statement, primary target customer, core unique value proposition, "
            "industry domain category, monetization model, and 5 search keywords."
        )

        user_prompt = (
            f"Founder Submission:\n\"{submission.raw_idea}\"\n\n"
            f"Optional Domain Hint: {submission.domain_hint or 'Auto-detect'}\n"
            f"Target Geography: {submission.target_geography or 'Global'}\n"
            f"Monetization Preference: {submission.monetization_preference or 'Best fit SaaS / Marketplace'}\n\n"
            "Return JSON matching this schema:\n"
            "{\n"
            '  "title": "Crisp Startup Title (1-3 words)",\n'
            '  "tagline": "One-line punchy elevator tagline",\n'
            '  "problem_statement": "The core acute problem being solved",\n'
            '  "solution_statement": "The precise product solution",\n'
            '  "target_customer": "Primary buyer or user profile",\n'
            '  "core_value_prop": "Unique value proposition and unfair advantage",\n'
            '  "industry_domain": "Primary market vertical (e.g. HealthTech, B2B SaaS, FinTech, PropTech)",\n'
            '  "monetization_model": "Primary revenue mechanism",\n'
            '  "key_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        title = data.get("title", "InnovateFlow")
        return StructuredIdea(
            title=title,
            tagline=data.get("tagline", "Autonomous intelligence for modern workflows."),
            problem_statement=data.get("problem_statement", "Founders and professionals waste excessive hours on manual research, analysis, and execution bottlenecks."),
            solution_statement=data.get("solution_statement", "An integrated multi-agent automation platform that delivers end-to-end data synthesis and execution."),
            target_customer=data.get("target_customer", "Early-stage founders, SMB operators, and independent knowledge workers."),
            core_value_prop=data.get("core_value_prop", "10x faster execution with automated verification, reduced labor costs, and actionable strategic reports."),
            industry_domain=data.get("industry_domain", submission.domain_hint or "AI & Enterprise Software"),
            monetization_model=data.get("monetization_model", submission.monetization_preference or "Freemium + Tiered SaaS Subscription"),
            key_keywords=data.get("key_keywords", [title.lower(), "startup automation", "market intelligence", "workflow", "ai"])
        )
