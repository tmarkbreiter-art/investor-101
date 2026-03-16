"""
AXIOM US — vNext Portfolio Engine
Rules-based sizing. No AI. Enforces caps, cash reserve.
"""
from collections import defaultdict


def build_portfolio(config, scored_stocks, budget):
    candidates = [s for s in scored_stocks if s["factor_score"].verdict != "PASS"]
    if not candidates:
        return []

    for s in candidates:
        fs = s["factor_score"]
        if fs.verdict == "BUY":
            s["base_alloc_pct"] = config.BUY_HIGH_ALLOC if fs.total >= 90 else config.BUY_MED_ALLOC
        else:
            s["base_alloc_pct"] = config.HOLD_HIGH_ALLOC if fs.total >= 75 else config.HOLD_MED_ALLOC

    investable = budget * (1 - config.CASH_RESERVE)
    raw = []
    for s in candidates:
        d = max(min(investable * s["base_alloc_pct"], budget * config.MAX_ALLOC_PCT), budget * config.MIN_ALLOC_PCT)
        raw.append((s, d))

    sector_totals = defaultdict(float)
    for s, d in raw: sector_totals[s["sector"]] += d

    adjusted = []
    for s, raw_d in raw:
        st  = sector_totals[s["sector"]]
        cap = budget * config.SECTOR_MAX_PCT
        d   = raw_d * (cap / st) if st > cap else raw_d
        s["alloc_dollar"] = round(d, 0)
        s["alloc_pct"]    = round(d / budget * 100, 1)
        adjusted.append(s)

    total = sum(s["alloc_dollar"] for s in adjusted)
    if total > investable:
        scale = investable / total
        for s in adjusted:
            s["alloc_dollar"] = round(s["alloc_dollar"] * scale, 0)
            s["alloc_pct"]    = round(s["alloc_dollar"] / budget * 100, 1)

    for s in adjusted:
        gr = s["guardrails"]
        s["buy_lo"] = gr.buy_lo; s["buy_hi"] = gr.buy_hi
        s["stop_loss"] = gr.stop_loss; s["target"] = gr.target

    return sorted(adjusted, key=lambda s: s["alloc_dollar"], reverse=True)[:config.MAX_POSITIONS]
