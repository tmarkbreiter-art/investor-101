"""
AXIOM US — vNext Dashboard
Clearly separates MEASURED SIGNALS from AI COMMENTARY.
"""
from datetime import datetime
import pytz


def _fmt(n):
    return f"${n:,.2f}" if isinstance(n, (int, float)) else "$-"

def _vc(verdict):
    if verdict == "BUY":  return {"bg":"#F0FDF4","border":"#059669","text":"#059669"}
    if verdict == "PASS": return {"bg":"#FFF1F2","border":"#DC2626","text":"#DC2626"}
    return {"bg":"#FFFBEB","border":"#D97706","text":"#D97706"}

def _fear_color(fear):
    return {"EXTREME FEAR":"#DC2626","HIGH FEAR":"#DC2626","ELEVATED":"#D97706",
            "NEUTRAL":"#57534E","GREED":"#059669"}.get(fear,"#57534E")

def _regime(pulse):
    fear = pulse.get("fear_level","NEUTRAL"); spy = pulse.get("spy_dp",0)
    if fear in ("EXTREME FEAR","HIGH FEAR"): return "RISK-OFF","#DC2626"
    if fear == "GREED" and spy > 0:          return "BULL MARKET","#059669"
    if spy < -1:                             return "CAUTION","#D97706"
    return "NEUTRAL / MIXED","#D97706"


class DashboardGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self, portfolio, pulse, budget):
        et  = pytz.timezone("US/Eastern")
        now = datetime.now(et)
        date_str = now.strftime("%A, %B %-d %Y")
        time_str = now.strftime("%-I:%M %p ET")

        regime, regime_color = _regime(pulse)
        fear       = pulse.get("fear_level","NEUTRAL")
        fear_color = _fear_color(fear)
        quotes     = pulse.get("quotes",{})
        spy  = quotes.get("SPY",{});  qqq  = quotes.get("QQQ",{})
        uso  = quotes.get("USO",{});  vixy = quotes.get("VIXY",{})

        n_buy    = sum(1 for p in portfolio if p["factor_score"].verdict=="BUY")
        n_hold   = sum(1 for p in portfolio if p["factor_score"].verdict=="HOLD")
        invested = sum(p.get("alloc_dollar",0) for p in portfolio)
        cash     = round(budget * self.config.CASH_RESERVE)
        cards    = "
".join(self._card(p) for p in portfolio)

        def pv(q, key, fmt=".2f"):
            v = q.get(key,0)
            return f"{v:{fmt}}"
        def pc(q):
            return "var(--green)" if q.get("dp",0)>=0 else "var(--red)"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>INVESTOR 101 · AXIOM US · {date_str}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,800;1,9..144,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{{
  --page:#F5F0E8;--card:#fff;--card2:#FAFAF7;--border:#E2DDD4;--border2:#EDE9E0;
  --ink:#1A1614;--text:#57534E;--muted:#9D9690;
  --green:#059669;--green-bg:#F0FDF4;--red:#DC2626;--red-bg:#FFF1F2;
  --orange:#D97706;--orange-bg:#FFFBEB;--blue:#1D4ED8;--blue-bg:#EFF6FF;
  --display:"Fraunces",Georgia,serif;--body:"Plus Jakarta Sans",system-ui,sans-serif;--mono:"JetBrains Mono",monospace;
  --r:12px;--R:16px;--s:0 1px 3px rgba(0,0,0,.06);--S:0 8px 24px rgba(0,0,0,.08);
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--page);color:var(--ink);font-family:var(--body);font-size:14px;line-height:1.6;}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 16px 60px;}}
.topbar{{background:var(--card);border-bottom:1px solid var(--border);padding:0 20px;margin-bottom:20px;}}
.tbi{{display:flex;align-items:center;justify-content:space-between;height:58px;gap:12px;flex-wrap:wrap;}}
.brand{{display:flex;align-items:center;gap:10px;}}
.logo{{width:32px;height:32px;background:var(--ink);border-radius:7px;display:flex;align-items:center;justify-content:center;}}
.logo svg{{width:18px;height:18px;fill:none;stroke:#fff;stroke-width:2.5;}}
.bname{{font-family:var(--display);font-size:17px;font-weight:700;}}
.bname span{{color:var(--green);}}
.tbr{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
.tbs{{background:var(--card2);border:1px solid var(--border);border-radius:7px;padding:4px 10px;}}
.tbs-l{{font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;}}
.tbs-v{{font-family:var(--mono);font-size:13px;font-weight:700;}}
.tbdate{{font-size:11px;color:var(--muted);font-family:var(--mono);}}
.pulse{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;}}
.pi{{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:12px 16px;flex:1;min-width:120px;box-shadow:var(--s);}}
.pi-l{{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;margin-bottom:3px;}}
.pi-v{{font-family:var(--display);font-size:20px;font-weight:700;margin-bottom:2px;}}
.pi-c{{font-size:11px;font-weight:600;}}
.regime{{background:var(--card);border:1px solid var(--border);border-radius:var(--R);padding:20px 24px;margin-bottom:16px;box-shadow:var(--s);}}
.stats{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:20px;}}
.sb{{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px;box-shadow:var(--s);}}
.sb-l{{font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.5px;text-transform:uppercase;margin-bottom:6px;}}
.sb-v{{font-family:var(--display);font-size:20px;font-weight:700;}}
.sb-s{{font-size:11px;color:var(--muted);margin-top:2px;}}
.sec-hdr{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px;}}
.sec-t{{font-family:var(--display);font-size:20px;font-weight:700;}}
.sec-s{{font-size:12px;color:var(--muted);}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(370px,1fr));gap:12px;margin-bottom:24px;}}
.scard{{background:var(--card);border:1px solid var(--border);border-radius:var(--R);overflow:hidden;box-shadow:var(--s);border-top:3px solid var(--ac,#1A1614);transition:box-shadow .2s;}}
.scard:hover{{box-shadow:var(--S);}}
.sc-top{{padding:16px 18px 12px;display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1px solid var(--border2);}}
.sc-sym{{font-family:var(--display);font-size:28px;font-weight:800;letter-spacing:-1px;color:var(--ac,var(--ink));}}
.sc-name{{font-size:13px;font-weight:600;margin-bottom:2px;}}
.sc-sec{{display:inline-block;font-size:10px;font-weight:600;background:var(--card2);border:1px solid var(--border);border-radius:20px;padding:2px 9px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}}
.sc-right{{text-align:right;}}
.verdict{{font-size:12px;font-weight:800;letter-spacing:1px;padding:5px 14px;border-radius:20px;border:1.5px solid;text-transform:uppercase;margin-bottom:8px;display:inline-block;}}
.sc-dollar{{font-family:var(--display);font-size:22px;font-weight:700;}}
.sc-pct{{font-size:11px;color:var(--muted);}}
.sc-price{{padding:12px 18px;background:#FAFAF7;border-bottom:1px solid var(--border2);}}
.price-val{{font-family:var(--mono);font-size:20px;font-weight:700;margin-bottom:4px;}}
.chg{{display:inline-block;font-size:12px;font-weight:700;padding:2px 10px;border-radius:20px;margin-bottom:8px;}}
.range-lbl{{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-bottom:4px;}}
.range-track{{height:5px;background:linear-gradient(90deg,var(--red-bg),var(--orange-bg),var(--green-bg));border-radius:3px;position:relative;border:1px solid var(--border);}}
.range-pin{{position:absolute;top:50%;transform:translateY(-50%);width:8px;height:12px;background:var(--ink);border-radius:2px;box-shadow:0 0 0 2px #fff,0 0 0 3px var(--ink);}}
.trace{{padding:12px 18px;border-bottom:1px solid var(--border2);}}
.trace-t{{font-size:10px;font-weight:700;letter-spacing:1px;color:var(--muted);text-transform:uppercase;margin-bottom:8px;}}
.score-total{{font-family:var(--mono);font-size:22px;font-weight:700;color:var(--ac,var(--ink));margin-bottom:8px;}}
.score-bars{{display:flex;flex-direction:column;gap:5px;}}
.sbar{{display:flex;align-items:center;gap:8px;font-size:11px;}}
.sbar-l{{width:70px;color:var(--text);font-weight:600;}}
.sbar-t{{flex:1;height:6px;background:var(--border);border-radius:3px;overflow:hidden;}}
.sbar-f{{height:100%;border-radius:3px;}}
.sbar-v{{width:32px;text-align:right;font-family:var(--mono);font-weight:700;}}
.checks{{padding:12px 18px;border-bottom:1px solid var(--border2);}}
.cl-t{{font-size:10px;font-weight:700;letter-spacing:1px;color:var(--muted);text-transform:uppercase;margin-bottom:8px;}}
.cli{{display:flex;align-items:flex-start;gap:8px;margin-bottom:5px;font-size:12px;}}
.cli-icon{{font-size:13px;flex-shrink:0;margin-top:1px;}}
.cli-name{{font-weight:700;min-width:110px;}}
.cli-detail{{color:var(--text);}}
.levels{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--border2);border-top:1px solid var(--border2);}}
.lbox{{background:var(--card);padding:10px 14px;}}
.lbox-l{{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:3px;}}
.lbox-v{{font-family:var(--mono);font-size:15px;font-weight:700;}}
.sc-ai{{padding:12px 18px;border-top:1px solid var(--border2);background:#FAFDF7;}}
.ai-badge{{display:inline-block;font-size:9px;font-weight:700;letter-spacing:1px;background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;border-radius:20px;padding:2px 8px;margin-bottom:6px;text-transform:uppercase;}}
.ai-why{{font-size:13px;color:var(--text);line-height:1.7;margin-bottom:6px;}}
.ai-watch{{font-size:12px;color:var(--ink);background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;padding:6px 10px;border-left:3px solid #D97706;}}
.sc-mas{{display:flex;gap:12px;padding:8px 18px;background:var(--card2);border-top:1px solid var(--border2);}}
.ma{{font-size:11px;color:var(--muted);font-family:var(--mono);}}
.ma strong{{color:var(--ink);}}
.footer{{text-align:center;font-size:11px;color:var(--muted);padding-top:20px;border-top:1px solid var(--border);margin-top:40px;line-height:1.8;}}
</style>
</head>
<body>
<div class="topbar"><div class="tbi">
  <div class="brand">
    <div class="logo"><svg viewBox="0 0 24 24"><path d="M2 12l5-5 4 4 5-6 4 3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
    <div class="bname">INVESTOR <span>101</span> <span style="font-weight:400;font-size:12px;color:var(--muted)">· AXIOM US</span></div>
  </div>
  <div class="tbr">
    <div class="tbs"><div class="tbs-l">Budget</div><div class="tbs-v">{_fmt(budget)}</div></div>
    <div class="tbs"><div class="tbs-l">Invested</div><div class="tbs-v">{_fmt(invested)}</div></div>
    <div class="tbs"><div class="tbs-l">Cash</div><div class="tbs-v">{_fmt(cash)}</div></div>
    <div class="tbs"><div class="tbs-l">Signals</div><div class="tbs-v" style="color:var(--green)">{n_buy} BUY · <span style="color:var(--orange)">{n_hold} HOLD</span></div></div>
    <div class="tbdate">{date_str} · {time_str}</div>
  </div>
</div></div>
<div class="wrap">
  <div class="pulse">
    <div class="pi"><div class="pi-l">S&amp;P 500 · SPY</div><div class="pi-v" style="color:{pc(spy)}">${pv(spy,'price')}</div><div class="pi-c" style="color:{pc(spy)}">{spy.get('dp',0):+.1f}% today</div></div>
    <div class="pi"><div class="pi-l">Nasdaq · QQQ</div><div class="pi-v" style="color:{pc(qqq)}">${pv(qqq,'price')}</div><div class="pi-c" style="color:{pc(qqq)}">{qqq.get('dp',0):+.1f}% today</div></div>
    <div class="pi"><div class="pi-l">Oil · USO</div><div class="pi-v">${pv(uso,'price')}</div><div class="pi-c" style="color:{'var(--red)' if uso.get('dp',0)>3 else 'var(--green)'}">{uso.get('dp',0):+.1f}% today</div></div>
    <div class="pi"><div class="pi-l">Fear Index · VIXY</div><div class="pi-v" style="color:{fear_color}">${pv(vixy,'price')}</div><div class="pi-c" style="color:{fear_color}">{fear}</div></div>
  </div>
  <div class="regime">
    <div style="font-size:10px;font-weight:700;letter-spacing:1px;color:var(--muted);text-transform:uppercase;margin-bottom:4px">Market Regime · Rules-Based Signal</div>
    <div style="font-family:var(--display);font-size:24px;font-weight:700;color:{regime_color}">{regime}</div>
    <div style="font-size:13px;color:var(--text);margin-top:6px">Determined by SPY momentum, VIXY fear gauge, and USO energy signal. Not AI-generated.</div>
  </div>
  <div class="stats">
    <div class="sb"><div class="sb-l">Buy Signals</div><div class="sb-v" style="color:var(--green)">{n_buy}</div><div class="sb-s">rules-verified</div></div>
    <div class="sb"><div class="sb-l">Hold</div><div class="sb-v" style="color:var(--orange)">{n_hold}</div><div class="sb-s">watch for entry</div></div>
    <div class="sb"><div class="sb-l">Invested</div><div class="sb-v">{_fmt(invested)}</div><div class="sb-s">{len(portfolio)} positions</div></div>
    <div class="sb"><div class="sb-l">Cash Reserve</div><div class="sb-v">{_fmt(cash)}</div><div class="sb-s">{self.config.CASH_RESERVE*100:.0f}% kept safe</div></div>
  </div>
  <div class="sec-hdr">
    <div class="sec-t">Today's Portfolio</div>
    <div class="sec-s">Scores &amp; decisions are deterministic · AI used only for commentary · Updated {time_str}</div>
  </div>
  <div class="grid">{cards}</div>
  <div class="footer">
    <strong>INVESTOR 101 · AXIOM US</strong> · Auto-generated {date_str} at {time_str} ET<br>
    For educational purposes only · Not investment advice · All investments carry risk including loss of principal<br>
    Data: Finnhub · yfinance &nbsp;|&nbsp; Commentary: Groq/Gemini &nbsp;|&nbsp; Decisions: Rules-based Python model
  </div>
</div></body></html>"""

    def _card(self, p):
        sym=p["symbol"]; name=p["name"]; sector=p["sector"]
        price=p["price"]; dp=p["dp"]
        h52=p.get("h52",price*1.2); l52=p.get("l52",price*0.8)
        fs=p["factor_score"]; gr=p["guardrails"]
        verdict=fs.verdict
        alloc_d=p.get("alloc_dollar",0); alloc_pct=p.get("alloc_pct",0)
        buy_lo=p.get("buy_lo",price); buy_hi=p.get("buy_hi",price)
        stop=p.get("stop_loss",round(price*0.92,2)); target=p.get("target",round(price*1.15,2))
        ai_why=p.get("ai_why",""); ai_watch=p.get("ai_watch","")
        vc=_vc(verdict)
        ac="059669" if verdict=="BUY" else "D97706" if verdict=="HOLD" else "DC2626"
        chg_c="var(--green)" if dp>=0 else "var(--red)"
        chg_bg="var(--green-bg)" if dp>=0 else "var(--red-bg)"
        rng=h52-l52; pos52=round((price-l52)/rng*100,1) if rng else 50
        mas=gr.mas
        def mav(k): return f"${mas[k]:.2f}" if mas.get(k) else "—"
        def bcolor(val,mx):
            p=val/mx if mx else 0
            return "#059669" if p>0.7 else "#D97706" if p>0.4 else "#DC2626"
        wt=self.config.W_TECHNICAL; wr=self.config.W_RISK; wq=self.config.W_QUALITY
        wm=self.config.W_MACRO; we=self.config.W_EVENT
        icon={"ok":"✅","warn":"⚠️","block":"❌","warning":"⚠️"}
        return f"""<div class="scard" style="--ac:#{ac}">
  <div class="sc-top">
    <div><div class="sc-sym">{sym}</div><div class="sc-name">{name}</div><div class="sc-sec">{sector}</div></div>
    <div class="sc-right">
      <div class="verdict" style="background:{vc['bg']};color:{vc['text']};border-color:{vc['border']}">{verdict}</div>
      <div class="sc-dollar">{_fmt(alloc_d)}</div>
      <div class="sc-pct">{alloc_pct:.1f}% of budget</div>
    </div>
  </div>
  <div class="sc-price">
    <div class="price-val">${price:.2f}</div>
    <div class="chg" style="background:{chg_bg};color:{chg_c}">{dp:+.1f}% today</div>
    <div class="range-lbl"><span>52wk low ${l52:.2f}</span><span style="color:#9D9690">{pos52:.0f}% up</span><span>${h52:.2f} high</span></div>
    <div class="range-track"><div class="range-pin" style="left:calc({pos52}% - 4px)"></div></div>
  </div>
  <div class="trace">
    <div class="trace-t">📊 Measured Signals — Score: {fs.total:.0f} / 100</div>
    <div class="score-bars">
      <div class="sbar"><span class="sbar-l">Technical</span><div class="sbar-t"><div class="sbar-f" style="width:{fs.technical/wt*100:.0f}%;background:{bcolor(fs.technical,wt)}"></div></div><span class="sbar-v">{fs.technical:.0f}/{wt}</span></div>
      <div class="sbar"><span class="sbar-l">Risk</span><div class="sbar-t"><div class="sbar-f" style="width:{fs.risk/wr*100:.0f}%;background:{bcolor(fs.risk,wr)}"></div></div><span class="sbar-v">{fs.risk:.0f}/{wr}</span></div>
      <div class="sbar"><span class="sbar-l">Quality</span><div class="sbar-t"><div class="sbar-f" style="width:{fs.quality/wq*100:.0f}%;background:{bcolor(fs.quality,wq)}"></div></div><span class="sbar-v">{fs.quality:.0f}/{wq}</span></div>
      <div class="sbar"><span class="sbar-l">Macro</span><div class="sbar-t"><div class="sbar-f" style="width:{fs.macro/wm*100:.0f}%;background:{bcolor(fs.macro,wm)}"></div></div><span class="sbar-v">{fs.macro:.0f}/{wm}</span></div>
      <div class="sbar"><span class="sbar-l">Event</span><div class="sbar-t"><div class="sbar-f" style="width:{fs.event/we*100:.0f}%;background:{bcolor(fs.event,we)}"></div></div><span class="sbar-v">{fs.event:.0f}/{we}</span></div>
    </div>
  </div>
  <div class="checks">
    <div class="cl-t">Guardrail Checks</div>
    <div class="cli"><span class="cli-icon">{icon.get(gr.no_chase_status,"⚠️")}</span><span class="cli-name">No-Chase Rule</span><span class="cli-detail">{gr.no_chase_detail}</span></div>
    <div class="cli"><span class="cli-icon">{icon.get(gr.trend_status,"⚠️")}</span><span class="cli-name">Trend Alignment</span><span class="cli-detail">{gr.trend_detail}</span></div>
    <div class="cli"><span class="cli-icon">{icon.get(gr.pos52_status,"⚠️")}</span><span class="cli-name">52wk Position</span><span class="cli-detail">{gr.pos52_detail}</span></div>
  </div>
  <div class="levels">
    <div class="lbox"><div class="lbox-l">Buy Range</div><div class="lbox-v" style="color:var(--green)">${buy_lo:.2f}–${buy_hi:.2f}</div></div>
    <div class="lbox"><div class="lbox-l">Stop Loss</div><div class="lbox-v" style="color:var(--red)">${stop:.2f}</div></div>
    <div class="lbox"><div class="lbox-l">Target</div><div class="lbox-v" style="color:var(--blue)">${target:.2f}</div></div>
  </div>
  <div class="sc-ai">
    <div class="ai-badge">🤖 AI Commentary — not the decision engine</div>
    <div class="ai-why">{ai_why}</div>
    <div class="ai-watch">⚠️ Watch: {ai_watch}</div>
  </div>
  <div class="sc-mas"><span class="ma">MA5 <strong>{mav("ma5")}</strong></span><span class="ma">MA10 <strong>{mav("ma10")}</strong></span><span class="ma">MA20 <strong>{mav("ma20")}</strong></span></div>
</div>"""
