"""
Executive PDF Report Generator for AI Startup Idea Validator using ReportLab.
Produces presentation-ready, beautifully styled PDF validation reports.
"""
import io
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from models import FullValidationReport

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically draw 'Page X of Y' and header/footer rules.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Ventura AI — Executive Startup Idea Validation Dossier")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, footer_text)
        self.drawString(54, 35, "CONFIDENTIAL & PROPRIETARY — PREPARED BY VENTURA MULTI-AGENT ENGINE")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

def generate_pdf_report(report: FullValidationReport) -> bytes:
    """
    Compiles FullValidationReport into a professional PDF and returns raw bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palettes
    c_primary = colors.HexColor("#0F172A")    # Deep slate
    c_accent = colors.HexColor("#2563EB")     # Brand blue
    c_success = colors.HexColor("#059669")    # Emerald
    c_warning = colors.HexColor("#D97706")    # Amber
    c_danger = colors.HexColor("#DC2626")     # Rose
    c_muted = colors.HexColor("#64748B")      # Muted grey
    c_card_bg = colors.HexColor("#F8FAFC")    # Light slate

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=4
    )

    tagline_style = ParagraphStyle(
        "DocTagline",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    card_text = ParagraphStyle(
        "CardText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # 1. Header Block
    story.append(Paragraph(f"VENTURA AI: STARTUP VALIDATION DOSSIER", ParagraphStyle("SuperH", fontName="Helvetica-Bold", fontSize=9, textColor=c_accent, leading=12, spaceAfter=2)))
    story.append(Paragraph(report.structured_idea.title, title_style))
    story.append(Paragraph(report.structured_idea.tagline, tagline_style))

    # Meta Table: ID, Date, Domain, Verdict
    verdict_color = c_success if "STRONG GO" in report.executive_verdict else (c_warning if "CAUTION" in report.executive_verdict else c_danger)
    meta_data = [
        [
            Paragraph("<b>Report ID:</b> " + report.report_id, card_text),
            Paragraph("<b>Domain:</b> " + report.structured_idea.industry_domain, card_text),
            Paragraph(f"<b>Viability Score:</b> {report.composite_viability_score} / 100", card_text),
            Paragraph(f"<b>Verdict:</b> {report.executive_verdict}", ParagraphStyle("Verdict", parent=card_text, fontName="Helvetica-Bold", textColor=verdict_color))
        ]
    ]
    meta_table = Table(meta_data, colWidths=[120, 140, 110, 134])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 2. Executive Summary & Key Directives
    story.append(Paragraph("1. Executive Summary & Strategic Verdict", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=6))
    story.append(Paragraph(report.executive_summary.replace("\n\n", "<br/><br/>"), body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Key Strategic Directives:</b>", body_style))
    for rec in report.key_recommendations:
        story.append(Paragraph(f"• {rec}", body_style))
    story.append(Spacer(1, 10))

    # 3. Core Idea & Problem-Solution Matrix
    story.append(Paragraph("2. Venture Foundation & Core Mechanics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=6))
    idea_table_data = [
        [Paragraph("<b>Problem Statement</b>", body_bold), Paragraph(report.structured_idea.problem_statement, body_style)],
        [Paragraph("<b>Proposed Solution</b>", body_bold), Paragraph(report.structured_idea.solution_statement, body_style)],
        [Paragraph("<b>Primary Customer</b>", body_bold), Paragraph(report.structured_idea.target_customer, body_style)],
        [Paragraph("<b>Value Proposition</b>", body_bold), Paragraph(report.structured_idea.core_value_prop, body_style)],
        [Paragraph("<b>Monetization Model</b>", body_bold), Paragraph(report.structured_idea.monetization_model, body_style)],
    ]
    idea_table = Table(idea_table_data, colWidths=[130, 374])
    idea_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(idea_table)
    story.append(Spacer(1, 10))

    # 4. Market Sizing & Customer Personas
    story.append(Paragraph("3. Market Opportunity & Sizing (TAM/SAM/SOM)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=6))
    market_data = [
        [
            Paragraph("<b>TAM (Total Market)</b>", body_bold),
            Paragraph("<b>SAM (Serviceable)</b>", body_bold),
            Paragraph("<b>SOM (Year 3)</b>", body_bold),
            Paragraph("<b>Growth (CAGR)</b>", body_bold),
            Paragraph("<b>Timing Score</b>", body_bold),
        ],
        [
            Paragraph(report.market_opportunity.tam_estimate, card_text),
            Paragraph(report.market_opportunity.sam_estimate, card_text),
            Paragraph(report.market_opportunity.som_estimate, card_text),
            Paragraph(report.market_opportunity.cagr_growth_rate, card_text),
            Paragraph(f"{report.market_opportunity.market_timing_score} / 100", card_text),
        ]
    ]
    market_table = Table(market_data, colWidths=[110, 100, 100, 100, 94])
    market_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(market_table)
    story.append(Spacer(1, 6))

    if report.market_opportunity.personas:
        story.append(Paragraph("<b>Primary Customer Personas:</b>", h2_style))
        for p in report.market_opportunity.personas[:2]:
            p_text = f"<b>{p.persona_name}</b> ({p.target_demographics}) — <i>Pain Points:</i> {', '.join(p.core_pain_points[:2])} | <i>Willingness to Pay:</i> {p.willingness_to_pay}"
            story.append(Paragraph(f"• {p_text}", body_style))
    story.append(Spacer(1, 10))

    # Page Break for clean multi-page dossier
    story.append(PageBreak())

    # 5. Competitor Discovery & White Space Opportunities
    story.append(Paragraph("4. Competitor Discovery & White Space Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=6))
    comp_header = [Paragraph("<b>Competitor</b>", body_bold), Paragraph("<b>Type / Position</b>", body_bold), Paragraph("<b>Strengths</b>", body_bold), Paragraph("<b>Weaknesses</b>", body_bold)]
    comp_rows = [comp_header]
    for c in report.competitor_analysis.competitors[:3]:
        comp_rows.append([
            Paragraph(f"<b>{c.name}</b><br/><i>{c.pricing_model}</i>", card_text),
            Paragraph(f"{c.competitor_type}<br/>{c.estimated_market_position}", card_text),
            Paragraph(", ".join(c.strengths[:2]), card_text),
            Paragraph(", ".join(c.weaknesses[:2]), card_text),
        ])
    comp_table = Table(comp_rows, colWidths=[120, 110, 137, 137])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Unfilled White Space Opportunities:</b>", h2_style))
    for ws in report.competitor_analysis.white_space_opportunities[:3]:
        story.append(Paragraph(f"• {ws}", body_style))
    story.append(Spacer(1, 10))

    # 6. SWOT & Risk Register
    story.append(Paragraph("5. SWOT Matrix & Execution Risk Register", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=6))
    swot_data = [
        [
            Paragraph(f"<b>STRENGTHS</b><br/>" + "<br/>• ".join([""] + report.swot_and_risk.strengths[:3]), card_text),
            Paragraph(f"<b>WEAKNESSES</b><br/>" + "<br/>• ".join([""] + report.swot_and_risk.weaknesses[:3]), card_text),
        ],
        [
            Paragraph(f"<b>OPPORTUNITIES</b><br/>" + "<br/>• ".join([""] + report.swot_and_risk.opportunities[:3]), card_text),
            Paragraph(f"<b>THREATS</b><br/>" + "<br/>• ".join([""] + report.swot_and_risk.threats[:3]), card_text),
        ]
    ]
    swot_table = Table(swot_data, colWidths=[252, 252])
    swot_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#ECFDF5")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#FEF2F2")),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor("#FFFBEB")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(swot_table)
    story.append(Spacer(1, 8))

    # Risk Table
    risk_header = [Paragraph("<b>Risk Category & Title</b>", body_bold), Paragraph("<b>Likelihood / Severity</b>", body_bold), Paragraph("<b>Mitigation Strategy</b>", body_bold)]
    risk_rows = [risk_header]
    for r in report.swot_and_risk.risk_items[:3]:
        risk_rows.append([
            Paragraph(f"<b>[{r.category}]</b> {r.risk_title}", card_text),
            Paragraph(f"{r.likelihood} / {r.severity}", card_text),
            Paragraph(r.mitigation_strategy, card_text)
        ])
    risk_table = Table(risk_rows, colWidths=[150, 100, 254])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 10))

    # 7. MVP Roadmap & GTM Strategy
    story.append(Paragraph("6. MVP Feature Prioritization (MoSCoW) & GTM Plan", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=6))
    story.append(Paragraph(f"<b>Build Timeline:</b> {report.mvp_recommendation.estimated_build_time_weeks} Weeks | <b>Estimated Budget:</b> {report.mvp_recommendation.estimated_mvp_budget_usd} | <b>North Star Metric:</b> {report.mvp_recommendation.critical_success_metric}", body_style))
    story.append(Spacer(1, 4))
    
    # Must-Haves
    must_haves = [f.feature_name for f in report.mvp_recommendation.core_features if f.moscow_category == "Must-Have"]
    story.append(Paragraph(f"• <b>Must-Have Core (Phase 1):</b> {', '.join(must_haves)}", body_style))
    should_haves = [f.feature_name for f in report.mvp_recommendation.core_features if f.moscow_category == "Should-Have"]
    if should_haves:
        story.append(Paragraph(f"• <b>Should-Have (Phase 2):</b> {', '.join(should_haves)}", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>First 100 Customers Playbook:</b>", h2_style))
    for step in report.gtm_strategy.first_100_customers_playbook[:3]:
        story.append(Paragraph(f"• {step}", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
