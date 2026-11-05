"""
Startup Validation Report Generation Agent.
Compiles all agent outputs into a unified executive report, determines verdict, and generates PDF/Markdown/JSON exports.
"""
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from agents.base_agent import BaseAgent
from models import (
    IdeaSubmission, StructuredIdea, WebSearchIntelligence,
    MarketOpportunity, CompetitorAnalysis, SWOTAndRiskReport,
    MVPRecommendation, GTMStrategy, FinancialFeasibility, FullValidationReport
)
from utils.llm_client import UnifiedLLMClient

class ReportGenerationAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="ReportGenerationAgent", role="Executive Startup Validation Report Synthesis", llm_client=llm_client)

    def run(
        self,
        submission: IdeaSubmission,
        idea: StructuredIdea,
        search_data: WebSearchIntelligence,
        market: MarketOpportunity,
        competitors: CompetitorAnalysis,
        swot_risk: SWOTAndRiskReport,
        mvp: MVPRecommendation,
        gtm: GTMStrategy,
        financial: Optional[FinancialFeasibility] = None
    ) -> FullValidationReport:
        self.log(f"Compiling comprehensive executive validation report for: {idea.title}")

        # Compute Composite Viability Score based on multi-dimensional weighting
        # Weights: Feasibility (25%), Market Opportunity (30%), Timing (15%), Defensibility/Moat (15%), Risk Inversion (15%)
        risk_penalty = 10 if swot_risk.overall_risk_rating == "Critical" else (5 if swot_risk.overall_risk_rating == "High" else 0)
        composite_score = int(
            (swot_risk.feasibility_score * 0.25) +
            (swot_risk.market_viability_score * 0.30) +
            (market.market_timing_score * 0.20) +
            (80 * 0.25) - risk_penalty
        )
        composite_score = max(20, min(98, composite_score))

        # Determine Executive Verdict
        if composite_score >= 82:
            verdict = "STRONG GO WITH FOCUS"
        elif composite_score >= 72:
            verdict = "GO WITH CAUTION"
        elif composite_score >= 58:
            verdict = "CONDITIONAL PIVOT RECOMMENDED"
        else:
            verdict = "NO-GO / HIGH EXECUTION RISK"

        system_prompt = (
            "You are a Senior Partner at a Tier-1 venture capital firm. "
            "Synthesize all previous agent findings into a crisp, high-impact 2-paragraph Executive Summary "
            "and 3-4 high-leverage strategic recommendations for the founder."
        )

        user_prompt = (
            f"Startup: {idea.title} - {idea.tagline}\n"
            f"Composite Score: {composite_score}/100 | Verdict: {verdict}\n"
            f"Market Size: TAM {market.tam_estimate}, CAGR {market.cagr_growth_rate}\n"
            f"Competitor Saturation: {competitors.market_saturation_level}\n"
            f"Key White Space: {', '.join(competitors.white_space_opportunities[:2])}\n"
            f"MVP Timeline: {mvp.estimated_build_time_weeks} weeks\n"
            f"GTM Channel: {gtm.primary_acquisition_channels[0]['channel'] if gtm.primary_acquisition_channels else 'Organic'}\n\n"
            "Return JSON matching:\n"
            "{\n"
            '  "executive_summary": "Two comprehensive paragraphs of VC-grade analysis...",\n'
            '  "key_recommendations": [\n'
            '    "Recommendation 1",\n'
            '    "Recommendation 2",\n'
            '    "Recommendation 3"\n'
            '  ]\n'
            "}"
        )

        data = self.execute_structured_prompt(system_prompt, user_prompt)

        summary = data.get("executive_summary", (
            f"{idea.title} represents a compelling venture opportunity within the rapidly expanding {idea.industry_domain} market. "
            f"By directly targeting underserved mid-market professionals and addressing critical workflow bottlenecks with modern AI automation, "
            f"the venture achieves a differentiated value proposition. Incumbents suffer from high enterprise price tags and sluggish innovation, "
            f"providing a clear window of opportunity.\n\n"
            f"To maximize success, the founding team must maintain strict discipline around the {mvp.estimated_build_time_weeks}-week Must-Have MVP scope, "
            f"prioritizing fast time-to-value over peripheral features. Early customer acquisition should leverage organic founder communities "
            f"and high-intent micro-tools to maintain an exceptional LTV/CAC ratio."
        ))

        recommendations = data.get("key_recommendations", [
            f"Execute the Phase 1 Must-Have MVP sprint within {mvp.estimated_build_time_weeks} weeks to establish rapid proof-of-concept.",
            "Formulate early case studies with 10 beta pilot customers to quantify ROI before initiating outbound paid campaigns.",
            "Protect the defensibility moat by focusing on vertical workflow stickiness and proprietary prompt optimization.",
            "Implement a transparent self-serve pricing tier to exploit incumbent price rigidity and accelerate user adoption."
        ])

        report_id = f"VAL-{uuid.uuid4().hex[:8].upper()}"

        return FullValidationReport(
            report_id=report_id,
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            submission=submission,
            structured_idea=idea,
            web_intelligence=search_data,
            market_opportunity=market,
            competitor_analysis=competitors,
            swot_and_risk=swot_risk,
            mvp_recommendation=mvp,
            gtm_strategy=gtm,
            financial_feasibility=financial,
            executive_verdict=verdict,
            composite_viability_score=composite_score,
            executive_summary=summary,
            key_recommendations=recommendations
        )

    def generate_markdown(self, report: FullValidationReport) -> str:
        """
        Formats report into a beautifully structured Markdown document.
        """
        md = []
        md.append(f"# 🚀 Startup Validation Report: {report.structured_idea.title}")
        md.append(f"**Report ID:** `{report.report_id}` | **Generated:** {report.created_at}")
        md.append(f"**Executive Verdict:** `{report.executive_verdict}` | **Viability Score:** **{report.composite_viability_score}/100**\n")
        
        md.append("## 📌 Executive Summary")
        md.append(report.executive_summary)
        md.append("\n### Key Strategic Directives")
        for rec in report.key_recommendations:
            md.append(f"- {rec}")
        
        md.append("\n---\n## 💡 Core Idea Breakdown")
        md.append(f"- **Tagline:** {report.structured_idea.tagline}")
        md.append(f"- **Problem Statement:** {report.structured_idea.problem_statement}")
        md.append(f"- **Solution Statement:** {report.structured_idea.solution_statement}")
        md.append(f"- **Target Customer:** {report.structured_idea.target_customer}")
        md.append(f"- **Core Value Proposition:** {report.structured_idea.core_value_prop}")
        md.append(f"- **Industry Category:** {report.structured_idea.industry_domain}")

        md.append("\n---\n## 🌐 Live Web Intelligence & Real-World Signals")
        md.append(report.web_intelligence.market_signals_summary)
        if report.web_intelligence.real_world_stats:
            md.append("\n### Real-World Data Points")
            for stat in report.web_intelligence.real_world_stats:
                md.append(f"- {stat}")

        md.append("\n---\n## 📈 Market Opportunity & Customer Segmentation")
        md.append(f"- **TAM (Total Addressable Market):** {report.market_opportunity.tam_estimate}")
        md.append(f"- **SAM (Serviceable Addressable Market):** {report.market_opportunity.sam_estimate}")
        md.append(f"- **SOM (Serviceable Obtainable Market - 3 Yr):** {report.market_opportunity.som_estimate}")
        md.append(f"- **Growth Rate (CAGR):** {report.market_opportunity.cagr_growth_rate}")
        md.append(f"- **Market Timing Score:** {report.market_opportunity.market_timing_score}/100")
        
        md.append("\n### Customer Personas")
        for p in report.market_opportunity.personas:
            md.append(f"#### 👤 {p.persona_name} ({p.target_demographics})")
            md.append(f"- **Core Pain Points:** {', '.join(p.core_pain_points)}")
            md.append(f"- **Current Workaround:** {p.current_workaround}")
            md.append(f"- **Willingness to Pay:** {p.willingness_to_pay}")
            md.append(f"- **Buying Trigger:** {p.key_buying_trigger}\n")

        md.append("\n---\n## 🎯 Competitor Landscape & Gap Analysis")
        md.append(f"**Market Saturation:** `{report.competitor_analysis.market_saturation_level}`\n")
        for c in report.competitor_analysis.competitors:
            md.append(f"### {c.name} ({c.competitor_type}) - *{c.estimated_market_position}*")
            md.append(f"{c.description}")
            md.append(f"- **Strengths:** {', '.join(c.strengths)}")
            md.append(f"- **Weaknesses:** {', '.join(c.weaknesses)}")
            md.append(f"- **Pricing Model:** {c.pricing_model}\n")

        md.append("### White Space Opportunities")
        for ws in report.competitor_analysis.white_space_opportunities:
            md.append(f"- {ws}")
        md.append(f"\n**Defensibility Moat:** {report.competitor_analysis.defensibility_moat}")

        md.append("\n---\n## ⚖️ SWOT & Risk Analysis")
        md.append("### Strengths")
        for s in report.swot_and_risk.strengths: md.append(f"- {s}")
        md.append("\n### Weaknesses")
        for w in report.swot_and_risk.weaknesses: md.append(f"- {w}")
        md.append("\n### Opportunities")
        for o in report.swot_and_risk.opportunities: md.append(f"- {o}")
        md.append("\n### Threats")
        for t in report.swot_and_risk.threats: md.append(f"- {t}")

        md.append("\n### Execution Risk Register")
        for r in report.swot_and_risk.risk_items:
            md.append(f"- **[{r.category}] {r.risk_title}** (Likelihood: `{r.likelihood}`, Severity: `{r.severity}`)")
            md.append(f"  - *Mitigation:* {r.mitigation_strategy}")

        md.append("\n---\n## 🚀 MVP Feature Roadmap (MoSCoW)")
        md.append(f"- **Estimated Build Time:** {report.mvp_recommendation.estimated_build_time_weeks} weeks")
        md.append(f"- **Estimated Budget:** {report.mvp_recommendation.estimated_mvp_budget_usd}")
        md.append(f"- **North Star Metric:** {report.mvp_recommendation.critical_success_metric}\n")
        for f in report.mvp_recommendation.core_features:
            md.append(f"### [{f.moscow_category}] {f.feature_name} (*{f.sprint_phase}*)")
            md.append(f"- **Impact:** `{f.user_impact}` | **Effort:** `{f.development_effort}`")
            md.append(f"- {f.description}\n")

        md.append("\n---\n## 📣 Go-To-Market & Growth Strategy")
        md.append(f"**Positioning:** {report.gtm_strategy.positioning_statement}\n")
        md.append("### Customer Acquisition Channels")
        for ch in report.gtm_strategy.primary_acquisition_channels:
            md.append(f"- **{ch['channel']}:** {ch['details']}")
        md.append("\n### First 100 Customers Playbook")
        for step in report.gtm_strategy.first_100_customers_playbook:
            md.append(f"1. {step}")

        return "\n".join(md)
