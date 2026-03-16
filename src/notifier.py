
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz


class Notifier:
    def __init__(self, config):
        self.config = config

    def send_digest(self, portfolio, pulse):
        if not self.config.EMAIL_SENDER or not self.config.EMAIL_PASSWORD:
            print("No email credentials - skipping digest")
            return
        receivers = [r.strip() for r in self.config.EMAIL_RECEIVERS.split(",") if r.strip()]
        if not receivers:
            receivers = [self.config.EMAIL_SENDER]

        et       = pytz.timezone("US/Eastern")
        now      = datetime.now(et)
        date_str = now.strftime("%A, %B %d %Y")
        n_buy    = sum(1 for p in portfolio if p["factor_score"].verdict == "BUY")
        subject  = "INVESTOR 101 - AXIOM US - " + date_str + " - " + str(n_buy) + " BUY signals"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = self.config.EMAIL_SENDER
        msg["To"]      = ", ".join(receivers)
        msg.attach(MIMEText(self._text(portfolio, pulse, date_str), "plain"))
        msg.attach(MIMEText(self._html(portfolio, pulse, date_str), "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.config.EMAIL_SENDER, self.config.EMAIL_PASSWORD)
                server.sendmail(self.config.EMAIL_SENDER, receivers, msg.as_string())
            print("Email sent to " + ", ".join(receivers))
        except Exception as e:
            print("Email failed: " + str(e))

    def _text(self, portfolio, pulse, date_str):
        fear  = pulse.get("fear_level", "NEUTRAL")
        lines = ["INVESTOR 101 - AXIOM US - " + date_str, "Fear: " + fear, ""]
        for p in portfolio:
            fs = p["factor_score"]
            gr = p["guardrails"]
            lines.append(
                fs.verdict + "  " + p["symbol"] + "  $" + str(p["price"])
                + "  Score:" + str(fs.total)
                + "  Stop:$" + str(gr.stop_loss)
                + "  Target:$" + str(gr.target)
                + "  Alloc:" + str(p.get("alloc_pct", 0)) + "% $" + str(p.get("alloc_dollar", 0))
            )
            lines.append("  AI: " + p.get("ai_why", ""))
            lines.append("")
        lines.append("Educational purposes only. Not investment advice.")
        return "
".join(lines)

    def _html(self, portfolio, pulse, date_str):
        fear  = pulse.get("fear_level", "NEUTRAL")
        n_buy  = sum(1 for p in portfolio if p["factor_score"].verdict == "BUY")
        n_hold = sum(1 for p in portfolio if p["factor_score"].verdict == "HOLD")

        rows = ""
        for p in portfolio:
            fs = p["factor_score"]
            gr = p["guardrails"]
            vc = {"BUY": "#059669", "HOLD": "#D97706", "PASS": "#DC2626"}.get(fs.verdict, "#57534E")
            rows += "<tr style='border-bottom:1px solid #E2DDD4'>"
            rows += "<td style='padding:14px 12px;vertical-align:top'>"
            rows += "<div style='font-size:22px;font-weight:800;color:" + vc + "'>" + p["symbol"] + "</div>"
            rows += "<div style='font-size:11px;color:#9D9690'>" + p["sector"] + "</div>"
            rows += "<div style='margin-top:6px;display:inline-block;background:#F0FDF4;color:" + vc + ";border:1.5px solid " + vc + ";border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800'>" + fs.verdict + "</div>"
            rows += "</td>"
            rows += "<td style='padding:14px 12px;vertical-align:top'>"
            rows += "<div style='font-size:18px;font-weight:700'>$" + str(p["price"]) + "</div>"
            rows += "<div style='font-size:12px;font-weight:700;margin:4px 0'>Score: " + str(fs.total) + "/100</div>"
            rows += "<div style='font-size:11px;color:#57534E'>Tech:" + str(fs.technical) + " Risk:" + str(fs.risk) + " Quality:" + str(fs.quality) + " Macro:" + str(fs.macro) + "</div>"
            rows += "<div style='margin-top:6px;font-size:12px;color:#57534E;background:#EFF6FF;border-left:3px solid #1D4ED8;padding:5px 8px'>" + p.get("ai_why", "") + "</div>"
            rows += "</td>"
            rows += "<td style='padding:14px 12px;vertical-align:top;text-align:right'>"
            rows += "<div style='font-size:11px;color:#9D9690'>Buy Range</div>"
            rows += "<div style='font-size:14px;font-weight:700;color:#059669'>$" + str(gr.buy_lo) + "-$" + str(gr.buy_hi) + "</div>"
            rows += "<div style='font-size:11px;color:#9D9690;margin-top:5px'>Stop Loss</div>"
            rows += "<div style='font-size:14px;font-weight:700;color:#DC2626'>$" + str(gr.stop_loss) + "</div>"
            rows += "<div style='font-size:11px;color:#9D9690;margin-top:5px'>Target</div>"
            rows += "<div style='font-size:14px;font-weight:700;color:#1D4ED8'>$" + str(gr.target) + "</div>"
            rows += "<div style='margin-top:8px;font-size:12px;font-weight:600'>" + str(p.get("alloc_pct", 0)) + "% - $" + str(p.get("alloc_dollar", 0)) + "</div>"
            rows += "</td></tr>"

        html = "<!DOCTYPE html><html><body style='margin:0;padding:0;background:#F5F0E8;font-family:sans-serif'>"
        html += "<div style='max-width:640px;margin:0 auto;padding:20px 12px'>"
        html += "<div style='background:#1A1614;border-radius:12px;padding:20px 24px;margin-bottom:16px;color:#fff'>"
        html += "<div style='font-size:22px;font-weight:800'>INVESTOR 101 - AXIOM US</div>"
        html += "<div style='font-size:13px;color:rgba(255,255,255,.6)'>" + date_str + "</div>"
        html += "<div style='margin-top:10px;display:flex;gap:20px;flex-wrap:wrap'>"
        html += "<div><div style='font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase'>Fear</div><div style='font-weight:700'>" + fear + "</div></div>"
        html += "<div><div style='font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase'>Buy</div><div style='font-weight:700;color:#059669'>" + str(n_buy) + "</div></div>"
        html += "<div><div style='font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase'>Hold</div><div style='font-weight:700;color:#D97706'>" + str(n_hold) + "</div></div>"
        html += "</div></div>"
        html += "<div style='background:#fff;border-radius:12px;overflow:hidden'>"
        html += "<table style='width:100%;border-collapse:collapse'>" + rows + "</table>"
        html += "</div>"
        html += "<div style='margin-top:16px;font-size:11px;color:#9D9690;text-align:center'>Educational purposes only - Not investment advice</div>"
        html += "</div></body></html>"
        return html
