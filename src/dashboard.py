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
        "EXTREME FEAR": "#DC2626",
        "HIGH FEAR": "#DC2626",
        "ELEVATED": "#D97706",
        "NEUTRAL": "#57534E",
        "GREED": "#059669"
    }
    return m.get(fear, "#57534E")


def get_regime(pulse):
    fear = pulse.get("fear_level", "NEUTRAL")
    spy = pulse.get("spy_dp", 0)
    if fear in ("EXTREME FEAR", "HIGH FEAR"):
        return "RISK-OFF", "#DC2626"
    if fear == "GREED" and spy > 0:
        return "BULL MARKET", "#059669"
    if spy < -1:
        return "CAUTION", "#D97706"
    return "NEUTRAL / MIXED", "#D97706"


def bar_color(val, mx):
    p = val / mx if mx else 0
    if p > 0.7:
        return "#059669"
    if p > 0.4:
        return "#D97706"
    return "#DC2626"


def quote_color(dp):
    if dp >= 0:
        return "#059669"
    return "#DC2626"


def quote_bg(dp):
    if dp >= 0:
        return "#F0FDF4"
    return "#FFF1F2"


def ma_val(mas, key):
    v = mas.get(key)
    if v:
        return "$" + "{:.2f}".format(v)
    return "-"


def check_icon(status):
    m = {"ok": "✅", "warn": "⚠️", "block": "🚫", "warning": "⚠️"}
    return m.get(status, "⚠️")


def get_css():
    lines = [
        ":root{",
        "--page:#F5F0E8;--card:#fff;--card2:#FAFAF7;--border:#E2DDD4;--border2:#EDE9E0;",
        "--ink:#1A1614;--text:#57534E;--muted:#9D9690;",
        "--green:#059669;--green-bg:#F0FDF4;--red:#DC2626;--red-bg:#FFF1F2;",
        "--orange:#D97706;--orange-bg:#FFFBEB;--blue:#1D4ED8;--blue-bg:#EFF6FF;",
        "}",
        "*{margin:0;padding:0;box-sizing:border-box;}",
        "body{background:var(--page);color:var(--ink);font-family:system-ui,sans-serif;font-size:14px;line-height:1.6;}",
        ".wrap{max-width:1200px;margin:0 auto;padding:0 16px 60px;}",
        ".topbar{background:var(--card);border-bottom:1px solid var(--border);padding:0 20px;margin-bottom:20px;}",
        ".tbi{display:flex;align-items:center;justify-content:space-between;height:58px;gap:12px;flex-wrap:wrap;}",
        ".brand{font-size:17px;font-weight:800;}",
        ".brand span{color:#059669;}",
        ".tbr{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}",
        ".tbs{background:var(--card2);border:1px solid var(--border);border-radius:7px;padding:4px 10px;}",
        ".tbs-l{font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;}",
        ".tbs-v{font-size:13px;font-weight:700;}",
        ".budget-input{width:80px;font-size:13px;font-weight:700;border:none;background:transparent;color:var(--ink);text-align:center;outline:none;}",
        ".budget-input:focus{border-bottom:2px solid var(--green);}",
        ".pulse{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;}",
        ".pi{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px;flex:1;min-width:120px;}",
        ".pi-l{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:3px;}",
        ".pi-v{font-size:20px;font-weight:700;margin-bottom:2px;}",
        ".pi-c{font-size:11px;font-weight:600;}",
        ".regime{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px 24px;margin-bottom:16px;}",
        ".stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:20px;}",
        ".sb{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;}",
        ".sb-l{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:6px;}",
        ".sb-v{font-size:20px;font-weight:700;}",
        ".sb-s{font-size:11px;color:var(--muted);margin-top:2px;}",
        ".sec-hdr{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px;}",
        ".sec-t{font-size:20px;font-weight:700;}",
        ".sec-s{font-size:12px;color:var(--muted);}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(370px,1fr));gap:12px;margin-bottom:24px;}",
        ".scard{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;border-top:3px solid #1A1614;cursor:pointer;transition:box-shadow 0.2s;}",
        ".scard:hover{box-shadow:0 4px 20px rgba(0,0,0,0.10);}",
        ".sc-top{padding:16px 18px 12px;display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1px solid var(--border2);}",
        ".sc-sym{font-size:28px;font-weight:800;letter-spacing:-1px;}",
        ".sc-name{font-size:13px;font-weight:600;margin-bottom:2px;}",
        ".sc-sec{display:inline-block;font-size:10px;background:var(--card2);border:1px solid var(--border);border-radius:20px;padding:2px 9px;color:var(--muted);text-transform:uppercase;}",
        ".sc-right{text-align:right;}",
        ".verdict{font-size:12px;font-weight:800;padding:5px 14px;border-radius:20px;border:1.5px solid;text-transform:uppercase;margin-bottom:8px;display:inline-block;}",
        ".sc-dollar{font-size:22px;font-weight:700;}",
        ".sc-pct{font-size:11px;color:var(--muted);}",
        ".sc-expand{font-size:10px;color:var(--muted);text-align:center;padding:4px;border-top:1px solid var(--border2);background:var(--card2);}",
        ".sc-body{display:none;}",
        ".sc-body.open{display:block;}",
        ".sc-price{padding:12px 18px;background:#FAFAF7;border-bottom:1px solid var(--border2);}",
        ".price-val{font-size:20px;font-weight:700;margin-bottom:4px;}",
        ".chg{display:inline-block;font-size:12px;font-weight:700;padding:2px 10px;border-radius:20px;margin-bottom:8px;}",
        ".range-lbl{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-bottom:4px;}",
        ".range-track{height:5px;background:linear-gradient(90deg,#FFF1F2,#FFFBEB,#F0FDF4);border-radius:3px;position:relative;border:1px solid var(--border);}",
        ".range-pin{position:absolute;top:50%;transform:translateY(-50%);width:8px;height:12px;background:#1A1614;border-radius:2px;}",
        ".trace{padding:12px 18px;border-bottom:1px solid var(--border2);}",
        ".trace-t{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:8px;}",
        ".score-bars{display:flex;flex-direction:column;gap:5px;}",
        ".sbar{display:flex;align-items:center;gap:8px;font-size:11px;}",
        ".sbar-l{width:70px;color:var(--text);font-weight:600;}",
        ".sbar-t{flex:1;height:6px;background:var(--border);border-radius:3px;overflow:hidden;}",
        ".sbar-f{height:100%;border-radius:3px;}",
        ".sbar-v{width:32px;text-align:right;font-weight:700;}",
        ".checks{padding:12px 18px;border-bottom:1px solid var(--border2);}",
        ".cl-t{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:8px;}",
        ".cli{display:flex;align-items:flex-start;gap:8px;margin-bottom:5px;font-size:12px;}",
        ".cli-name{font-weight:700;min-width:110px;}",
        ".cli-detail{color:var(--text);}",
        ".levels{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--border2);}",
        ".lbox{background:var(--card);padding:10px 14px;}",
        ".lbox-l{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;margin-bottom:3px;}",
        ".lbox-v{font-size:15px;font-weight:700;}",
        ".sc-ai{padding:12px 18px;border-top:1px solid var(--border2);background:#FAFDF7;}",
        ".ai-badge{display:inline-block;font-size:9px;font-weight:700;background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;border-radius:20px;padding:2px 8px;margin-bottom:6px;text-transform:uppercase;}",
        ".ai-why{font-size:13px;color:var(--text);line-height:1.7;margin-bottom:6px;}",
        ".ai-watch{font-size:12px;background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;padding:6px 10px;border-left:3px solid #D97706;}",
        ".sc-mas{display:flex;gap:12px;padding:8px 18px;background:var(--card2);border-top:1px solid var(--border2);}",
        ".ma{font-size:11px;color:var(--muted);}",
        ".footer{text-align:center;font-size:11px;color:var(--muted);padding-top:20px;border-top:1px solid var(--border);margin-top:40px;line-height:1.8;}",
        ".chat-btn{position:fixed;bottom:28px;right:28px;background:#059669;color:#fff;border:none;border-radius:50px;padding:14px 22px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(5,150,105,0.4);z-index:1000;}",
        ".chat-btn:hover{background:#047857;}",
        ".chat-box{position:fixed;bottom:90px;right:28px;width:370px;max-height:520px;background:#fff;border:1px solid var(--border);border-radius:20px;box-shadow:0 8px 40px rgba(0,0,0,0.15);display:none;flex-direction:column;z-index:1000;}",
        ".chat-box.open{display:flex;}",
        ".chat-hdr{padding:14px 18px;border-bottom:1px solid var(--border);font-weight:700;font-size:14px;display:flex;justify-content:space-between;align-items:center;}",
        ".chat-close{cursor:pointer;color:var(--muted);font-size:18px;}",
        ".chat-msgs{flex:1;overflow-y:auto;padding:14px 18px;display:flex;flex-direction:column;gap:10px;}",
        ".msg{padding:8px 12px;border-radius:12px;font-size:13px;line-height:1.6;max-width:90%;}",
        ".msg.user{background:#059669;color:#fff;align-self:flex-end;}",
        ".msg.ai{background:var(--card2);border:1px solid var(--border);align-self:flex-start;}",
        ".chat-inp{display:flex;gap:8px;padding:12px 14px;border-top:1px solid var(--border);}",
        ".chat-inp input{flex:1;border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:13px;outline:none;}",
        ".chat-inp button{background:#059669;color:#fff;border:none;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;}",
    ]
    return "\n".join(lines)


def build_card(p, config):
    sym      = p["symbol"]
    name     = p["name"]
    sector   = p["sector"]
    price    = p["price"]
    dp       = p["dp"]
    h52      = p.get("h52", price * 1.2)
    l52      = p.get("l52", price * 0.8)
    fs       = p["factor_score"]
    gr       = p["guardrails"]
    verdict  = fs.verdict
    alloc_d  = p.get("alloc_dollar", 0)
    alloc_p  = p.get("alloc_pct", 0)
    buy_lo   = p.get("buy_lo", price)
    buy_hi   = p.get("buy_hi", price)
    stop     = p.get("stop_loss", round(price * 0.92, 2))
    target   = p.get("target", round(price * 1.15, 2))
    ai_why   = p.get("ai_why", "")
    ai_watch = p.get("ai_watch", "")
    vc       = verdict_colors(verdict)
    rng      = h52 - l52
    pos52    = round((price - l52) / rng * 100, 1) if rng else 50
    wt = config.W_TECHNICAL
    wr = config.W_RISK
    wq = config.W_QUALITY
    wm = config.W_MACRO
    we = config.W_EVENT
    mas = gr.mas

    sym_color = "#059669" if verdict == "BUY" else "#D97706" if verdict == "HOLD" else "#DC2626"
    card_id = "card-" + sym

    parts = []
    parts.append("<div class='scard' id='" + card_id + "' onclick='toggleCard(\"" + card_id + "\")'>")

    # Always visible top
    parts.append("<div class='sc-top'>")
    parts.append("<div>")
    parts.append("<div class='sc-sym' style='color:" + sym_color + "'>" + sym + "</div>")
    parts.append("<div class='sc-name'>" + name + "</div>")
    parts.append("<div class='sc-sec'>" + sector + "</div>")
    parts.append("</div>")
    parts.append("<div class='sc-right'>")
    parts.append("<div class='verdict' style='background:" + vc["bg"] + ";color:" + vc["text"] + ";border-color:" + vc["border"] + "'>" + verdict + "</div>")
    parts.append("<div class='sc-dollar alloc-val' data-pct='" + str(alloc_p) + "'>" + fmt_dollar(alloc_d) + "</div>")
    parts.append("<div class='sc-pct'>" + str(alloc_p) + "% of budget</div>")
    parts.append("</div></div>")

    parts.append("<div class='sc-expand' id='expand-" + card_id + "'>▼ Click to expand</div>")

    # Collapsible body
    parts.append("<div class='sc-body' id='body-" + card_id + "'>")

    parts.append("<div class='sc-price'>")
    parts.append("<div class='price-val'>$" + "{:.2f}".format(price) + "</div>")
    parts.append("<div class='chg' style='background:" + quote_bg(dp) + ";color:" + quote_color(dp) + "'>" + "{:+.1f}".format(dp) + "% today</div>")
    parts.append("<div class='range-lbl'>")
    parts.append("<span>52wk low $" + "{:.2f}".format(l52) + "</span>")
    parts.append("<span>" + str(pos52) + "% up</span>")
    parts.append("<span>$" + "{:.2f}".format(h52) + " high</span>")
    parts.append("</div>")
    parts.append("<div class='range-track'>")
    parts.append("<div class='range-pin' style='left:calc(" + str(pos52) + "% - 4px)'></div>")
    parts.append("</div></div>")

    parts.append("<div class='trace'>")
    parts.append("<div class='trace-t'>Measured Signals - Score: " + str(fs.total) + " / 100</div>")
    parts.append("<div class='score-bars'>")
    for label, val, mx in [("Technical", fs.technical, wt), ("Risk", fs.risk, wr), ("Quality", fs.quality, wq), ("Macro", fs.macro, wm), ("Event", fs.event, we)]:
        pct = int(val / mx * 100) if mx else 0
        parts.append("<div class='sbar'>")
        parts.append("<span class='sbar-l'>" + label + "</span>")
        parts.append("<div class='sbar-t'><div class='sbar-f' style='width:" + str(pct) + "%;background:" + bar_color(val, mx) + "'></div></div>")
        parts.append("<span class='sbar-v'>" + str(val) + "/" + str(mx) + "</span>")
        parts.append("</div>")
    parts.append("</div></div>")

    parts.append("<div class='checks'>")
    parts.append("<div class='cl-t'>Guardrail Checks</div>")
    for label, status, detail in [
        ("No-Chase Rule", gr.no_chase_status, gr.no_chase_detail),
        ("Trend Alignment", gr.trend_status, gr.trend_detail),
        ("52wk Position", gr.pos52_status, gr.pos52_detail)
    ]:
        parts.append("<div class='cli'>")
        parts.append("<span style='font-weight:700;min-width:30px'>" + check_icon(status) + "</span>")
        parts.append("<span class='cli-name'>" + label + "</span>")
        parts.append("<span class='cli-detail'>" + detail + "</span>")
        parts.append("</div>")
    parts.append("</div>")

    parts.append("<div class='levels'>")
    parts.append("<div class='lbox'><div class='lbox-l'>Buy Range</div><div class='lbox-v' style='color:#059669'>$" + "{:.2f}".format(buy_lo) + "-$" + "{:.2f}".format(buy_hi) + "</div></div>")
    parts.append("<div class='lbox'><div class='lbox-l'>Stop Loss</div><div class='lbox-v' style='color:#DC2626'>$" + "{:.2f}".format(stop) + "</div></div>")
    parts.append("<div class='lbox'><div class='lbox-l'>Target</div><div class='lbox-v' style='color:#1D4ED8'>$" + "{:.2f}".format(target) + "</div></div>")
    parts.append("</div>")

    parts.append("<div class='sc-ai'>")
    parts.append("<div class='ai-badge'>AI Coach - not the decision engine</div>")
    parts.append("<div class='ai-why'>" + ai_why + "</div>")
    parts.append("<div class='ai-watch'>Watch: " + ai_watch + "</div>")
    parts.append("</div>")

    parts.append("<div class='sc-mas'>")
    parts.append("<span class='ma'>MA5 <strong>" + ma_val(mas, "ma5") + "</strong></span>")
    parts.append("<span class='ma'>MA10 <strong>" + ma_val(mas, "ma10") + "</strong></span>")
    parts.append("<span class='ma'>MA20 <strong>" + ma_val(mas, "ma20") + "</strong></span>")
    parts.append("</div>")

    parts.append("</div>")  # end sc-body
    parts.append("</div>")  # end scard
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
        fear    = pulse.get("fear_level", "NEUTRAL")
        fc      = fear_color(fear)
        quotes  = pulse.get("quotes", {})
        spy     = quotes.get("SPY", {})
        qqq     = quotes.get("QQQ", {})
        uso     = quotes.get("USO", {})
        vixy    = quotes.get("VIXY", {})

        n_buy    = sum(1 for p in portfolio if p["factor_score"].verdict == "BUY")
        n_hold   = sum(1 for p in portfolio if p["factor_score"].verdict == "HOLD")
        invested = sum(p.get("alloc_dollar", 0) for p in portfolio)
        cash     = round(budget * self.config.CASH_RESERVE)

        cards = "\n".join(build_card(p, self.config) for p in portfolio)

        spy_price  = "${:.2f}".format(spy.get("price", 0))
        spy_dp     = "{:+.1f}%".format(spy.get("dp", 0))
        qqq_price  = "${:.2f}".format(qqq.get("price", 0))
        qqq_dp     = "{:+.1f}%".format(qqq.get("dp", 0))
        uso_price  = "${:.2f}".format(uso.get("price", 0))
        uso_dp     = "{:+.1f}%".format(uso.get("dp", 0))
        vixy_price = "${:.2f}".format(vixy.get("price", 0))

        portfolio_json = "[" + ",".join(
            "{\"sym\":\"" + p["symbol"] + "\",\"verdict\":\"" + p["factor_score"].verdict +
            "\",\"score\":" + str(p["factor_score"].total) +
            ",\"price\":" + str(p["price"]) +
            ",\"stop\":" + str(p.get("stop_loss", 0)) +
            ",\"target\":" + str(p.get("target", 0)) +
            ",\"alloc\":" + str(p.get("alloc_dollar", 0)) + "}"
            for p in portfolio
        ) + "]"

        parts = []
        parts.append("<!DOCTYPE html><html lang='en'><head>")
        parts.append("<meta charset='UTF-8'>")
        parts.append("<meta name='viewport' content='width=device-width,initial-scale=1.0'>")
        parts.append("<title>INVESTOR 101 - AXIOM US - " + date_str + "</title>")
        parts.append("<style>" + get_css() + "</style>")
        parts.append("</head><body>")

        parts.append("<div class='topbar'><div class='tbi'>")
        parts.append("<div class='brand'>INVESTOR <span>101</span> - AXIOM US</div>")
        parts.append("<div class='tbr'>")
        parts.append("<div class='tbs'><div class='tbs-l'>Budget</div><div class='tbs-v'>$<input class='budget-input' id='budgetInput' type='number' value='" + str(int(budget)) + "' onchange='updateBudget(this.value)'/></div></div>")
        parts.append("<div class='tbs'><div class='tbs-l'>Invested</div><div class='tbs-v' id='investedVal'>" + fmt_dollar(invested) + "</div></div>")
        parts.append("<div class='tbs'><div class='tbs-l'>Cash</div><div class='tbs-v' id='cashVal'>" + fmt_dollar(cash) + "</div></div>")
        parts.append("<div class='tbs'><div class='tbs-l'>Signals</div><div class='tbs-v'>" + str(n_buy) + " BUY / " + str(n_hold) + " HOLD</div></div>")
        parts.append("<div style='font-size:11px;color:#9D9690'>" + date_str + " - " + time_str + "</div>")
        parts.append("</div></div></div>")

        parts.append("<div class='wrap'>")

        parts.append("<div class='pulse'>")
        parts.append("<div class='pi'><div class='pi-l'>S&amp;P 500 - SPY</div><div class='pi-v' style='color:" + quote_color(spy.get("dp", 0)) + "'>" + spy_price + "</div><div class='pi-c' style='color:" + quote_color(spy.get("dp", 0)) + "'>" + spy_dp + " today</div></div>")
        parts.append("<div class='pi'><div class='pi-l'>Nasdaq - QQQ</div><div class='pi-v' style='color:" + quote_color(qqq.get("dp", 0)) + "'>" + qqq_price + "</div><div class='pi-c' style='color:" + quote_color(qqq.get("dp", 0)) + "'>" + qqq_dp + " today</div></div>")
        parts.append("<div class='pi'><div class='pi-l'>Oil - USO</div><div class='pi-v'>" + uso_price + "</div><div class='pi-c'>" + uso_dp + " today</div></div>")
        parts.append("<div class='pi'><div class='pi-l'>Fear Index - VIXY</div><div class='pi-v' style='color:" + fc + "'>" + vixy_price + "</div><div class='pi-c' style='color:" + fc + "'>" + fear + "</div></div>")
        parts.append("</div>")

        parts.append("<div class='regime'>")
        parts.append("<div style='font-size:10px;font-weight:700;color:#9D9690;text-transform:uppercase;margin-bottom:4px'>Market Regime - Rules-Based Signal</div>")
        parts.append("<div style='font-size:24px;font-weight:700;color:" + regime_color + "'>" + regime + "</div>")
        parts.append("<div style='font-size:13px;color:#57534E;margin-top:6px'>Determined by SPY momentum, VIXY fear gauge, and USO energy signal. Not AI-generated.</div>")
        parts.append("</div>")

        parts.append("<div class='stats'>")
        parts.append("<div class='sb'><div class='sb-l'>Buy Signals</div><div class='sb-v' style='color:#059669'>" + str(n_buy) + "</div><div class='sb-s'>rules-verified</div></div>")
        parts.append("<div class='sb'><div class='sb-l'>Hold</div><div class='sb-v' style='color:#D97706'>" + str(n_hold) + "</div><div class='sb-s'>watch for entry</div></div>")
        parts.append("<div class='sb'><div class='sb-l'>Invested</div><div class='sb-v' id='investedStat'>" + fmt_dollar(invested) + "</div><div class='sb-s'>" + str(len(portfolio)) + " positions</div></div>")
        parts.append("<div class='sb'><div class='sb-l'>Cash Reserve</div><div class='sb-v' id='cashStat'>" + fmt_dollar(cash) + "</div><div class='sb-s'>" + str(int(self.config.CASH_RESERVE * 100)) + "% kept safe</div></div>")
        parts.append("</div>")

        parts.append("<div class='sec-hdr'>")
        parts.append("<div class='sec-t'>Today's Portfolio</div>")
        parts.append("<div class='sec-s'>Click any card to expand. Scores deterministic - AI for coaching only - Updated " + time_str + "</div>")
        parts.append("</div>")
        parts.append("<div class='grid'>" + cards + "</div>")

        parts.append("<div class='footer'>")
        parts.append("INVESTOR 101 - AXIOM US - Auto-generated " + date_str + " at " + time_str + " ET<br>")
        parts.append("For educational purposes only - Not investment advice - All investments carry risk<br>")
        parts.append("Data: Finnhub / yfinance | Commentary: Groq/Gemini | Decisions: Rules-based Python model")
        parts.append("</div>")

        parts.append("</div>")

        # Chat button + box
        parts.append("<button class='chat-btn' onclick='toggleChat()'>💬 Ask AXIOM</button>")
        parts.append("<div class='chat-box' id='chatBox'>")
        parts.append("<div class='chat-hdr'><span>💬 AXIOM Coach</span><span class='chat-close' onclick='toggleChat()'>✕</span></div>")
        parts.append("<div class='chat-msgs' id='chatMsgs'><div class='msg ai'>Hi! I know your full portfolio today. Ask me anything — what to buy, what a stop loss means, or how to grow your money.</div></div>")
        parts.append("<div class='chat-inp'><input id='chatIn' type='text' placeholder='Ask anything...' onkeydown='if(event.key==\"Enter\")sendMsg()'/><button onclick='sendMsg()'>Send</button></div>")
        parts.append("</div>")

        cash_reserve = self.config.CASH_RESERVE

        parts.append("""
<script>
const PORTFOLIO = """ + portfolio_json + """;
const BUDGET_DEFAULT = """ + str(int(budget)) + """;
const CASH_RESERVE = """ + str(cash_reserve) + """;
const INVESTED = """ + str(float(invested)) + """;

function fmt(n){ return '$'+parseFloat(n).toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g,','); }

function toggleCard(id){
    const body = document.getElementById('body-'+id);
    const lbl  = document.getElementById('expand-'+id);
    if(!body) return;
    body.classList.toggle('open');
    lbl.textContent = body.classList.contains('open') ? '▲ Click to collapse' : '▼ Click to expand';
}

function updateBudget(val){
    const b = parseFloat(val) || BUDGET_DEFAULT;
    localStorage.setItem('axiom_budget', b);
    document.getElementById('cashVal').textContent = fmt(b * CASH_RESERVE);
    document.getElementById('cashStat').textContent = fmt(b * CASH_RESERVE);
    document.querySelectorAll('.alloc-val').forEach(el => {
        const pct = parseFloat(el.dataset.pct) || 0;
        el.textContent = fmt(b * pct / 100);
    });
}

window.onload = function(){
    const saved = localStorage.getItem('axiom_budget');
    if(saved){ document.getElementById('budgetInput').value = saved; updateBudget(saved); }
};

function toggleChat(){
    document.getElementById('chatBox').classList.toggle('open');
}

async function sendMsg(){
    const inp = document.getElementById('chatIn');
    const msg = inp.value.trim();
    if(!msg) return;
    inp.value = '';
    addMsg(msg, 'user');
    addMsg('Thinking...', 'ai', 'thinking');

    const context = 'Portfolio today: ' + PORTFOLIO.map(p =>
        p.sym + ' ' + p.verdict + ' score=' + p.score + ' price=$' + p.price +
        ' stop=$' + p.stop + ' target=$' + p.target + ' alloc=$' + p.alloc
    ).join(', ') + '. Market fear: """ + fear + """.';

    try {
        const r = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({messages:[
                {role:'system', content:'You are AXIOM Coach, an expert investing teacher for a beginner investor. You have full context of their portfolio. Be direct, use dollar amounts, explain simply. Never say consult a financial advisor. Context: ' + context},
                {role:'user', content: msg}
            ]})
        });
        const data = await r.json();
        const reply = data.choices[0].message.content;
        document.getElementById('thinking')?.remove();
        addMsg(reply, 'ai');
    } catch(e) {
        document.getElementById('thinking')?.remove();
        addMsg('Chat unavailable - deploy to Vercel to enable live chat.', 'ai');
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
</script>
</body></html>""")

        return "\n".join(parts)
