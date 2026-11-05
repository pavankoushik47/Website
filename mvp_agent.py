"""
MVP Feature Recommendation Agent.
Prioritizes feature set using the MoSCoW framework, designs release roadmap, and suggests tech stack.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from models import StructuredIdea, CompetitorAnalysis, SWOTAndRiskReport, MVPRecommendation, MVPFeature
from utils.llm_client import UnifiedLLMClient

class MVPRecommendationAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="MVPRecommendationAgent", role="MVP Feature Roadmap & Prioritization", llm_client=llm_client)

    def run(self, idea: StructuredIdea, competitors: CompetitorAnalysis, swot_risk: SWOTAndRiskReport) -> MVPRecommendation:
        self.log(f"Formulating MVP feature roadmap and MoSCoW prioritization for: {idea.title}")

        system_prompt = (
            "You are a seasoned Head of Product and agile startup technical founder. "
            "Based on the startup idea, competitive gaps, and execution risks, define a lean, high-impact MVP. "
            "Use the MoSCoW framework (Must-Have, Should-Have, Could-Have, Won't-Have for v1). "
            "Provide realistic development effort, user impact, a 3-phase sprint roadmap, tech stack, build duration, and primary success KPI."
        )

        user_prompt = (
            f"Startup: {idea.title}\n"
            f"Tagline: {idea.tagline}\n"
            f"Problem: {idea.problem_statement}\n"
            f"Solution: {idea.solution_statement}\n"
            f"Competitor White Spaces: {', '.join(competitors.white_space_opportunities[:2])}\n"
            f"Execution Complexity: {swot_risk.execution_complexity}\n"
            f"Feasibility Score: {swot_risk.feasibility_score}/100\n\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            '  "estimated_build_time_weeks": 4,\n'
            '  "estimated_mvp_budget_usd": "$2,000 - $5,000",\n'
            '  "critical_success_metric": "Clear measurable North Star KPI (e.g. 50 active users completing core workflow)",\n'
            '  "recommended_tech_stack": {\n'
            '    "Frontend": "Tech name",\n'
            '    "Backend": "Tech name",\n'
            '    "AI/LLM": "Tech name",\n'
            '    "Database": "Tech name",\n'
            '    "Hosting": "Tech name"\n'
            '  },\n'
            '  "core_features": [\n'
            '    {\n'
            '      "feature_name": "Feature 1",\n'
            '      "moscow_category": "Must-Have",\n'
            '      "description": "Clear explanation",\n'
            '      "user_impact": "High",\n'
            '      "development_effort": "Low" | "Medium" | "High",\n'
            '      "sprint_phase": "Phase 1: Core Engine"\n'
            '    },\n'
            '    {\n'
            '      "feature_name": "Feature 2",\n'
            '      "moscow_category": "Must-Have",\n'
            '      "description": "Clear explanation",\n'
            '      "user_impact": "High",\n'
            '      "development_effort": "Medium",\n'
            '      "sprint_phase": "Phase 1: Core Engine"\n'
            '    },\n'
            '    {\n'
            '      "feature_name": "Feature 3",\n'
            '      "moscow_category": "Should-Have",\n'
            '      "description": "Clear explanation",\n'
            '      "user_impact": "High",\n'
            '      "development_effort": "Medium",\n'
            '      "sprint_phase": "Phase 2: Enhanced Value"\n'
            '    },\n'
            '    {\n'
            '      "feature_name": "Feature 4",\n'
            '      "moscow_category": "Could-Have",\n'
            '      "description": "Clear explanation",\n'
            '      "user_impact": "Medium",\n'
            '      "development_effort": "Low",\n'
            '      "sprint_phase": "Phase 2: Enhanced Value"\n'
            '    },\n'
            '    {\n'
            '      "feature_name": "Feature 5",\n'
            '      "moscow_category": "Won\'t-Have (v1)",\n'
            '      "description": "Clear explanation why deferred",\n'
            '      "user_impact": "Low",\n'
            '      "development_effort": "High",\n'
            '      "sprint_phase": "Phase 3: Scale & Ecosystem"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        # Parse features safely
        features_raw = data.get("core_features", [])
        features: List[MVPFeature] = []
        for f in features_raw:
            try:
                features.append(MVPFeature(
                    feature_name=f.get("feature_name", "Core Feature"),
                    moscow_category=f.get("moscow_category", "Must-Have"),
                    description=f.get("description", "Essential component for initial validation."),
                    user_impact=f.get("user_impact", "High"),
                    development_effort=f.get("development_effort", "Medium"),
                    sprint_phase=f.get("sprint_phase", "Phase 1: Core Engine")
                ))
            except Exception:
                continue

        if not features:
            features = [
                MVPFeature(
                    feature_name="Streamlined Intake & Workflow Setup",
                    moscow_category="Must-Have",
                    description="Intuitive 2-minute onboarding interface for users to submit tasks or inputs.",
                    user_impact="High",
                    development_effort="Low",
                    sprint_phase="Phase 1: Core Engine"
                ),
                MVPFeature(
                    feature_name="Automated AI Processing & Execution Pipeline",
                    moscow_category="Must-Have",
                    description="The foundational autonomous workflow engine that replaces manual labor.",
                    user_impact="High",
                    development_effort="Medium",
                    sprint_phase="Phase 1: Core Engine"
                ),
                MVPFeature(
                    feature_name="Executive Dashboard & Verifiable Export Reports",
                    moscow_category="Must-Have",
                    description="Visual summary of results with downloadable, client-ready PDF/Markdown exports.",
                    user_impact="High",
                    development_effort="Low",
                    sprint_phase="Phase 1: Core Engine"
                ),
                MVPFeature(
                    feature_name="Interactive Follow-Up Query Assistant",
                    moscow_category="Should-Have",
                    description="Contextual chat interface for users to refine results or request tweaks.",
                    user_impact="High",
                    development_effort="Medium",
                    sprint_phase="Phase 2: Enhanced Value"
                ),
                MVPFeature(
                    feature_name="Custom Team Workspaces & Sharing Links",
                    moscow_category="Could-Have",
                    description="Multi-user collaboration allowing teammates to comment and review runs.",
                    user_impact="Medium",
                    development_effort="Medium",
                    sprint_phase="Phase 2: Enhanced Value"
                ),
                MVPFeature(
                    feature_name="Full Enterprise SSO & Custom Compliance Auditing",
                    moscow_category="Won't-Have (v1)",
                    description="Heavyweight enterprise integrations deferred until post-revenue product validation.",
                    user_impact="Low",
                    development_effort="High",
                    sprint_phase="Phase 3: Scale & Ecosystem"
                )
            ]

        tech_stack = data.get("recommended_tech_stack", {
            "Frontend": "Modern Streamlit / Next.js with React",
            "Backend": "Python 3.12 (FastAPI / Asynchronous Pipeline)",
            "AI / LLM Layer": "LangChain + Groq / OpenAI / Gemini API",
            "Data & Search": "Tavily Search API + PostgreSQL",
            "Deployment": "Streamlit Cloud / Railway / Vercel"
        })

        return MVPRecommendation(
            core_features=features,
            recommended_tech_stack=tech_stack,
            estimated_build_time_weeks=int(data.get("estimated_build_time_weeks", 4)),
            estimated_mvp_budget_usd=data.get("estimated_mvp_budget_usd", "$2,000 - $5,000"),
            critical_success_metric=data.get("critical_success_metric", "At least 35 verified target users completing full end-to-end workflow with >= 80% satisfaction score.")
        )
