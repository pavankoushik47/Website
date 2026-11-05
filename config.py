"""
Configuration settings for AI Startup Idea Validator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file from the local directory or parent directories if available
load_dotenv(BASE_DIR / ".env")
load_dotenv()

# App Metadata
APP_NAME = "Startup Validator — Multi-Agent Startup Idea Validator"
APP_VERSION = "2.5.0"
APP_TAGLINE = "Validate your startup in minutes with real-time web intelligence and multi-agent reasoning."

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM Providers Configuration
DEFAULT_PROVIDER = "groq" if GROQ_API_KEY else ("gemini" if GEMINI_API_KEY else ("openai" if OPENAI_API_KEY else "auto"))

AVAILABLE_PROVIDERS = {
    "groq": {
        "name": "Groq (Fast Llama-3.3-70B)",
        "default_model": "llama-3.3-70b-versatile",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    },
    "gemini": {
        "name": "Google Gemini",
        "default_model": "gemini-1.5-flash",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
    },
    "openai": {
        "name": "OpenAI / Compatible API",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    },
    "heuristic": {
        "name": "Intelligent Heuristic Engine (Offline / No Key Required)",
        "default_model": "startup-validator-heuristic-engine",
        "models": ["startup-validator-heuristic-engine"],
    }
}

# Web Search Settings
SEARCH_ENGINE = "tavily" if TAVILY_API_KEY else "ddgs"
MAX_SEARCH_RESULTS_PER_QUERY = 5
MAX_SEARCH_QUERIES = 4

# Pipeline Steps Definition
PIPELINE_STEPS = [
    {
        "id": "extraction",
        "name": "Idea Extraction & Parsing",
        "role": "Idea Analysis Agent",
        "icon": "",
        "desc": "Extracts problem, target audience, core value proposition, and industry domain."
    },
    {
        "id": "web_search",
        "name": "Live Web Search & Intelligence",
        "role": "Web Search Agent",
        "icon": "",
        "desc": "Queries real-time market data, trending competitor products, and industry benchmarks."
    },
    {
        "id": "market_analysis",
        "name": "Market Opportunity & Segmentation",
        "role": "Market Analysis Agent",
        "icon": "",
        "desc": "Calculates TAM/SAM/SOM, market growth trajectory, and granular target customer personas."
    },
    {
        "id": "competitor_analysis",
        "name": "Competitor Discovery & Gap Analysis",
        "role": "Competitor Discovery Agent",
        "icon": "",
        "desc": "Maps direct, indirect, and substitute players, offering matrices, and white space opportunities."
    },
    {
        "id": "swot_risk",
        "name": "SWOT & Execution Risk Assessment",
        "role": "SWOT & Risk Agent",
        "icon": "",
        "desc": "Identifies 4-quadrant SWOT, execution pitfalls, regulatory hurdles, and feasibility scoring."
    },
    {
        "id": "mvp_features",
        "name": "MVP Feature Roadmap (MoSCoW)",
        "role": "MVP Recommendation Agent",
        "icon": "",
        "desc": "Prioritizes Must-Have, Should-Have, Could-Have features with a 3-phase release roadmap."
    },
    {
        "id": "gtm_strategy",
        "name": "Go-To-Market & Traction Playbook",
        "role": "GTM Strategy Module",
        "icon": "",
        "desc": "Formulates first 100 customers strategy, acquisition channels, pricing models, and unit economics."
    },
    {
        "id": "financial_feasibility",
        "name": "Financial Feasibility & P&L Modeling",
        "role": "Financial Modeling Agent",
        "icon": "",
        "desc": "Projects 5-year revenue, expenses, profit/loss, break-even timeline, and investment ROI."
    },
    {
        "id": "report_generation",
        "name": "Startup Validation Report & Verdict",
        "role": "Report Generation Agent",
        "icon": "",
        "desc": "Synthesizes multi-agent outputs into an executive report with Go/No-Go verdict and downloadable PDF."
    }
]
