"""
Heuristic fallback reasoning engine for startup analysis when offline or when API keys are not supplied.
Generates comprehensive, domain-aware, structured responses.
"""
import re
import json

def detect_domain(text: str) -> str:
    # 1. If explicit domain is provided in prompts (e.g. 'Domain: ...' or 'Industry Domain: ...'), extract directly
    m = re.search(r"(?:industry\s+domain|domain\s+hint|domain):\s*([^\n\r,]+)", text, re.IGNORECASE)
    if m:
        extracted = m.group(1).strip()
        if extracted and extracted.lower() not in ["auto-detect", "unknown", "none", "n/a"]:
            return extracted

    text_lower = text.lower()

    # 2. Use word boundary checks to prevent false substring collisions
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["health", "medtech", "medicine", "medical", "doctor", "clinic", "patient", "wellness", "pharma"]):
        return "HealthTech & MedTech"
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["carbon", "climate", "solar", "cleantech", "recycle", "esg", "emissions"]):
        return "ClimateTech & Sustainability"
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["fintech", "payment", "banking", "credit", "invoice", "crypto", "defi", "investing", "loan"]):
        return "FinTech & Financial Services"
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["edtech", "student", "teacher", "tutoring", "curriculum", "pedagogy"]):
        return "EdTech & Learning Platforms"
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["freelance", "contract", "legal", "legaltech", "lawyer", "attorney", "workflow", "crm", "b2b"]):
        return "LegalTech & Creator Economy" if any(w in text_lower for w in ["legal", "contract", "lawyer", "attorney"]) else "B2B SaaS & Developer Tools"
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["food", "grocery", "restaurant", "dining", "meal", "kitchen", "culinary"]):
        return "FoodTech & Q-Commerce"
    if any(re.search(rf"\b{re.escape(k)}", text_lower) for k in ["cybersecurity", "infosec", "fraud", "penetration", "soc2", "gdpr"]):
        return "Cybersecurity & Compliance"
    return "AI-Powered Vertical SaaS"

def generate_heuristic_response(system_prompt: str, user_prompt: str) -> str:
    prompt_lower = (system_prompt + " " + user_prompt).lower()
    domain = detect_domain(user_prompt)

    # 0. Conversational Advisor Request (Check first before generic keyword matches)
    if "advisor" in prompt_lower or "founder" in prompt_lower or "question:" in prompt_lower or "recent conversation" in prompt_lower:
        return (
            f"### 🎯 Strategic Advisor Recommendation\n\n"
            f"Based on our multi-agent validation for your **{domain}** venture:\n\n"
            f"1. **Core Priority**: Focus strictly on the Phase 1 Must-Have MVP features identified in your roadmap. Resist feature creep.\n"
            f"2. **Competitive Moat**: Incumbents suffer from high prices and sluggish release cycles. Your strongest advantage is workflow speed, intuitive modern UX, and immediate time-to-value.\n"
            f"3. **Zero-Dollar Early Traction**: Execute founder-led outreach on LinkedIn and indie founder communities. Offer 15 free workflow audits in exchange for video testimonials and direct product feedback.\n"
            f"4. **Pricing Tip**: Start with a low-friction self-serve starter tier to capture market share, then introduce usage-based enterprise add-ons as accounts mature.\n\n"
            f"What specific area should we optimize next: landing page conversion copy, outbound email sequences, or pitch deck traction metrics?"
        )

    # 1. Extraction Agent Request
    if "extract" in prompt_lower or "structured idea" in prompt_lower:
        title = "SmartVentures AI"
        match = re.search(r"startup idea:\s*([^\n\.]+)", user_prompt, re.IGNORECASE)
        if match:
            raw_title = match.group(1).strip()
            words = raw_title.split()
            title = f"{words[0].capitalize()}{words[1].capitalize() if len(words) > 1 else 'Flow'}"
        
        return json.dumps({
            "title": title,
            "tagline": f"Next-generation intelligence platform for modern {domain.lower()}.",
            "problem_statement": "Founders and professionals face fragmented manual workflows, high operational costs, and slow turnaround times when relying on legacy tools.",
            "solution_statement": "An automated, AI-augmented workflow engine that unifies data retrieval, real-time decision intelligence, and streamlined execution into one intuitive workspace.",
            "target_customer": f"Mid-market enterprises, independent specialists, and growing teams operating in {domain}.",
            "core_value_prop": "10x faster execution with verifiable accuracy, automated compliance checks, and measurable cost reduction.",
            "industry_domain": domain,
            "monetization_model": "Tiered B2B SaaS Subscription (Per-seat & Usage-based)",
            "key_keywords": [domain.lower(), "automation", "ai workflows", "analytics", "market trends"]
        })

    # 2. Market Analysis Agent Request
    elif "market opportunity" in prompt_lower or "tam" in prompt_lower or "cagr" in prompt_lower:
        tam = "$38.5 Billion"
        sam = "$7.2 Billion"
        som = "$180 Million"
        cagr = "21.4% CAGR (2024-2031)"
        if "health" in domain.lower():
            tam = "$65.2 Billion"
            sam = "$12.8 Billion"
            som = "$240 Million"
            cagr = "24.8% CAGR"
        elif "climate" in domain.lower():
            tam = "$42.0 Billion"
            sam = "$9.5 Billion"
            som = "$150 Million"
            cagr = "26.2% CAGR"

        return json.dumps({
            "tam_estimate": tam,
            "sam_estimate": sam,
            "som_estimate": som,
            "cagr_growth_rate": cagr,
            "market_drivers": [
                "Rapid enterprise adoption of autonomous agentic workflows and specialized AI tooling",
                "Increasing regulatory transparency and compliance mandates forcing workflow automation",
                "Pressure on operating margins pushing companies to eliminate manual operational overhead"
            ],
            "market_barriers": [
                "Customer reluctance to replace ingrained legacy ERP or spreadsheet habits",
                "Data privacy compliance (GDPR, SOC2, HIPAA) required before enterprise procurement",
                "Initial customer acquisition friction in trust-sensitive business verticals"
            ],
            "personas": [
                {
                    "persona_name": "Operational Decision Maker (VP / Director)",
                    "target_demographics": "Ages 32-52, Mid-to-Large organizations, oversees 15+ member operations",
                    "core_pain_points": [
                        "Drowning in manual verification and repetitive oversight",
                        "Lack of unified audit trails and real-time dashboard visibility",
                        "High employee burnout and costly human errors"
                    ],
                    "current_workaround": "Spreadsheets, Jira/Asana workarounds, and disparate point solutions",
                    "willingness_to_pay": "High ($150 - $600 / user / month budget allocation)",
                    "key_buying_trigger": "Measurable 40%+ reduction in turnaround latency within 14-day pilot"
                },
                {
                    "persona_name": "Frontline Specialist / Freelancer",
                    "target_demographics": "Ages 24-40, Tech-savvy independent practitioners or boutique teams",
                    "core_pain_points": [
                        "Lacks enterprise budget for heavyweight legacy suites",
                        "Needs instant, clean client-facing reports and validations"
                    ],
                    "current_workaround": "Manual copy-pasting across free open-source tools",
                    "willingness_to_pay": "Moderate ($29 - $79 / month self-serve)",
                    "key_buying_trigger": "Simple onboarding with zero engineering setup required"
                }
            ],
            "market_timing_score": 86
        })

    # 3. Competitor Discovery Agent Request
    elif "competitor" in prompt_lower or "gap analysis" in prompt_lower:
        return json.dumps({
            "competitors": [
                {
                    "name": "LegacyCorp Enterprise",
                    "competitor_type": "Direct",
                    "description": "Incumbent industry software with extensive feature set but antiquated UX and slow release cycles.",
                    "strengths": ["Strong enterprise brand recognition", "Existing vendor contracts", "Deep compliance certifications"],
                    "weaknesses": ["Expensive annual commitments ($15k+)", "Clunky UI requiring weeks of training", "Lacks modern autonomous AI agents"],
                    "pricing_model": "Annual enterprise license with mandatory onboarding fees",
                    "estimated_market_position": "Market Leader (Incumbent)"
                },
                {
                    "name": "PointSolution Pro",
                    "competitor_type": "Indirect",
                    "description": "Niche cloud tool focusing on a single step of the broader workflow.",
                    "strengths": ["Fast setup", "Affordable starter pricing", "Good basic reporting"],
                    "weaknesses": ["Siloed data", "No end-to-end multi-agent orchestration", "Does not scale to complex workflows"],
                    "pricing_model": "Monthly SaaS ($49/month)",
                    "estimated_market_position": "Fast-growing challenger"
                },
                {
                    "name": "Custom In-House Spreadsheets & Manual Consultants",
                    "competitor_type": "Substitute",
                    "description": "Internal teams using Google Sheets, Notion, and outsourced consulting agencies.",
                    "strengths": ["Zero new software vendor approval required", "Fully customized to legacy habits"],
                    "weaknesses": ["Completely non-scalable", "High error rate", "Expensive man-hours"],
                    "pricing_model": "High internal personnel salary cost",
                    "estimated_market_position": "Default status quo"
                }
            ],
            "market_saturation_level": "Moderate",
            "feature_matrix": {
                "AI Agentic Automation": {"LegacyCorp Enterprise": False, "PointSolution Pro": False, "This Startup": True},
                "Real-Time Data Verification": {"LegacyCorp Enterprise": True, "PointSolution Pro": False, "This Startup": True},
                "Self-Serve Onboarding < 5 min": {"LegacyCorp Enterprise": False, "PointSolution Pro": True, "This Startup": True},
                "Collaborative Multi-Role Workspace": {"LegacyCorp Enterprise": True, "PointSolution Pro": False, "This Startup": True},
                "Transparent Usage-Based Pricing": {"LegacyCorp Enterprise": False, "PointSolution Pro": True, "This Startup": True}
            },
            "white_space_opportunities": [
                "Autonomous verification: Existing players require human input at every juncture, while this startup provides autonomous agentic loops.",
                "Modern intuitive UX with immediate time-to-value: Bypasses the 3-month onboarding cycle typical of enterprise incumbents.",
                "Accessible entry pricing for growing SMBs and freelancers who are currently priced out by legacy solutions."
            ],
            "defensibility_moat": "Proprietary domain-tuned reasoning prompts, compounding proprietary benchmark data, and sticky integration into customer operational workflows."
        })

    # 4. SWOT and Risk Agent Request
    elif "swot" in prompt_lower or "risk" in prompt_lower:
        return json.dumps({
            "strengths": [
                "Hyper-targeted focus solving a high-friction, acute pain point with modern AI",
                "Lightweight modern architecture enabling rapid iterative deployment cycles",
                "Significantly lower cost structure compared to legacy incumbents",
                "Built-in multi-agent workflows that deliver autonomous end-to-end results"
            ],
            "weaknesses": [
                "Early-stage brand with no established case studies or enterprise logos",
                "Initial dependency on third-party foundation models and API rate limits",
                "Limited marketing runway requiring lean, high-ROI customer acquisition"
            ],
            "opportunities": [
                "Unserved mid-market segment abandoned by high-ticket legacy software vendors",
                "Global expansion enabled by cloud-native architecture and localized compliance modules",
                "API platform potential: licensing workflow components to third-party developer ecosystems"
            ],
            "threats": [
                "Rapid feature expansion by well-funded incumbents into AI workflow automation",
                "Risk of foundation model price fluctuations or API deprecations",
                "Customer inertia and resistance to changing entrenched legacy habits"
            ],
            "risk_items": [
                {
                    "category": "Market Adoption",
                    "risk_title": "Reluctance to switch from established manual habits",
                    "description": "Prospective users might be comfortable with spreadsheets despite known inefficiencies.",
                    "likelihood": "Medium",
                    "severity": "High",
                    "mitigation_strategy": "Offer a frictionless interactive free trial or browser extension that demonstrates tangible value in under 2 minutes."
                },
                {
                    "category": "Technical/AI",
                    "risk_title": "Model hallucinations or edge-case reasoning errors",
                    "description": "Domain-critical tasks require high precision; inaccuracies could erode user trust.",
                    "likelihood": "Medium",
                    "severity": "High",
                    "mitigation_strategy": "Implement rigorous confidence scoring, validation guardrails, and human-in-the-loop review overrides."
                },
                {
                    "category": "Financial/Runway",
                    "risk_title": "High Customer Acquisition Cost (CAC) prior to product-market fit",
                    "description": "Paid advertising can rapidly deplete early capital if organic referral loops are not established.",
                    "likelihood": "Medium",
                    "severity": "Medium",
                    "mitigation_strategy": "Focus strictly on founder-led sales, organic developer/specialist communities, and product-led growth (PLG)."
                },
                {
                    "category": "Regulatory/Legal",
                    "risk_title": "Data privacy and client confidentiality mandates",
                    "description": "Enterprise clients require strict non-disclosure, zero data-retention for training, and SOC2 compliance.",
                    "likelihood": "Low",
                    "severity": "High",
                    "mitigation_strategy": "Guarantee zero-data retention agreements with model providers and design privacy-first isolated client workspaces."
                }
            ],
            "feasibility_score": 84,
            "market_viability_score": 81,
            "execution_complexity": "Moderate",
            "overall_risk_rating": "Moderate"
        })

    # 5. MVP Feature Recommendation Agent Request
    elif "mvp" in prompt_lower or "moscow" in prompt_lower:
        return json.dumps({
            "core_features": [
                {
                    "feature_name": "Instant Idea Intake & Smart Parsing Engine",
                    "moscow_category": "Must-Have",
                    "description": "Simple input interface that automatically extracts problem statements, target personas, and value propositions.",
                    "user_impact": "High",
                    "development_effort": "Low",
                    "sprint_phase": "Phase 1: Core Engine"
                },
                {
                    "feature_name": "Automated Multi-Agent Research Pipeline",
                    "moscow_category": "Must-Have",
                    "description": "Sequential orchestration of search, market calculation, and competitor analysis agents.",
                    "user_impact": "High",
                    "development_effort": "Medium",
                    "sprint_phase": "Phase 1: Core Engine"
                },
                {
                    "feature_name": "Interactive Scorecard & Feasibility Gauge",
                    "moscow_category": "Must-Have",
                    "description": "Visual dashboard summarizing TAM/SAM/SOM, SWOT, risk scoring, and Go/No-Go verdict.",
                    "user_impact": "High",
                    "development_effort": "Low",
                    "sprint_phase": "Phase 1: Core Engine"
                },
                {
                    "feature_name": "Exportable Executive PDF & Markdown Reports",
                    "moscow_category": "Should-Have",
                    "description": "One-click generation of branded, presentation-ready reports for co-founders and investors.",
                    "user_impact": "Medium",
                    "development_effort": "Low",
                    "sprint_phase": "Phase 2: Enhanced Value"
                },
                {
                    "feature_name": "Interactive AI Startup Advisor Chat",
                    "moscow_category": "Should-Have",
                    "description": "Conversational assistant allowing founders to stress-test business models and ask follow-up questions.",
                    "user_impact": "High",
                    "development_effort": "Medium",
                    "sprint_phase": "Phase 2: Enhanced Value"
                },
                {
                    "feature_name": "Custom Integration Webhooks & Notion/Slack Sync",
                    "moscow_category": "Could-Have",
                    "description": "Automated synchronization of validated outputs directly to team communication tools.",
                    "user_impact": "Low",
                    "development_effort": "Medium",
                    "sprint_phase": "Phase 3: Scale & Ecosystem"
                },
                {
                    "feature_name": "Full Multi-Tenant Enterprise Role Hierarchy",
                    "moscow_category": "Won't-Have (v1)",
                    "description": "Complex RBAC permissions and custom SSO configurations reserved for enterprise V2.",
                    "user_impact": "Low",
                    "development_effort": "High",
                    "sprint_phase": "Phase 3: Scale & Ecosystem"
                }
            ],
            "recommended_tech_stack": {
                "Frontend": "Modern Streamlit / React + Tailwind CSS with dark-mode glassmorphism",
                "Backend": "Python 3.12 (FastAPI / Streamlit Native Multi-threading)",
                "AI Agent Layer": "LangChain / Direct Provider Clients (Groq, Gemini, OpenAI)",
                "Search Layer": "Tavily Search API with DDGS live fallback",
                "Data & Export": "Pydantic V2 + ReportLab PDF Generator"
            },
            "estimated_build_time_weeks": 4,
            "estimated_mvp_budget_usd": "$1,500 - $4,500",
            "critical_success_metric": "30+ verified founder validation runs with >= 70% completing full report export and giving 4+ star utility rating."
        })

    # 6. GTM Strategy Agent Request
    elif "gtm" in prompt_lower or "go-to-market" in prompt_lower or "first 100" in prompt_lower:
        return json.dumps({
            "ideal_customer_profile": f"Early-stage venture builders, solo technical founders, startup incubators, and boutique consultancies in {domain}.",
            "positioning_statement": "For entrepreneurs and product builders who need fast, rigorous market validation, our AI Validator provides exhaustive data-backed viability reports in under 3 minutes, unlike slow, expensive market research agencies.",
            "primary_acquisition_channels": [
                {
                    "channel": "Community-Led Organic (Product Hunt, Reddit r/startups, IndieHackers)",
                    "details": "Launch transparent 'Building in Public' breakdowns of famous startup ideas and offer 50 free validation audits to active community members."
                },
                {
                    "channel": "Founder & Accelerator Partnerships",
                    "details": "Partner with regional startup incubators, university entrepreneurship cells, and angel syndicates as an official idea screening partner."
                },
                {
                    "channel": "High-Intent SEO & Free Micro-Tools",
                    "details": "Create free indexable tools such as 'Startup TAM Calculator' and 'Competitor Matrix Generator' that funnel traffic into the full validator."
                }
            ],
            "first_100_customers_playbook": [
                "Week 1: Direct outreach to 150 early-stage founders on Twitter/LinkedIn offering a free comprehensive validation report of their current pitch.",
                "Week 2: Launch on Product Hunt, Hacker News Show HN, and IndieHackers with a video demonstration and actionable sample reports.",
                "Week 3: Run a virtual teardown workshop: 'Validating 10 Live Startup Ideas in 60 Minutes' in founder communities.",
                "Week 4: Introduce referral incentive: founders who invite 2 peers unlock advanced PDF investor-ready slide exports."
            ],
            "pricing_strategy": {
                "model": "Freemium + Pay-Per-Validation + Pro Subscription",
                "recommended_tiers": [
                    {"tier": "Starter (Free)", "price": "$0", "target": "1 Full Validation + Web Overview"},
                    {"tier": "Founder Pass", "price": "$29 / month", "target": "Unlimited validations, full PDF exports & AI Advisor chat"},
                    {"tier": "Incubator / Studio", "price": "$149 / month", "target": "Batch idea screening, custom branding & investor export packs"}
                ]
            },
            "unit_economics_estimate": {
                "Target CAC": "$22 - $45 (Blended)",
                "Estimated LTV": "$180 - $350",
                "LTV / CAC Ratio": "4.8x - 7.7x (Extremely Healthy)",
                "Target Payback Period": "< 45 Days"
            }
        })

    # 7. Final Report / Executive Summary Request
    elif "report" in prompt_lower or "verdict" in prompt_lower or "summary" in prompt_lower:
        return json.dumps({
            "executive_verdict": "STRONG GO WITH FOCUS",
            "composite_viability_score": 85,
            "executive_summary": "The proposed startup addresses an acute operational bottleneck with clear commercial demand and favorable market timing. While competition exists from legacy incumbents, their slow release cadence and high price barriers create a high-value white space for an agile, AI-first solution. Execution focus should be placed on an ultra-simple MVP and founder-led community distribution.",
            "key_recommendations": [
                "Launch the core Must-Have features within a strict 4-week development sprint to start gathering user feedback immediately.",
                "Avoid building heavyweight enterprise features in Version 1; focus obsessively on speed, accuracy, and workflow simplicity.",
                "Leverage organic founder communities and micro-tools to secure the first 100 passionate early adopters before allocating paid ad spend."
            ]
        })

    # 8. Conversational Advisor Response
    return f"Based on our comprehensive multi-agent validation report for your startup idea in **{domain}**, here is strategic advice:\n\n1. **Core Priority**: Focus immediately on the Must-Have MVP features identified in the MoSCoW roadmap.\n2. **Defensibility**: Your strongest moat lies in vertical workflow stickiness and proprietary prompt optimization rather than raw foundation models.\n3. **First 100 Users**: Execute the community-led organic playbook across IndieHackers and niche LinkedIn groups.\n\nWhat specific aspect would you like to explore deeper: market sizing, competitor counter-moves, MVP sprint planning, or investor pitching?"
