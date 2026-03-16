"""
AXIOM US - vNext Main Runner
"""
import os, sys
from datetime import datetime
import pytz


def run(config):
    from data_provider    import DataProvider
    from factor_model     import compute_guardrails, score_stock
    from portfolio_engine import build_portfolio
    from ai_commentary    import add_commentary
    from dashboard        import DashboardGenerator
    from notifier         import Notifier

    et  = pytz.timezone("US/Eastern")
    now = datetime.now(et)
    print("AXIOM US vNext - " + now.strftime("%A %B %d %Y %I:%M %p ET"))

    provider  = DataProvider(config)
    generator = DashboardGenerator(config)
    notifier  = Notifier(config)

    print("Fetching market pulse...")
    pulse = provider.fetch_pulse()
    print("  SPY " + str(round(pulse["spy_dp"], 1)) + "%  Fear: " + pulse["fear_level"])

    symbols = [s["symbol"] for s in config.SCAN_UNIVERSE]
    for sym in config.WATCHLIST:
        if sym not in symbols and sym in config.SYMBOL_MAP:
            symbols.insert(0, sym)
    symbols = symbols[:20]

    print("Fetching " + str(len(symbols)) + " stocks...")
    stocks = provider.fetch_all_stocks(symbols)

    print("Computing guardrails and factor scores...")
    scored = []
    for s in stocks:
        gr = compute_guardrails(config, s["symbol"], s["price"], s["history"], s["h52"], s["l52"])
        fs = score_stock(config, s, gr, pulse)
        scored.append({**s, "guardrails": gr, "factor_score": fs})

    n_buy  = sum(1 for s in scored if s["factor_score"].verdict == "BUY")
    n_hold = sum(1 for s in scored if s["factor_score"].verdict == "HOLD")
    print("  " + str(n_buy) + " BUY  " + str(n_hold) + " HOLD")

    print("Building portfolio...")
    portfolio = build_portfolio(config, scored, config.BUDGET)
    print("  " + str(len(portfolio)) + " positions")

    print("Adding AI commentary...")
    if config.GROQ_API_KEY or config.GEMINI_API_KEY:
        portfolio = add_commentary(config, portfolio, pulse)
    else:
        for p in portfolio:
            p["ai_why"]   = "No AI key set - rules score above tells the full story."
            p["ai_watch"] = "Set GROQ_API_KEY or GEMINI_API_KEY in secrets to enable commentary."

    print("Generating dashboard...")
    html = generator.generate(portfolio, pulse, config.BUDGET)
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(html)
    print("  Saved to docs/index.html")

    notifier.send_digest(portfolio, pulse)
    print("Done.")
    return html
