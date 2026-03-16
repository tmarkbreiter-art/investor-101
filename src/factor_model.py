"""
AXIOM US — vNext Factor Model
Deterministic scoring + guardrails. No AI decisions.
"""
import math
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Guardrails:
    no_chase_status: str
    no_chase_detail: str
    trend_status: str
    trend_detail: str
    pos52_status: str
    pos52_detail: str
    stop_loss: float
    target: float
    buy_lo: float
    buy_hi: float
    deviation_pct: Optional[float]
    alignment: str
    block_buy: bool
    warn_buy: bool
    mas: dict


@dataclass
class FactorScore:
    technical: float
    risk: float
    quality: float
    macro: float
    event: float
    total: float
    verdict: str
    reasons: List[str]


def _compute_mas(prices):
    def ma(n):
        tail = [p for p in prices if p and p > 0]
        if len(tail) < n: return None
        return round(sum(tail[-n:]) / n, 4)
    return {"ma5": ma(5), "ma10": ma(10), "ma20": ma(20)}


def compute_guardrails(config, symbol, price, history, h52, l52):
    mas = _compute_mas(history)
    ma5, ma10, ma20 = mas.get("ma5"), mas.get("ma10"), mas.get("ma20")

    no_chase_status = "warning"; no_chase_detail = "Insufficient history for MA20"
    deviation_pct = None
    if ma20 and ma20 > 0:
        deviation_pct = (price - ma20) / ma20 * 100
        if deviation_pct > config.NO_CHASE_HARD_PCT:
            no_chase_status = "block"; no_chase_detail = f"+{deviation_pct:.1f}% above MA20 - too extended"
        elif deviation_pct > config.NO_CHASE_WARN_PCT:
            no_chase_status = "warn";  no_chase_detail = f"+{deviation_pct:.1f}% above MA20 - caution"
        else:
            no_chase_status = "ok";    no_chase_detail = f"{deviation_pct:+.1f}% from MA20 - safe zone"

    trend_status = "warning"; trend_detail = "Insufficient history"; alignment = "unknown"
    if ma5 and ma10 and ma20:
        if ma5 > ma10 > ma20:
            alignment = "bull"; trend_status = "ok"
            trend_detail = f"MA5 {ma5:.2f} > MA10 {ma10:.2f} > MA20 {ma20:.2f} - bull"
        elif ma5 < ma10:
            alignment = "bear"; trend_status = "block"
            trend_detail = f"MA5 {ma5:.2f} < MA10 {ma10:.2f} - weakness"
        else:
            alignment = "mixed"; trend_status = "warn"
            trend_detail = f"MA5/MA10 OK but MA10 < MA20 - mixed"

    pos52_status = "warn"; pos52_detail = "52wk range unavailable"
    rng = h52 - l52
    if rng > 0:
        pos = (price - l52) / rng * 100
        if pos > 90:   pos52_status = "warn"; pos52_detail = f"Near 52wk high ({h52:.2f}) - elevated risk"
        elif pos < 20: pos52_status = "warn"; pos52_detail = f"Near 52wk low ({l52:.2f}) - check fundamentals"
        else:          pos52_status = "ok";   pos52_detail = f"{pos:.0f}% up from 52wk low - healthy"

    stop_loss = round(price * (1 - config.STOP_LOSS_PCT), 2)
    target    = round(price * (1 + config.BASE_TARGET_PCT), 2)

    if ma5 and alignment in ("bull", "mixed") and price < ma5 * 1.01:
        buy_lo = round(ma5 * 0.995, 2); buy_hi = round(ma5 * 1.005, 2)
    else:
        buy_lo = round(price * 0.997, 2); buy_hi = round(price * 1.003, 2)

    block_buy = (deviation_pct is not None and deviation_pct > config.NO_CHASE_HARD_PCT) or alignment == "bear"
    warn_buy  = (deviation_pct is not None and config.NO_CHASE_WARN_PCT < deviation_pct <= config.NO_CHASE_HARD_PCT) or alignment == "mixed"

    return Guardrails(
        no_chase_status=no_chase_status, no_chase_detail=no_chase_detail,
        trend_status=trend_status, trend_detail=trend_detail,
        pos52_status=pos52_status, pos52_detail=pos52_detail,
        stop_loss=stop_loss, target=target, buy_lo=buy_lo, buy_hi=buy_hi,
        deviation_pct=deviation_pct, alignment=alignment,
        block_buy=block_buy, warn_buy=warn_buy, mas=mas,
    )


def score_stock(config, stock, guardrails, macro):
    price   = stock.get("price", 0.0)
    metrics = stock.get("metrics", {}) or {}
    sector  = stock.get("sector", "?")
    history = stock.get("history", []) or []
    reasons = []
    blocked = guardrails.block_buy

    # TECHNICAL (40pts)
    wt = config.W_TECHNICAL; tech = 0.0
    dev = guardrails.deviation_pct
    if dev is None:
        tech += wt*0.20*0.3; reasons.append("TECH_MA20_UNKNOWN")
    elif -5 <= dev <= 3:
        tech += wt*0.20*1.0; reasons.append("TECH_MA20_GOOD")
    elif -10 <= dev <= 8:
        tech += wt*0.20*0.6; reasons.append("TECH_MA20_OK")
    else:
        tech += wt*0.20*0.2; reasons.append("TECH_MA20_STRETCHED")

    al = guardrails.alignment
    if   al == "bull":    tech += wt*0.25*1.0; reasons.append("TECH_TREND_BULL")
    elif al == "mixed":   tech += wt*0.25*0.5; reasons.append("TECH_TREND_MIXED")
    elif al == "bear":    tech += wt*0.25*0.1; reasons.append("TECH_TREND_BEAR")
    else:                 tech += wt*0.25*0.3; reasons.append("TECH_TREND_UNKNOWN")

    if len(history) >= 40:
        recent = history[-20:]; older = history[-60:-40] if len(history) >= 60 else history[:20]
        if older and recent:
            slope = (sum(recent)/len(recent) - sum(older)/len(older)) / (sum(older)/len(older))
            if   slope > 0.08:  tech += wt*0.25*1.0; reasons.append("TECH_MOMO_STRONG")
            elif slope > 0.0:   tech += wt*0.25*0.6; reasons.append("TECH_MOMO_POSITIVE")
            elif slope > -0.05: tech += wt*0.25*0.3; reasons.append("TECH_MOMO_FLAT")
            else:               tech += wt*0.25*0.1; reasons.append("TECH_MOMO_NEGATIVE")
    else:
        tech += wt*0.25*0.3; reasons.append("TECH_MOMO_UNKNOWN")

    if guardrails.pos52_status == "ok":
        tech += wt*0.30*0.9; reasons.append("TECH_52WK_HEALTHY")
    else:
        tech += wt*0.30*0.4; reasons.append("TECH_52WK_CAUTIOUS")
    tech = min(max(tech, 0), wt)

    # RISK (20pts)
    wr = config.W_RISK; risk = 0.0
    vol_ratio = 0.25
    if len(history) >= 20 and price > 0:
        w = history[-20:]; avg = sum(w)/len(w)
        std = math.sqrt(sum((p-avg)**2 for p in w)/len(w))
        vol_ratio = std / price
    if   vol_ratio < 0.02: risk += wr*0.40; reasons.append("RISK_VERY_LOW_VOL")
    elif vol_ratio < 0.05: risk += wr*1.00; reasons.append("RISK_COMFORTABLE_VOL")
    elif vol_ratio < 0.10: risk += wr*0.70; reasons.append("RISK_MED_VOL")
    elif vol_ratio < 0.20: risk += wr*0.50; reasons.append("RISK_HIGH_VOL")
    else:                  risk += wr*0.30; reasons.append("RISK_VERY_HIGH_VOL")
    risk = min(max(risk, 0), wr)

    # QUALITY (20pts)
    wq = config.W_QUALITY; qual = 0.0
    pe = metrics.get("pe"); rev_g = metrics.get("rev_growth")
    roe = metrics.get("roe"); debt_eq = metrics.get("debt_eq")

    if   pe is None or pe<=0: qual += wq*0.25*0.4; reasons.append("QUAL_PE_UNKNOWN")
    elif pe < 15:             qual += wq*0.25*1.0; reasons.append("QUAL_PE_CHEAP")
    elif pe < 30:             qual += wq*0.25*0.8; reasons.append("QUAL_PE_REASONABLE")
    elif pe < 60:             qual += wq*0.25*0.6; reasons.append("QUAL_PE_EXPENSIVE")
    else:                     qual += wq*0.25*0.3; reasons.append("QUAL_PE_VERY_EXPENSIVE")

    if   rev_g is None: qual += wq*0.25*0.4; reasons.append("QUAL_REVG_UNKNOWN")
    elif rev_g > 0.20:  qual += wq*0.25*1.0; reasons.append("QUAL_REVG_STRONG")
    elif rev_g > 0.05:  qual += wq*0.25*0.8; reasons.append("QUAL_REVG_OK")
    elif rev_g > 0.0:   qual += wq*0.25*0.6; reasons.append("QUAL_REVG_FLAT")
    else:               qual += wq*0.25*0.3; reasons.append("QUAL_REVG_NEGATIVE")

    if   roe is None: qual += wq*0.25*0.4; reasons.append("QUAL_ROE_UNKNOWN")
    elif roe > 0.20:  qual += wq*0.25*1.0; reasons.append("QUAL_ROE_STRONG")
    elif roe > 0.10:  qual += wq*0.25*0.8; reasons.append("QUAL_ROE_OK")
    elif roe > 0.0:   qual += wq*0.25*0.6; reasons.append("QUAL_ROE_WEAK")
    else:             qual += wq*0.25*0.3; reasons.append("QUAL_ROE_NEGATIVE")

    if   debt_eq is None: qual += wq*0.25*0.4; reasons.append("QUAL_DE_UNKNOWN")
    elif debt_eq < 0.5:   qual += wq*0.25*1.0; reasons.append("QUAL_DE_LOW")
    elif debt_eq < 1.5:   qual += wq*0.25*0.8; reasons.append("QUAL_DE_MODERATE")
    elif debt_eq < 3.0:   qual += wq*0.25*0.6; reasons.append("QUAL_DE_HIGH")
    else:                 qual += wq*0.25*0.3; reasons.append("QUAL_DE_VERY_HIGH")
    qual = min(max(qual, 0), wq)

    # MACRO (10pts)
    wm = config.W_MACRO
    fear = macro.get("fear_level", "NEUTRAL")
    fear_mult = {"GREED":1.0,"NEUTRAL":0.8,"ELEVATED":0.6,"HIGH FEAR":0.4,"EXTREME FEAR":0.3}.get(fear, 0.7)
    favor = (fear in ("HIGH FEAR","EXTREME FEAR") and sector in ("Defense","Energy","Materials","Commodities")) or             (fear not in ("HIGH FEAR","EXTREME FEAR") and sector in ("Technology","Consumer","Finance"))
    macro_s = wm * fear_mult if favor else wm * fear_mult * 0.7
    reasons.append("MACRO_SECTOR_FAVORED" if favor else "MACRO_SECTOR_NEUTRAL")
    macro_s = min(max(macro_s, 0), wm)

    # EVENT (10pts)
    we = config.W_EVENT; event_s = we * 0.7; reasons.append("EVENT_BASELINE")

    total = min(max(tech + risk + qual + macro_s + event_s, 0), 100)

    if blocked:
        verdict = "PASS"; reasons.append("VERDICT_BLOCKED_GUARDRAILS")
    elif total >= config.SCORE_BUY_MIN:
        verdict = "BUY";  reasons.append("VERDICT_BUY_SCORE")
    elif total >= config.SCORE_HOLD_MIN:
        verdict = "HOLD"; reasons.append("VERDICT_HOLD_SCORE")
    else:
        verdict = "PASS"; reasons.append("VERDICT_PASS_SCORE")

    return FactorScore(
        technical=round(tech,1), risk=round(risk,1), quality=round(qual,1),
        macro=round(macro_s,1), event=round(event_s,1), total=round(total,1),
        verdict=verdict, reasons=reasons,
    )
