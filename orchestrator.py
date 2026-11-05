"""
Multi-Agent Sequential Pipeline Orchestrator.
Manages context passing between agents, step callbacks, timing, and error handling.
"""
import time
from typing import Callable, Optional, Dict, Any, List
from models import (
    IdeaSubmission, StructuredIdea, WebSearchIntelligence,
    MarketOpportunity, CompetitorAnalysis, SWOTAndRiskReport,
    MVPRecommendation, GTMStrategy, FullValidationReport
)
from agents import (
    IdeaExtractionAgent, WebSearchAgent, MarketAnalysisAgent,
    CompetitorAnalysisAgent, SWOTAndRiskAgent, MVPRecommendationAgent,
    GTMStrategyAgent, FinancialFeasibilityAgent, ReportGenerationAgent, ConversationalAdvisorAgent
)
from utils.llm_client import UnifiedLLMClient

class ValidationOrchestrator:
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        tavily_api_key: Optional[str] = None
    ):
        self.llm_client = UnifiedLLMClient(provider=llm_provider, model=llm_model, api_key=llm_api_key)
        self.tavily_api_key = tavily_api_key

        # Initialize agents
        self.extraction_agent = IdeaExtractionAgent(llm_client=self.llm_client)
        self.search_agent = WebSearchAgent(tavily_api_key=self.tavily_api_key, llm_client=self.llm_client)
        self.market_agent = MarketAnalysisAgent(llm_client=self.llm_client)
        self.competitor_agent = CompetitorAnalysisAgent(llm_client=self.llm_client)
        self.swot_agent = SWOTAndRiskAgent(llm_client=self.llm_client)
        self.mvp_agent = MVPRecommendationAgent(llm_client=self.llm_client)
        self.gtm_agent = GTMStrategyAgent(llm_client=self.llm_client)
        self.financial_agent = FinancialFeasibilityAgent(llm_client=self.llm_client)
        self.report_agent = ReportGenerationAgent(llm_client=self.llm_client)
        self.advisor_agent = ConversationalAdvisorAgent(llm_client=self.llm_client)

    def run_pipeline(
        self,
        submission: IdeaSubmission,
        on_step_start: Optional[Callable[[int, str, str], None]] = None,
        on_step_complete: Optional[Callable[[int, str, Any], None]] = None
    ) -> FullValidationReport:
        """
        Executes the full sequential multi-agent validation pipeline.
        Calls on_step_start(step_index, step_name, agent_role)
        and on_step_complete(step_index, step_name, step_result).
        """
        start_time = time.time()

        # Step 1: Idea Extraction
        if on_step_start: on_step_start(0, "Idea Extraction", "IdeaExtractionAgent")
        structured_idea = self.extraction_agent.run(submission)
        if on_step_complete: on_step_complete(0, "Idea Extraction", structured_idea)

        # Step 2: Web Search and Intelligence
        if on_step_start: on_step_start(1, "Live Web Search", "WebSearchAgent")
        search_data = self.search_agent.run(structured_idea)
        if on_step_complete: on_step_complete(1, "Live Web Search", search_data)

        # Step 3: Market Opportunity & Customer Segmentation
        if on_step_start: on_step_start(2, "Market Opportunity", "MarketAnalysisAgent")
        market_opp = self.market_agent.run(structured_idea, search_data)
        if on_step_complete: on_step_complete(2, "Market Opportunity", market_opp)

        # Step 4: Competitor Discovery & Gap Analysis
        if on_step_start: on_step_start(3, "Competitor Discovery", "CompetitorAnalysisAgent")
        competitor_analysis = self.competitor_agent.run(structured_idea, search_data, market_opp)
        if on_step_complete: on_step_complete(3, "Competitor Discovery", competitor_analysis)

        # Step 5: SWOT & Risk Analysis
        if on_step_start: on_step_start(4, "SWOT & Risk Assessment", "SWOTAndRiskAgent")
        swot_risk = self.swot_agent.run(structured_idea, market_opp, competitor_analysis)
        if on_step_complete: on_step_complete(4, "SWOT & Risk Assessment", swot_risk)

        # Step 6: MVP Feature Roadmap (MoSCoW)
        if on_step_start: on_step_start(5, "MVP Feature Set", "MVPRecommendationAgent")
        mvp_rec = self.mvp_agent.run(structured_idea, competitor_analysis, swot_risk)
        if on_step_complete: on_step_complete(5, "MVP Feature Set", mvp_rec)

        # Step 7: Go-To-Market Strategy
        if on_step_start: on_step_start(6, "GTM & Growth Playbook", "GTMStrategyAgent")
        gtm_strat = self.gtm_agent.run(structured_idea, market_opp, competitor_analysis, mvp_rec)
        if on_step_complete: on_step_complete(6, "GTM & Growth Playbook", gtm_strat)

        # Step 8: Financial Feasibility & P&L Modeling
        if on_step_start: on_step_start(7, "Financial Feasibility & P&L", "FinancialFeasibilityAgent")
        financial_model = self.financial_agent.run(structured_idea, market_opp, mvp_rec, gtm_strat)
        if on_step_complete: on_step_complete(7, "Financial Feasibility & P&L", financial_model)

        # Step 9: Validation Report Generation
        if on_step_start: on_step_start(8, "Executive Report Synthesis", "ReportGenerationAgent")
        final_report = self.report_agent.run(
            submission=submission,
            idea=structured_idea,
            search_data=search_data,
            market=market_opp,
            competitors=competitor_analysis,
            swot_risk=swot_risk,
            mvp=mvp_rec,
            gtm=gtm_strat,
            financial=financial_model
        )
        if on_step_complete: on_step_complete(8, "Executive Report Synthesis", final_report)

        elapsed = time.time() - start_time
        print(f"[Orchestrator] Multi-agent pipeline completed successfully in {elapsed:.2f} seconds.")
        return final_report
