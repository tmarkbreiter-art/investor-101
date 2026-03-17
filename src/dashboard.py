from datetime import datetime
import pytz


def fmt_dollar(n):
    if isinstance(n, (int, float)):
        return "$" + "{:,.2f}".format(n)
    return "$-"


def verdict_colors(verdict):
    if verdict == "BUY":
        return {"bg": "#F0FDF4", "border": "#059669", "text": "#059669"}
    if verdict == "PASS":
        return {"bg": "#FFF1F2", "border": "#DC2626", "text": "#DC2626"}
    return {"bg": "#FFFBEB", "border": "#D97706", "text": "#D97706"}


def fear_color(fear):
    m = {
        "EXTREME FEAR": "#DC2626", "HIGH FEAR": "#DC2626",
        "ELEVATED": "#D97706", "NEUTRAL": "#57534E", "GREED": "#059669"
    }
    return m.get(fear, "#57534E")


def get_regime(pulse):
    fear = pulse.get("fear_level", "NEUTRAL")
    spy = pulse.get("spy_dp", 0)
    if fear in ("EXTREME FEAR", "HIGH FEAR"):
        return "RISK-OFF — Be careful, market is fearful", "#DC2626"
    if fear == "GREED" and spy > 0:
        return "BULL MARKET — Good conditions to invest", "#059669"
    if spy < -1:
        return "CAUTION — Market is shaky, go slow", "#D97706"
    return "MIXED — Market is uncertain, be selective", "#D97706"


def bar_color(val, mx):
    p = val / mx if mx else 0
    if p > 0.7: return "#059669"
    if p > 0.4: return "#D97706"
    return "#DC2626"


def score_badge(total):
    if total >= 80:
        return ("STRONG BUY CANDIDATE", "#059669", "#F0FDF4")
    if total >= 70:
        return ("DECENT PICK", "#D97706", "#FFFBEB")
    return ("WEAK — WAIT", "#DC2626", "#FFF1F2")


def quote_color(dp):
    return "#059669" if dp >= 0 else "#DC2626"


def quote_bg(dp):
    return "#F0FDF4" if dp >= 0 else "#FFF1F2"


def ma_val(mas, key):
    v = mas.get(key)
    return ("$" + "{:.2f}".format(v)) if v else "-"


def check_plain(status, label, detail):
    questions = {
        "No-Chase Rule": "Is the price too high right now?",
        "Trend Alignment": "Is the price trending upward?",
        "52wk Position": "How is it doing vs. the past year?"
    }
    answers = {
        ("No-Chase Rule", "ok"):   "✅ No — price is at a reasonable level",
        ("No-Chase Rule", "warn"): "⚠️ Yes — price has jumped recently, be cautious",
        ("No-Chase Rule", "block"):"❌ Yes — price is too high right now, wait",
        ("Trend Alignment", "ok"):  "✅ Yes — price is moving up steadily",
        ("Trend Alignment", "warn"):"⚠️ Mixed — short-term up but not fully confirmed",
        ("Trend Alignment", "block"):"❌ No — price trend is down, avoid for now",
        ("52wk Position", "ok"):   "✅ Healthy — not at extreme highs or lows",
        ("52wk Position", "warn"):  "⚠️ Near its highest price in a year — elevated risk",
        ("52wk Position", "block"): "❌ At yearly low — could keep falling",
    }
    key = (label, status)
    answer = answers.get(key, "⚠️ " + detail)
    return questions.get(label, label), answer


def get_css():
    return """
:root{
  --page:#F7F5F0;--card:#fff;--card2:#FAFAF7;--border:#E8E3DA;--border2:#EDE9E0;
  --ink:#1A1614;--text:#57534E;--muted:#9D9690;
  --green:#059669;--red:#DC2626;--orange:#D97706;--blue:#1D4ED8;
}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--page);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;line-height:1.6;}
.wrap{max-width:1200px;margin:0 auto;padding:0 16px 80px;}

/* TOP BAR */
.topbar{background:#fff;border-bottom:2px solid var(--border);padding:0 24px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);}
.tbi{display:flex;align-items:center;justify-content:space-between;height:64px;gap:12px;flex-wrap:wrap;}
.brand{font-size:18px;font-weight:900;letter-spacing:-0.5px;}
.brand span{color:#059669;}
.brand-sub{font-size:11px;color:var(--muted);font-weight:400;display:block;margin-top:-2px;}
.tbr{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.tbs{background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:6px 14px;text-align:center;}
.tbs-l{font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;font-weight:700;}
.tbs-v{font-size:14px;font-weight:800;margin-top:1px;}
.budget-input{width:80px;font-size:14px;font-weight:800;border:none;background:transparent;color:var(--ink);text-align:center;outline:none;}
.budget-input:focus{border-bottom:2px solid var(--green);}

/* MARKET PULSE */
.pulse{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;}
.pi{background:#fff;border:1px solid var(--border);border-radius:14px;padding:14px 18px;flex:1;min-width:130px;}
.pi-l{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;}
.pi-v{font-size:22px;font-weight:800;margin-bottom:2px;}
.pi-c{font-size:12px;font-weight:600;}

/* REGIME BANNER */
.regime{border-radius:16px;padding:18px 24px;margin-bottom:20px;border:1px solid var(--border);}
.regime-label{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;}
.regime-val{font-size:22px;font-weight:800;margin-bottom:4px;}
.regime-sub{font-size:12px;color:var(--text);}

/* STATS ROW */
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-bottom:24px;}
.sb{background:#fff;border:1px solid var(--border);border-radius:14px;padding:16px 18px;}
.sb-l{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;}
.sb-v{font-size:22px;font-weight:800;}
.sb-s{font-size:11px;color:var(--muted);margin-top:3px;}

/* SECTION HEADER */
.sec-hdr{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:14px;}
.sec-t{font-size:22px;font-weight:800;}
.sec-s{font-size:12px;color:var(--muted);}

/* CARDS GRID */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px;margin-bottom:28px;}
.scard{background:#fff;border:1px solid var(--border);border-radius:20px;overflow:hidden;cursor:pointer;transition:box-shadow 0.2s,transform 0.1s;}
.scard:hover{box-shadow:0 6px 24px rgba(0,0,0,0.10);transform:translateY(-1px);}

/* CARD TOP */
.sc-top{padding:18px 20px 14px;display:flex;justify-content:space-between;align-items:flex-start;}
.sc-left{}
.sc-sym{font-size:30px;font-weight:900;letter-spacing:-1px;margin-bottom:2px;}
.sc-name{font-size:14px;font-weight:600;color:var(--text);}
.sc-sec{display:inline-block;font-size:10px;background:var(--card2);border:1px solid var(--border);border-radius:20px;padding:2px 10px;color:var(--muted);text-transform:uppercase;margin-top:4px;}
.sc-right{text-align:right;}
.verdict{font-size:11px;font-weight:900;padding:5px 16px;border-radius:20px;border:2px solid;text-transform:uppercase;margin-bottom:6px;display:inline-block;letter-spacing:0.5px;}
.sc-summary{font-size:12px;color:var(--text);margin-top:4px;max-width:140px;text-align:right;line-height:1.4;}

/* EXPAND */
.sc-expand{font-size:11px;color:var(--muted);text-align:center;padding:6px;border-top:1px solid var(--border2);background:var(--card2);letter-spacing:0.3px;}

/* CARD BODY */
.sc-body{display:none;}
.sc-body.open{display:block;}

/* PRICE SECTION */
.sc-price{padding:14px 20px;background:#FAFAF7;border-bottom:1px solid var(--border2);}
.price-val{font-size:28px;font-weight:800;margin-bottom:4px;}
.chg{display:inline-block;font-size:13px;font-weight:700;padding:3px 12px;border-radius:20px;margin-bottom:10px;}
.yr-range-label{font-size:11px;font-weight:700;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;}
.range-lbl{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-bottom:5px;}
.range-track{height:6px;background:linear-gradient(90deg,#FFF1F2,#FFFBEB,#F0FDF4);border-radius:3px;position:relative;border:1px solid var(--border);}
.range-pin{position:absolute;top:50%;transform:translateY(-50%);width:10px;height:14px;background:#1A1614;border-radius:3px;}

/* SCORE BADGE */
.score-section{padding:14px 20px;border-bottom:1px solid var(--border2);}
.score-badge{display:inline-block;font-size:11px;font-weight:800;padding:5px 14px;border-radius:20px;margin-bottom:8px;letter-spacing:0.5px;}
.score-num{font-size:13px;color:var(--muted);margin-bottom:10px;}
.score-bars{display:flex;flex-direction:column;gap:6px;}
.sbar{display:flex;align-items:center;gap:10px;font-size:12px;}
.sbar-l{width:100px;color:var(--text);font-weight:600;}
.sbar-t{flex:1;height:7px;background:var(--border);border-radius:3px;overflow:hidden;}
.sbar-f{height:100%;border-radius:3px;}
.sbar-v{width:36px;text-align:right;font-weight:700;font-size:11px;}

/* SAFETY CHECKS */
.checks{padding:14px 20px;border-bottom:1px solid var(--border2);}
.cl-t{font-size:11px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;}
.cli{margin-bottom:8px;}
.cli-q{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:2px;}
.cli-a{font-size:12px;color:var(--text);}

/* LEVELS */
.levels{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--border2);}
.lbox{background:#fff;padding:12px 16px;}
.lbox-l{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;}
.lbox-v{font-size:14px;font-weight:800;}
.lbox-sub{font-size:10px;color:var(--muted);margin-top:2px;}

/* ALLOCATION */
.alloc-section{padding:14px 20px;border-bottom:1px solid var(--border2);background:#F8FFF8;}
.alloc-title{font-size:12px;font-weight:800;color:#059669;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;}
.alloc-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.alloc-lbl{font-size:12px;font-weight:700;color:var(--ink);}
.alloc-inp{width:100px;font-size:16px;font-weight:800;border:2px solid var(--border);border-radius:10px;padding:7px 12px;background:#fff;color:var(--ink);outline:none;}
.alloc-inp:focus{border-color:var(--green);}
.alloc-shares{font-size:12px;color:var(--muted);}
.rr-panel{background:#fff;border:1.5px solid var(--border2);border-radius:12px;padding:12px 16px;margin-bottom:10px;}
.rr-title{font-size:11px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;}
.rr-row{display:flex;justify-content:space-between;align-items:center;font-size:13px;margin-bottom:5px;}
.rr-gain{color:#059669;font-weight:800;}
.rr-loss{color:#DC2626;font-weight:800;}
.rr-ratio{font-size:12px;font-weight:800;padding:3px 12px;border-radius:20px;border:2px solid #ccc;background:#f5f5f5;}
.rr-explain{font-size:12px;margin-top:8px;padding:8px 10px;border-radius:8px;display:none;line-height:1.5;}
.ask-axiom-btn{display:block;width:100%;background:#1D4ED8;color:#fff;border:none;border-radius:10px;padding:10px;font-size:13px;font-weight:800;cursor:pointer;text-align:center;letter-spacing:0.3px;}
.ask-axiom-btn:hover{background:#1e40af;}

/* AI COACH */
.sc-ai{padding:14px 20px;background:#F8FCFF;border-top:1px solid var(--border2);}
.ai-badge{display:inline-block;font-size:9px;font-weight:800;background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;border-radius:20px;padding:3px 10px;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;}
.ai-why{font-size:14px;color:var(--ink);line-height:1.7;margin-bottom:8px;font-weight:500;}
.ai-watch{font-size:13px;background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:8px 12px;border-left:3px solid #D97706;line-height:1.6;}

/* FOOTER */
.footer{text-align:center;font-size:11px;color:var(--muted);padding-top:20px;border-top:1px solid var(--border);margin-top:40px;line-height:2;}

/* REFRESH BUTTON */
.refresh-bar{display:flex;align-items:center;justify-content:space-between;background:#fff;border:1px solid var(--border);border-radius:12px;padding:10px 16px;margin-bottom:20px;font-size:12px;color:var(--muted);}
.refresh-btn{background:#059669;color:#fff;border:none;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:700;cursor:pointer;}
.refresh-btn:hover{background:#047857;}

/* CHAT */
.chat-btn{position:fixed;bottom:28px;right:28px;background:#1D4ED8;color:#fff;border:none;border-radius:50px;padding:14px 22px;font-size:15px;font-weight:800;cursor:pointer;box-shadow:0 4px 20px rgba(29,78,216,0.4);z-index:1000;}
.chat-btn:hover{background:#1e40af;}
.chat-box{position:fixed;bottom:90px;right:28px;width:380px;max-height:560px;background:#fff;border:1px solid var(--border);border-radius:20px;box-shadow:0 8px 40px rgba(0,0,0,0.15);display:none;flex-direction:column;z-index:1000;}
.chat-box.open{display:flex;}
.chat-hdr{padding:14px 18px;border-bottom:1px solid var(--border);font-weight:800;font-size:15px;display:flex;justify-content:space-between;align-items:center;background:#1D4ED8;color:#fff;border-radius:20px 20px 0 0;}
.chat-close{cursor:pointer;font-size:20px;opacity:0.8;}
.chat-msgs{flex:1;overflow-y:auto;padding:14px 16px;display:flex;flex-direction:column;gap:10px;}
.msg{padding:10px 14px;border-radius:14px;font-size:13px;line-height:1.6;max-width:92%;}
.msg.user{background:#1D4ED8;color:#fff;align-self:flex-end;border-radius:14px 14px 4px 14px;}
.msg.ai{background:#F1F5F9;color:#1A1614;align-self:flex-start;border-radius:14px 14px 14px 4px;}
.chat-suggestions{display:flex;flex-direction:column;gap:6px;padding:0 16px 10px;}
.chat-sug{background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;border-radius:20px;padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer;text-align:left;}
.chat-sug:hover{background:#DBEAFE;}
.chat-inp{display:flex;gap:8px;padding:12px 14px;border-top:1px solid var(--border);}
.chat-inp input{flex:1;border:1.5px solid var(--border);border-radius:10px;padding:9px 14px;font-size:13px;outline:none;}
.chat-inp input:focus{border-color:#1D4ED8;}
.chat-inp button{background:#1D4ED8;color:#fff;border:none;border-radius:10px;padding:9px 16px;font-weight:800;cursor:pointer;font-size:13px;}
"""


def build_card(p, config):
    sym     = p["symbol"]
    name    = p["name"]
    sector  = p["sector"]
    price   = p["price"]
    dp      = p["dp"]
    h52     = p.get("h52", price * 1.2)
    l52     = p.get("l52", price * 0.8)
    fs      = p["factor_score"]
    gr      = p["guardrails"]
    verdict = fs.verdict
    buy_lo  = p.get("buy_lo", price)
    buy_hi  = p.get("buy_hi", price)
    stop    = p.get("stop_loss", round(price * 0.92, 2))
    target  = p.get("target", round(price * 1.15, 2))
    ai_why  = p.get("ai_why", "")
    ai_watch= p.get("ai_watch", "")
    vc      = verdict_colors(verdict)
    rng     = h52 - l52
    pos52   = round((price - l52) / rng * 100, 1) if rng else 50
    wt = config.W_TECHNICAL
    wr = config.W_RISK
    wq = config.W_QUALITY
    wm = config.W_MACRO
    we = config.W_EVENT
    mas     = gr.mas
    badge_text, badge_color, badge_bg = score_badge(fs.total)
    sym_color = "#059669" if verdict == "BUY" else "#D97706" if verdict == "HOLD" else "#DC2626"
    card_id = "card-" + sym
    p2 = "{:.2f}".format

    # Card summary line
    if verdict == "BUY":
        summary = "System says buy now"
    else:
        summary = "Watch — not buying yet"

    parts = []
    parts.append("<div class='scard' id='" + card_id + "' onclick='toggleCard(\"" + card_id + "\")'>")

    # Top
    parts.append("<div class='sc-top'>")
    parts.append("<div class='sc-left'>")
    parts.append("<div class='sc-sym' style='color:" + sym_color + "'>" + sym + "</div>")
    parts.append("<div class='sc-name'>" + name + "</div>")
    parts.append("<div class='sc-sec'>" + sector + "</div>")
    parts.append("</div>")
    parts.append("<div class='sc-right'>")
    parts.append("<div class='verdict' style='background:" + vc["bg"] + ";color:" + vc["text"] + ";border-color:" + vc["border"] + "'>" + verdict + "</div>")
    parts.append("<div style='font-size:20px;font-weight:800;margin:4px 0'>$" + p2(price) + "</div>")
    parts.append("<div class='sc-summary'>" + summary + "</div>")
    parts.append("</div></div>")

    parts.append("<div class='sc-expand' id='expand-" + card_id + "'>▼ Tap to see full analysis</div>")
    parts.append("<div class='sc-body' id='body-" + card_id + "'>")

    # Price + year range
    parts.append("<div class='sc-price'>")
    parts.append("<div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>")
    parts.append("<div class='price-val'>$" + p2(price) + "</div>")
    parts.append("<div class='chg' style='background:" + quote_bg(dp) + ";color:" + quote_color(dp) + "'>" + "{:+.1f}".format(dp) + "% today</div>")
    parts.append("</div>")
    parts.append("<div class='yr-range-label'>Where it sits in its yearly range</div>")
    parts.append("<div class='range-lbl'><span>Yearly Low $" + p2(l52) + "</span><span>" + str(pos52) + "% of the way up</span><span>Yearly High $" + p2(h52) + "</span></div>")
    parts.append("<div class='range-track'><div class='range-pin' style='left:calc(" + str(pos52) + "% - 5px)'></div></div>")
    parts.append("</div>")

    # Score
    parts.append("<div class='score-section'>")
    parts.append("<div class='score-badge' style='background:" + badge_bg + ";color:" + badge_color + "'>" + badge_text + "</div>")
    parts.append("<div class='score-num'>Overall Score: <strong>" + str(fs.total) + " / 100</strong></div>")
    parts.append("<div class='score-bars'>")
    score_labels = [
        ("Price Momentum", fs.technical, wt),
        ("Risk Level", fs.risk, wr),
        ("Company Quality", fs.quality, wq),
        ("Market Conditions", fs.macro, wm),
        ("News & Events", fs.event, we)
    ]
    for label, val, mx in score_labels:
        pct = int(val / mx * 100) if mx else 0
        parts.append("<div class='sbar'><span class='sbar-l'>" + label + "</span><div class='sbar-t'><div class='sbar-f' style='width:" + str(pct) + "%;background:" + bar_color(val, mx) + "'></div></div><span class='sbar-v'>" + str(int(pct)) + "%</span></div>")
    parts.append("</div></div>")

    # Safety checks — plain English
    parts.append("<div class='checks'><div class='cl-t'>Safety Checks</div>")
    for raw_label, status, detail in [
        ("No-Chase Rule", gr.no_chase_status, gr.no_chase_detail),
        ("Trend Alignment", gr.trend_status, gr.trend_detail),
        ("52wk Position", gr.pos52_status, gr.pos52_detail)
    ]:
        q, a = check_plain(status, raw_label, detail)
        parts.append("<div class='cli'><div class='cli-q'>" + q + "</div><div class='cli-a'>" + a + "</div></div>")
    parts.append("</div>")

    # Key levels — plain English
    parts.append("<div class='levels'>")
    parts.append("<div class='lbox'><div class='lbox-l'>Good Entry Price</div><div class='lbox-v' style='color:#059669'>$" + p2(buy_lo) + " – $" + p2(buy_hi) + "</div><div class='lbox-sub'>Best price to buy</div></div>")
    parts.append("<div class='lbox'><div class='lbox-l'>Sell If It Drops To</div><div class='lbox-v' style='color:#DC2626'>$" + p2(stop) + "</div><div class='lbox-sub'>Protect yourself here</div></div>")
    parts.append("<div class='lbox'><div class='lbox-l'>Price Target</div><div class='lbox-v' style='color:#1D4ED8'>$" + p2(target) + "</div><div class='lbox-sub'>Where it could go</div></div>")
    parts.append("</div>")

    # Allocation + Risk/Reward
    parts.append("<div class='alloc-section' onclick='event.stopPropagation()'>")
    parts.append("<div class='alloc-title'>💵 How much do you want to invest?</div>")
    parts.append("<div class='alloc-row'>")
    parts.append("<input class='alloc-inp' id='alloc-inp-" + sym + "' type='number' min='0' placeholder='$0'")
    parts.append("  oninput='updateRR(\"" + sym + "\"," + str(price) + "," + str(stop) + "," + str(target) + ")' />")
    parts.append("<span class='alloc-shares' id='shares-" + sym + "'></span>")
    parts.append("</div>")
    parts.append("<div class='rr-panel'>")
    parts.append("<div class='rr-title'>Your Risk &amp; Reward</div>")
    parts.append("<div class='rr-row'><span>💰 You could make (if it hits target)</span><span class='rr-gain' id='rr-gain-" + sym + "'>enter amount</span></div>")
    parts.append("<div class='rr-row'><span>🛑 You could lose (if it hits sell point)</span><span class='rr-loss' id='rr-loss-" + sym + "'>enter amount</span></div>")
    parts.append("<div class='rr-row'><span>📊 For every $1 you risk, you could make</span><span class='rr-ratio' id='rr-ratio-" + sym + "'>-</span></div>")
    parts.append("<div class='rr-explain' id='rr-explain-" + sym + "'></div>")
    parts.append("</div>")
    parts.append("<button class='ask-axiom-btn' onclick='askAxiomAbout(\"" + sym + "\",\"" + verdict + "\"," + str(fs.total) + "," + str(price) + "," + str(stop) + "," + str(target) + ")'>💬 Ask AXIOM — should I put money in " + sym + "?</button>")
    parts.append("</div>")

    # AI Coach
    parts.append("<div class='sc-ai'>")
    parts.append("<div class='ai-badge'>🤖 AXIOM Coach says</div>")
    parts.append("<div class='ai-why'>" + ai_why + "</div>")
    parts.append("<div class='ai-watch'>⚠️ " + ai_watch + "</div>")
    parts.append("</div>")

    parts.append("</div></div>")
    return "\n".join(parts)


class DashboardGenerator:
    def __init__(self, config):
        self.config = config

    def generate(self, portfolio, pulse, budget):
        et       = pytz.timezone("US/Eastern")
        now      = datetime.now(et)
        date_str = now.strftime("%A, %B %d %Y")
        time_str = now.strftime("%I:%M %p ET")

        regime, regime_color = get_regime(pulse)
        fear   = pulse.get("fear_level", "NEUTRAL")
        fc     = fear_color(fear)
        quotes = pulse.get("quotes", {})
        spy    = quotes.get("SPY", {})
        qqq    = quotes.get("QQQ", {})
        uso    = quotes.get("USO", {})
        vixy   = quotes.get("VIXY", {})

        n_buy  = sum(1 for p in portfolio if p["factor_score"].verdict == "BUY")
        n_hold = sum(1 for p in portfolio if p["factor_score"].verdict == "HOLD")

        cards = "\n".join(build_card(p, self.config) for p in portfolio)
        p2 = "{:.2f}".format

        portfolio_json = "[" + ",".join(
            "{\"sym\":\"" + p["symbol"] + "\",\"verdict\":\"" + p["factor_score"].verdict +
            "\",\"score\":" + str(p["factor_score"].total) +
            ",\"price\":" + str(p["price"]) +
            ",\"stop\":" + str(p.get("stop_loss", 0)) +
            ",\"target\":" + str(p.get("target", 0)) + "}"
            for p in portfolio
        ) + "]"

        buy_stocks = [p["symbol"] for p in portfolio if p["factor_score"].verdict == "BUY"]
        buy_list = ", ".join(buy_stocks) if buy_stocks else "none today"

        parts = []
        parts.append("<!DOCTYPE html><html lang='en'><head>")
        parts.append("<meta charset='UTF-8'>")
        parts.append("<meta name='viewport' content='width=device-width,initial-scale=1.0'>")
        parts.append("<title>INVESTOR 101 - AXIOM US - " + date_str + "</title>")
        parts.append("<style>" + get_css() + "</style>")
        parts.append("</head><body>")

        # Top bar
        parts.append("<div class='topbar'><div class='tbi'>")
        parts.append("<div><div class='brand'>INVESTOR <span>101</span> · AXIOM</div><span class='brand-sub'>Your personal investing dashboard</span></div>")
        parts.append("<div class='tbr'>")
        parts.append("<div class='tbs'><div class='tbs-l'>My Budget</div><div class='tbs-v'>$<input class='budget-input' id='budgetInput' type='number' value='" + str(int(budget)) + "' oninput='recalcTotals()'/></div></div>")
        parts.append("<div class='tbs'><div class='tbs-l'>Invested</div><div class='tbs-v' id='investedVal'>$0.00</div></div>")
        parts.append("<div class='tbs'><div class='tbs-l'>Cash Left</div><div class='tbs-v' id='cashVal'>$" + str(int(budget)) + ".00</div></div>")
        parts.append("<div class='tbs'><div class='tbs-l'>Buy Signals</div><div class='tbs-v' style='color:#059669'>" + str(n_buy) + " stocks</div></div>")
        parts.append("<div style='font-size:11px;color:#9D9690;white-space:nowrap'>" + time_str + "</div>")
        parts.append("</div></div></div>")

        parts.append("<div class='wrap'>")

        # Refresh bar
        parts.append("<div class='refresh-bar'>")
        parts.append("<span>📡 Last updated: <strong>" + date_str + " at " + time_str + "</strong> — data updates automatically each day</span>")
        parts.append("</div>")

        # Market pulse
        parts.append("<div class='pulse'>")
        parts.append("<div class='pi'><div class='pi-l'>S&amp;P 500 (whole market)</div><div class='pi-v' style='color:" + quote_color(spy.get("dp",0)) + "'>$" + p2(spy.get("price",0)) + "</div><div class='pi-c' style='color:" + quote_color(spy.get("dp",0)) + "'>" + "{:+.1f}%".format(spy.get("dp",0)) + " today</div></div>")
        parts.append("<div class='pi'><div class='pi-l'>Nasdaq (tech stocks)</div><div class='pi-v' style='color:" + quote_color(qqq.get("dp",0)) + "'>$" + p2(qqq.get("price",0)) + "</div><div class='pi-c' style='color:" + quote_color(qqq.get("dp",0)) + "'>" + "{:+.1f}%".format(qqq.get("dp",0)) + " today</div></div>")
        parts.append("<div class='pi'><div class='pi-l'>Oil prices</div><div class='pi-v'>$" + p2(uso.get("price",0)) + "</div><div class='pi-c'>" + "{:+.1f}%".format(uso.get("dp",0)) + " today</div></div>")
        parts.append("<div class='pi'><div class='pi-l'>Market Fear Level</div><div class='pi-v' style='color:" + fc + "'>$" + p2(vixy.get("price",0)) + "</div><div class='pi-c' style='color:" + fc + "'>" + fear + "</div></div>")
        parts.append("</div>")

        # Regime
        regime_bg = "#F0FDF4" if "BULL" in regime else "#FFFBEB" if "CAUTION" in regime or "MIXED" in regime else "#FFF1F2"
        parts.append("<div class='regime' style='background:" + regime_bg + ";border-color:" + regime_color + "'>")
        parts.append("<div class='regime-label'>Today's Market Conditions</div>")
        parts.append("<div class='regime-val' style='color:" + regime_color + "'>" + regime + "</div>")
        parts.append("<div class='regime-sub'>Today's buy signals: <strong>" + buy_list + "</strong></div>")
        parts.append("</div>")

        # Stats
        parts.append("<div class='stats'>")
        parts.append("<div class='sb'><div class='sb-l'>Stocks to Buy Now</div><div class='sb-v' style='color:#059669'>" + str(n_buy) + "</div><div class='sb-s'>system-verified signals</div></div>")
        parts.append("<div class='sb'><div class='sb-l'>Stocks to Watch</div><div class='sb-v' style='color:#D97706'>" + str(n_hold) + "</div><div class='sb-s'>not ready to buy yet</div></div>")
        parts.append("<div class='sb'><div class='sb-l'>You Have Invested</div><div class='sb-v' id='investedStat'>$0.00</div><div class='sb-s'>across " + str(len(portfolio)) + " stocks</div></div>")
        parts.append("<div class='sb'><div class='sb-l'>Cash Remaining</div><div class='sb-v' id='cashStat'>$" + str(int(budget)) + ".00</div><div class='sb-s'>available to deploy</div></div>")
        parts.append("</div>")

        parts.append("<div class='sec-hdr'>")
        parts.append("<div class='sec-t'>Today's Stock Analysis</div>")
        parts.append("<div class='sec-s'>Tap any card to see full details &amp; enter your investment amount</div>")
        parts.append("</div>")
        parts.append("<div class='grid'>" + cards + "</div>")

        parts.append("<div class='footer'>INVESTOR 101 · AXIOM US · Auto-updated " + date_str + " at " + time_str + "<br>For learning purposes only — not financial advice — all investing involves risk<br>Data: Finnhub / yfinance &nbsp;|&nbsp; AI Coach: Groq &nbsp;|&nbsp; Decisions: Rules-based model</div>")
        parts.append("</div>")

        # Chat
        parts.append("<button class='chat-btn' onclick='toggleChat()'>💬 Ask AXIOM</button>")
        parts.append("<div class='chat-box' id='chatBox'>")
        parts.append("<div class='chat-hdr'><span>💬 AXIOM Coach</span><span class='chat-close' onclick='toggleChat()'>✕</span></div>")
        parts.append("<div class='chat-msgs' id='chatMsgs'><div class='msg ai'>Hi! I know your full portfolio. Ask me anything — or tap one of the quick questions below 👇</div></div>")
        parts.append("<div class='chat-suggestions' id='chatSuggestions'>")
        parts.append("<button class='chat-sug' onclick='askSuggestion(this)'>What should I buy today?</button>")
        parts.append("<button class='chat-sug' onclick='askSuggestion(this)'>How do I split my budget across these stocks?</button>")
        parts.append("<button class='chat-sug' onclick='askSuggestion(this)'>Explain what stop loss means in simple terms</button>")
        parts.append("</div>")
        parts.append("<div class='chat-inp'><input id='chatIn' type='text' placeholder='Ask anything...' onkeydown='if(event.key==\"Enter\")sendMsg()'/><button onclick='sendMsg()'>Send</button></div>")
        parts.append("</div>")

        parts.append("<script>")
        parts.append("const PORTFOLIO = " + portfolio_json + ";")
        parts.append("const BUDGET_DEFAULT = " + str(int(budget)) + ";")
        parts.append("const FEAR = '" + fear + "';")
        parts.append(r"""
function fmt(n){ return '$'+parseFloat(n).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,','); }

function toggleCard(id){
    const body = document.getElementById('body-'+id);
    const lbl  = document.getElementById('expand-'+id);
    if(!body) return;
    body.classList.toggle('open');
    lbl.textContent = body.classList.contains('open') ? '\u25b2 Tap to collapse' : '\u25bc Tap to see full analysis';
}

function getUserAlloc(sym){
    const inp = document.getElementById('alloc-inp-'+sym);
    return inp ? (parseFloat(inp.value)||0) : 0;
}

function recalcTotals(){
    let total = 0;
    PORTFOLIO.forEach(p => { total += getUserAlloc(p.sym); });
    const budget = parseFloat(document.getElementById('budgetInput').value)||BUDGET_DEFAULT;
    const cash = budget - total;
    document.getElementById('investedVal').textContent = fmt(total);
    document.getElementById('investedStat').textContent = fmt(total);
    document.getElementById('cashVal').textContent = fmt(cash < 0 ? 0 : cash);
    document.getElementById('cashStat').textContent = fmt(cash < 0 ? 0 : cash);
}

function updateRR(sym, price, stop, target){
    const alloc = getUserAlloc(sym);
    const sharesEl  = document.getElementById('shares-'+sym);
    const gainEl    = document.getElementById('rr-gain-'+sym);
    const lossEl    = document.getElementById('rr-loss-'+sym);
    const ratioEl   = document.getElementById('rr-ratio-'+sym);
    const explainEl = document.getElementById('rr-explain-'+sym);
    if(alloc <= 0){
        if(sharesEl) sharesEl.textContent = '';
        if(gainEl) gainEl.textContent = 'enter amount';
        if(lossEl) lossEl.textContent = 'enter amount';
        if(ratioEl) ratioEl.textContent = '-';
        if(explainEl) explainEl.style.display='none';
        recalcTotals(); return;
    }
    const shares = alloc / price;
    if(sharesEl) sharesEl.textContent = '= ' + shares.toFixed(3) + ' shares';
    const gain = (target - price) * shares;
    const loss = (price - stop) * shares;
    if(gainEl) gainEl.textContent = '+' + fmt(gain);
    if(lossEl) lossEl.textContent = '-' + fmt(loss);
    const ratio = loss > 0 ? gain/loss : 0;
    if(ratioEl) ratioEl.textContent = '$' + ratio.toFixed(2);
    if(explainEl){
        explainEl.style.display = 'block';
        if(ratio >= 2){
            ratioEl.style.cssText='background:#F0FDF4;color:#059669;border-color:#059669;font-size:12px;font-weight:800;padding:3px 12px;border-radius:20px;border:2px solid;';
            explainEl.style.cssText='display:block;font-size:12px;margin-top:8px;padding:8px 10px;border-radius:8px;background:#F0FDF4;color:#059669;line-height:1.5;';
            explainEl.textContent='\u2705 Great setup \u2014 for every $1 you risk, you could gain $'+ratio.toFixed(2)+'. This is a favorable trade.';
        } else if(ratio >= 1){
            ratioEl.style.cssText='background:#FFFBEB;color:#D97706;border-color:#D97706;font-size:12px;font-weight:800;padding:3px 12px;border-radius:20px;border:2px solid;';
            explainEl.style.cssText='display:block;font-size:12px;margin-top:8px;padding:8px 10px;border-radius:8px;background:#FFFBEB;color:#D97706;line-height:1.5;';
            explainEl.textContent='\u26a0\ufe0f Fair setup \u2014 for every $1 you risk, you could gain $'+ratio.toFixed(2)+'. Proceed carefully and keep the amount small.';
        } else {
            ratioEl.style.cssText='background:#FFF1F2;color:#DC2626;border-color:#DC2626;font-size:12px;font-weight:800;padding:3px 12px;border-radius:20px;border:2px solid;';
            explainEl.style.cssText='display:block;font-size:12px;margin-top:8px;padding:8px 10px;border-radius:8px;background:#FFF1F2;color:#DC2626;line-height:1.5;';
            explainEl.textContent='\u274c Risky setup \u2014 you could lose more than you gain. Consider investing less or waiting for the price to come down closer to the entry range.';
        }
    }
    recalcTotals();
}

function askAxiomAbout(sym, verdict, score, price, stop, target){
    const alloc = getUserAlloc(sym);
    const budget = parseFloat(document.getElementById('budgetInput').value)||BUDGET_DEFAULT;
    const q = 'I am thinking about ' + sym + ' — it has a ' + verdict + ' signal with a score of ' + score + '/100. '
        + 'Price is $' + price + ', I should sell to protect myself if it drops to $' + stop + ', and the target is $' + target + '. '
        + 'My total budget is $' + budget + '. '
        + (alloc > 0 ? 'I am thinking of putting in $' + alloc + '. Is this a good idea?' : 'How much should I put in?');
    document.getElementById('chatBox').classList.add('open');
    document.getElementById('chatIn').value = q;
    sendMsg();
}

function askSuggestion(btn){
    document.getElementById('chatIn').value = btn.textContent;
    document.getElementById('chatSuggestions').style.display = 'none';
    sendMsg();
}

window.onload = function(){ recalcTotals(); };
function toggleChat(){ document.getElementById('chatBox').classList.toggle('open'); }

async function sendMsg(){
    const inp = document.getElementById('chatIn');
    const msg = inp.value.trim();
    if(!msg) return;
    inp.value = '';
    addMsg(msg, 'user');
    addMsg('Thinking...', 'ai', 'thinking');
    const context = 'Stocks today: ' + PORTFOLIO.map(p =>
        p.sym + ' (' + p.verdict + ', score ' + p.score + '/100, price $' + p.price +
        ', sell-point $' + p.stop + ', target $' + p.target + ', user has $' + getUserAlloc(p.sym) + ' allocated)'
    ).join(' | ') + '. Market mood: ' + FEAR + '.';
    try {
        const r = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({messages:[
                {role:'system', content:'You are AXIOM Coach. You help a complete beginner investor make smart decisions. RULES: max 4 sentences, no jargon, no bullet points, talk like a smart helpful friend via text message. Use real dollar amounts. Never say "consult a financial advisor". Context: ' + context},
                {role:'user', content: msg}
            ]})
        });
        const data = await r.json();
        const reply = data.choices[0].message.content;
        document.getElementById('thinking')?.remove();
        addMsg(reply, 'ai');
    } catch(e) {
        document.getElementById('thinking')?.remove();
        addMsg('Chat unavailable right now. Try again in a moment.', 'ai');
    }
}

function addMsg(text, role, id){
    const box = document.getElementById('chatMsgs');
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    if(id) div.id = id;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}
""")
        parts.append("</script></body></html>")
        return "\n".join(parts)
