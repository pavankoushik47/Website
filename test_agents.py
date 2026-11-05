"""
End-to-end unit and integration tests for all 8 agents and the orchestrator.
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from models import IdeaSubmission
from orchestrator import ValidationOrchestrator
from utils.pdf_generator import generate_pdf_report
from agents.advisor_agent import ConversationalAdvisorAgent
import unittest

def test_full_pipeline():
    print("\n=======================================================")
    print("RUNNING END-TO-END STARTUP VALIDATOR PIPELINE TEST")
    print("=======================================================\n")

    # Sample idea
    submission = IdeaSubmission(
        raw_idea="An AI-powered contract review tool for freelance designers and creative contractors that highlights unfair payment terms, indemnity traps, and unlimited revision clauses, drafting instant counter-amendments.",
        domain_hint="LegalTech & Creator Economy",
        target_geography="Global",
        monetization_preference="Freemium + $19/mo Pro Subscription"
    )

    orchestrator = ValidationOrchestrator(llm_provider="heuristic")

    steps_started = []
    steps_finished = []

    def on_step_start(idx, name, role):
        print(f"  [START] Step {idx+1}/8: {name} ({role})")
        steps_started.append(name)

    def on_step_complete(idx, name, result):
        print(f"  [DONE]  Step {idx+1}/8: {name} complete.")
        steps_finished.append(name)

    report = orchestrator.run_pipeline(
        submission,
        on_step_start=on_step_start,
        on_step_complete=on_step_complete
    )

    # Assertions
    assert len(steps_started) == 9, f"Expected 9 started steps, got {len(steps_started)}"
    assert len(steps_finished) == 9, f"Expected 9 completed steps, got {len(steps_finished)}"

    # Check Structured Idea
    assert report.structured_idea.title, "Title should not be empty"
    print(f"\n[Validation] Title: {report.structured_idea.title}")
    print(f"[Validation] Domain: {report.structured_idea.industry_domain}")

    # Check Web Intelligence
    assert len(report.web_intelligence.results) > 0, "Should have retrieved search results"
    print(f"[Validation] Search records count: {len(report.web_intelligence.results)}")

    # Check Financial Feasibility
    assert report.financial_feasibility is not None, "Financial feasibility should be generated"
    assert len(report.financial_feasibility.yearly_projections) == 5, "Should have 5-year projections"
    print(f"[Validation] Break-even: Month {report.financial_feasibility.break_even_month} | 5-Yr ROI: {report.financial_feasibility.five_year_roi_percent}%")

    # Check Market Opportunity
    assert report.market_opportunity.tam_estimate, "TAM should be present"
    assert len(report.market_opportunity.personas) >= 1, "Should have customer personas"
    print(f"[Validation] TAM: {report.market_opportunity.tam_estimate} | SAM: {report.market_opportunity.sam_estimate}")

    # Check Competitors
    assert len(report.competitor_analysis.competitors) >= 2, "Should have competitors"
    print(f"[Validation] Competitors: {[c.name for c in report.competitor_analysis.competitors]}")

    # Check SWOT & Risk
    assert len(report.swot_and_risk.strengths) > 0, "SWOT strengths missing"
    assert len(report.swot_and_risk.risk_items) > 0, "Risk register missing"
    print(f"[Validation] Feasibility Score: {report.swot_and_risk.feasibility_score} | Viability: {report.swot_and_risk.market_viability_score}")

    # Check MVP
    assert len(report.mvp_recommendation.core_features) > 0, "MVP features missing"
    print(f"[Validation] MVP Build Weeks: {report.mvp_recommendation.estimated_build_time_weeks}")

    # Check GTM
    assert len(report.gtm_strategy.primary_acquisition_channels) > 0, "GTM channels missing"
    assert len(report.gtm_strategy.first_100_customers_playbook) > 0, "First 100 playbook missing"

    # Check Verdict and Score
    assert 0 <= report.composite_viability_score <= 100, "Viability score must be 0-100"
    print(f"[Validation] Composite Score: {report.composite_viability_score}/100")
    print(f"[Validation] Executive Verdict: {report.executive_verdict}")

    # Test PDF Generation
    pdf_bytes = generate_pdf_report(report)
    assert len(pdf_bytes) > 2000, f"PDF file size too small: {len(pdf_bytes)} bytes"
    print(f"[Validation] Generated PDF Report: {len(pdf_bytes)} bytes successfully.")

    # Test Markdown Generation
    md_text = orchestrator.report_agent.generate_markdown(report)
    assert "# 🚀 Startup Validation Report" in md_text
    print(f"[Validation] Generated Markdown Report: {len(md_text)} chars successfully.")

    # Test Conversational Advisor
    advisor = ConversationalAdvisorAgent(llm_client=orchestrator.llm_client)
    answer = advisor.answer_query("How should I price the MVP during the initial beta?", report)
    assert len(answer) > 30, "Advisor answer should not be empty"
    print(f"[Validation] Advisor Answer Sample: {answer[:120]}...")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<\n")

class TestPipeline(unittest.TestCase):
    def test_pipeline_execution(self):
        test_full_pipeline()

if __name__ == "__main__":
    test_full_pipeline()
