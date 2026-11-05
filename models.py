"""
Pydantic data models for the AI Startup Idea Validator multi-agent pipeline.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class IdeaSubmission(BaseModel):
    raw_idea: str = Field(..., description="The raw 2-3 line startup idea description provided by the founder")
    domain_hint: Optional[str] = Field(None, description="Optional industry sector or domain category")
    target_geography: Optional[str] = Field("Global", description="Target geography e.g. North America, Global, India, Europe")
    monetization_preference: Optional[str] = Field(None, description="E.g. SaaS, Marketplace, B2B, B2C, Freemium")

class CustomerPersona(BaseModel):
    persona_name: str
    target_demographics: str
    core_pain_points: List[str]
    current_workaround: str
    willingness_to_pay: str
    key_buying_trigger: str

class StructuredIdea(BaseModel):
    title: str = Field(..., description="A catchy, crisp working startup title")
    tagline: str = Field(..., description="One-line elevator tagline")
    problem_statement: str = Field(..., description="Clearly articulated customer pain point")
    solution_statement: str = Field(..., description="How the startup solves the problem")
    target_customer: str = Field(..., description="Primary ideal customer segment")
    core_value_prop: str = Field(..., description="Unique value proposition")
    industry_domain: str = Field(..., description="Primary industry or market category")
    monetization_model: str = Field(..., description="Primary revenue model")
    key_keywords: List[str] = Field(default_factory=list, description="Keywords for search retrieval")

class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    query_used: str
    source_domain: str = ""

class WebSearchIntelligence(BaseModel):
    queries_executed: List[str]
    results: List[SearchResultItem]
    market_signals_summary: str
    real_world_stats: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MarketOpportunity(BaseModel):
    tam_estimate: str = Field(..., description="Total Addressable Market size estimate (e.g. $45 Billion)")
    sam_estimate: str = Field(..., description="Serviceable Available Market estimate (e.g. $8.2 Billion)")
    som_estimate: str = Field(..., description="Serviceable Obtainable Market estimate in Year 1-3 (e.g. $120 Million)")
    cagr_growth_rate: str = Field(..., description="Compound annual growth rate (e.g. 18.4% through 2030)")
    market_drivers: List[str] = Field(..., description="Key tailwinds and macroeconomic trends fueling growth")
    market_barriers: List[str] = Field(..., description="Adoption barriers, switching costs, or headwinds")
    personas: List[CustomerPersona] = Field(default_factory=list, description="Detailed customer personas")
    market_timing_score: int = Field(80, ge=0, le=100, description="Score 0-100 indicating timing favorability")

class Competitor(BaseModel):
    name: str
    competitor_type: str = Field(..., description="Direct, Indirect, or Substitute")
    description: str
    strengths: List[str]
    weaknesses: List[str]
    pricing_model: str
    estimated_market_position: str

class CompetitorAnalysis(BaseModel):
    competitors: List[Competitor]
    market_saturation_level: str = Field("Moderate", description="Low, Moderate, High, or Saturated")
    feature_matrix: Dict[str, Dict[str, bool]] = Field(default_factory=dict, description="Feature comparison matrix")
    white_space_opportunities: List[str] = Field(..., description="Gaps in existing competitors that the startup can exploit")
    defensibility_moat: str = Field(..., description="Long term sustainable competitive advantage / moat")

class RiskItem(BaseModel):
    category: str = Field(..., description="Execution, Regulatory/Legal, Technical/AI, Financial/Runway, Market Adoption")
    risk_title: str
    description: str
    likelihood: str = Field("Medium", description="Low, Medium, or High")
    severity: str = Field("Medium", description="Low, Medium, or High")
    mitigation_strategy: str

class SWOTAndRiskReport(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    risk_items: List[RiskItem]
    feasibility_score: int = Field(75, ge=0, le=100)
    market_viability_score: int = Field(75, ge=0, le=100)
    execution_complexity: str = Field("Moderate", description="Low, Moderate, High, Extreme")
    overall_risk_rating: str = Field("Moderate", description="Low, Moderate, High, Critical")

class MVPFeature(BaseModel):
    feature_name: str
    moscow_category: str = Field(..., description="Must-Have, Should-Have, Could-Have, Won't-Have (v1)")
    description: str
    user_impact: str = Field("High", description="Low, Medium, High")
    development_effort: str = Field("Medium", description="Low, Medium, High")
    sprint_phase: str = Field("Phase 1: Core Engine", description="Phase 1, Phase 2, or Phase 3")

class MVPRecommendation(BaseModel):
    core_features: List[MVPFeature]
    recommended_tech_stack: Dict[str, str] = Field(
        default_factory=lambda: {
            "Frontend": "Next.js / React with TailwindCSS",
            "Backend": "Python FastAPI or Node.js",
            "Database": "PostgreSQL + Supabase",
            "AI / LLM": "LangChain / OpenAI / Groq API",
            "Hosting": "Vercel + Railway / AWS"
        }
    )
    estimated_build_time_weeks: int = Field(6, description="Estimated weeks to launch MVP")
    estimated_mvp_budget_usd: str = Field("$2,500 - $8,000", description="Estimated initial launch budget")
    critical_success_metric: str = Field(..., description="Primary KPI to validate MVP success")

class GTMStrategy(BaseModel):
    ideal_customer_profile: str
    positioning_statement: str
    primary_acquisition_channels: List[Dict[str, str]] = Field(
        ...,
        description="List of channels with strategy, e.g. [{'channel': 'LinkedIn Cold Outreach', 'details': '...'}]"
    )
    first_100_customers_playbook: List[str] = Field(..., description="Step-by-step tactical guide to 100 users")
    pricing_strategy: Dict[str, Any] = Field(
        default_factory=lambda: {
            "model": "Freemium / Tiered SaaS",
            "recommended_tiers": [
                {"tier": "Starter", "price": "$0 / month", "target": "Individual users / Trial"},
                {"tier": "Pro", "price": "$29 / month", "target": "Power users / Freelancers"},
                {"tier": "Team", "price": "$99 / month", "target": "Growing teams"}
            ]
        }
    )
    unit_economics_estimate: Dict[str, str] = Field(
        default_factory=lambda: {
            "Target CAC": "$40 - $70",
            "Estimated LTV": "$350 - $600",
            "LTV / CAC Ratio": "5.5x (Healthy)",
            "Target Payback Period": "< 3 Months"
        }
    )

class FinancialYearProjection(BaseModel):
    year: str
    customers: int
    revenue: float
    cogs_and_expenses: float
    marketing_cost: float
    rd_and_operations: float
    net_profit_or_loss: float
    cumulative_cash_flow: float

class FinancialFeasibility(BaseModel):
    initial_investment: float = Field(35000.0, description="Recommended initial seed / bootstrapping capital in USD")
    break_even_month: int = Field(14, description="Projected break-even milestone in months")
    five_year_roi_percent: float = Field(320.0, description="Projected 5-year ROI percentage")
    burn_rate_monthly: float = Field(4500.0, description="Estimated monthly burn rate during pre-revenue")
    target_gross_margin: float = Field(82.0, description="Target gross margin percentage")
    yearly_projections: List[FinancialYearProjection] = Field(default_factory=list)
    financial_verdict: str = Field("Viable with Lean Operations", description="Summary financial feasibility verdict")

class FullValidationReport(BaseModel):
    report_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    submission: IdeaSubmission
    structured_idea: StructuredIdea
    web_intelligence: WebSearchIntelligence
    market_opportunity: MarketOpportunity
    competitor_analysis: CompetitorAnalysis
    swot_and_risk: SWOTAndRiskReport
    mvp_recommendation: MVPRecommendation
    gtm_strategy: GTMStrategy
    financial_feasibility: Optional[FinancialFeasibility] = None
    executive_verdict: str = Field("GO WITH CAUTION", description="STRONG GO, GO WITH CAUTION, CONDITIONAL PIVOT, or NO-GO")
    composite_viability_score: int = Field(82, ge=0, le=100)
    executive_summary: str
    key_recommendations: List[str]
