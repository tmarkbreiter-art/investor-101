# INVESTOR 101 · AXIOM US

Rules-based daily US equity advisor. Scores 26 stocks every weekday at 8:00 AM ET.
Publishes a live dashboard to GitHub Pages.

## Live Dashboard
**[View it here](https://YOUR_USERNAME.github.io/investor-101)**

## How It Works
- `src/factor_model.py` — deterministic 100-pt scoring engine (no AI decisions)
- `src/portfolio_engine.py` — rules-based position sizing with sector caps
- `src/ai_commentary.py` — AI explains verdicts only, never changes them
- `src/dashboard.py` — generates the HTML dashboard
- `.github/workflows/daily.yml` — runs automatically at 8 AM ET Mon–Fri

## Setup
See SETUP.md for step-by-step instructions.

## Disclaimer
For educational purposes only. Not investment advice.
