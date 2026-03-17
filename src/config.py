"""
AXIOM US — vNext Configuration
Rules-first engine. No secrets in code — all read from environment variables.
"""
import os

class Config:
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")

    BUDGET        = float(os.getenv("BUDGET", "500"))
    CASH_RESERVE  = 0.08
    MAX_POSITIONS = 10

    NO_CHASE_WARN_PCT = 5.0
    NO_CHASE_HARD_PCT = 10.0
    STOP_LOSS_PCT     = 0.08
    BASE_TARGET_PCT   = 0.15

    W_TECHNICAL = 40
    W_RISK      = 20
    W_QUALITY   = 20
    W_MACRO     = 10
    W_EVENT     = 10

    SCORE_BUY_MIN  = 80
    SCORE_HOLD_MIN = 65

    BUY_HIGH_ALLOC  = 0.12
    BUY_MED_ALLOC   = 0.08
    HOLD_HIGH_ALLOC = 0.05
    HOLD_MED_ALLOC  = 0.03

    MIN_ALLOC_PCT  = 0.03
    MAX_ALLOC_PCT  = 0.15
    SECTOR_MAX_PCT = 0.30

    EMAIL_SENDER    = os.getenv("EMAIL_SENDER", "")
    EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_RECEIVERS = os.getenv("EMAIL_RECEIVERS", "")

    WATCHLIST     = [s.strip() for s in os.getenv("WATCHLIST","").split(",") if s.strip()]
    PULSE_SYMBOLS = ["SPY", "QQQ", "USO", "VIXY"]

    SCAN_UNIVERSE = [
        {"symbol": "NVDA",  "name": "NVIDIA",        "sector": "Technology"},
        {"symbol": "AAPL",  "name": "Apple",          "sector": "Technology"},
        {"symbol": "MSFT",  "name": "Microsoft",      "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet",       "sector": "Technology"},
        {"symbol": "META",  "name": "Meta",           "sector": "Technology"},
        {"symbol": "PLTR",  "name": "Palantir",       "sector": "Technology"},
        {"symbol": "CRWD",  "name": "CrowdStrike",    "sector": "Technology"},
        {"symbol": "SNOW",  "name": "Snowflake",      "sector": "Technology"},
        {"symbol": "AMZN",  "name": "Amazon",         "sector": "Technology"},
        {"symbol": "TSLA",  "name": "Tesla",          "sector": "Technology"},
        {"symbol": "XOM",   "name": "ExxonMobil",     "sector": "Energy"},
        {"symbol": "OXY",   "name": "Occidental",     "sector": "Energy"},
        {"symbol": "CVX",   "name": "Chevron",        "sector": "Energy"},
        {"symbol": "COP",   "name": "ConocoPhillips", "sector": "Energy"},
        {"symbol": "SLB",   "name": "SLB",            "sector": "Energy"},
    ]
    SYMBOL_MAP = {s["symbol"]: s for s in SCAN_UNIVERSE}
