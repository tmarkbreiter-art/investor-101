name: AXIOM Daily + Market Hours Refresh

on:
  schedule:
    # Run every 30 minutes Mon-Fri during market hours (9:00am - 4:30pm ET = 13:00-20:30 UTC)
    - cron: "0,30 13-20 * * 1-5"
    # Also run once at 6am ET daily for pre-market snapshot
    - cron: "0 10 * * 1-5"
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run AXIOM
        env:
          FINNHUB_API_KEY: ${{ secrets.FINNHUB_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python main.py

      - name: Commit and push dashboard
        run: |
          git config user.name "axiom-bot"
          git config user.email "axiom@bot.com"
          git add docs/index.html
          git diff --staged --quiet || git commit -m "auto: refresh $(date -u '+%Y-%m-%d %H:%M UTC')"
          git push
