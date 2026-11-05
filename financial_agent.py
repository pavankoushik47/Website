"""
Financial Feasibility and Investment ROI Modeling Agent.
Calculates startup financial projections, 5-year P&L, break-even timeline, and investment returns.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from models import (
    StructuredIdea, MarketOpportunity, MVPRecommendation,
    GTMStrategy, FinancialFeasibility, FinancialYearProjection
)
from utils.llm_client import UnifiedLLMClient

class FinancialFeasibilityAgent(BaseAgent):
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        super().__init__(name="FinancialFeasibilityAgent", role="Financial Modeling & Investment ROI Simulation", llm_client=llm_client)

    def run(
        self,
        idea: StructuredIdea,
        market: MarketOpportunity,
        mvp: MVPRecommendation,
        gtm: GTMStrategy
    ) -> FinancialFeasibility:
        self.log(f"Formulating 5-year financial feasibility and P&L projection for: {idea.title}")

        # Extract base pricing signals
        pricing_tiers = gtm.pricing_strategy.get("recommended_tiers", [])
        avg_price = 29.0
        if pricing_tiers:
            for t in pricing_tiers:
                p_str = str(t.get("price", "0")).replace("$", "").split("/")[0].strip()
                try:
                    val = float(p_str)
                    if val > 0:
                        avg_price = val
                        break
                except ValueError:
                    continue

        # Heuristic Baseline Computation
        init_invest = 35000.0
        if "Enterprise" in idea.monetization_model or "Hardware" in idea.industry_domain:
            init_invest = 75000.0
        elif "Freemium" in idea.monetization_model:
            init_invest = 25000.0

        burn_rate = init_invest / 8.0

        # Build 5-year baseline model
        growth_factors = [
            {"year": "Year 1", "cust": 180, "rev_mult": 1.0, "cac_mult": 0.85, "ops_mult": 1.2},
            {"year": "Year 2", "cust": 650, "rev_mult": 1.15, "cac_mult": 0.70, "ops_mult": 1.6},
            {"year": "Year 3", "cust": 2100, "rev_mult": 1.30, "cac_mult": 0.55, "ops_mult": 2.2},
            {"year": "Year 4", "cust": 5400, "rev_mult": 1.45, "cac_mult": 0.45, "ops_mult": 3.0},
            {"year": "Year 5", "cust": 12000, "rev_mult": 1.60, "cac_mult": 0.40, "ops_mult": 4.1},
        ]

        projections: List[FinancialYearProjection] = []
        cumulative = -init_invest

        for gf in growth_factors:
            cust = gf["cust"]
            annual_arpu = avg_price * 12.0 * gf["rev_mult"]
            revenue = round(cust * annual_arpu, 2)
            cogs = round(revenue * 0.18, 2)  # ~82% gross margin for digital / software
            marketing = round(cust * 65.0 * gf["cac_mult"], 2)
            rd_ops = round(burn_rate * 12.0 * gf["ops_mult"], 2)
            total_expenses = cogs + marketing + rd_ops
            net_pl = round(revenue - total_expenses, 2)
            cumulative = round(cumulative + net_pl, 2)

            projections.append(FinancialYearProjection(
                year=gf["year"],
                customers=cust,
                revenue=revenue,
                cogs_and_expenses=cogs,
                marketing_cost=marketing,
                rd_and_operations=rd_ops,
                net_profit_or_loss=net_pl,
                cumulative_cash_flow=cumulative
            ))

        break_even = 14
        if projections[1].net_profit_or_loss > 0:
            break_even = 14
        elif projections[2].net_profit_or_loss > 0:
            break_even = 22
        else:
            break_even = 28

        total_net = sum(p.net_profit_or_loss for p in projections)
        roi_pct = round((total_net / init_invest) * 100.0, 1)

        system_prompt = (
            "You are a seasoned venture capital financial analyst. Analyze the startup financial model "
            "and output a strategic financial feasibility verdict and executive summary."
        )
        user_prompt = (
            f"Startup: {idea.title} ({idea.industry_domain})\n"
            f"Initial Seed Capital: ${init_invest:,.2f}\n"
            f"Break-even: {break_even} months\n"
            f"5-Year Projected ROI: {roi_pct}%\n"
            "Return JSON in format:\n"
            '{\n  "financial_verdict": "Clear 2-sentence financial assessment regarding capital efficiency, margin safety, and unit economics."\n}'
        )

        financial_verdict = (
            f"Capital efficient model with projected break-even at Month {break_even}. "
            f"5-year ROI is projected at {roi_pct}% with healthy gross margins exceeding 80%."
        )

        try:
            data = self.execute_structured_prompt(system_prompt, user_prompt)
            if "financial_verdict" in data:
                financial_verdict = data["financial_verdict"]
        except Exception:
            pass

        return FinancialFeasibility(
            initial_investment=init_invest,
            break_even_month=break_even,
            five_year_roi_percent=roi_pct,
            burn_rate_monthly=round(burn_rate, 2),
            target_gross_margin=82.0,
            yearly_projections=projections,
            financial_verdict=financial_verdict
        )

