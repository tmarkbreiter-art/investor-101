"""
AXIOM US — vNext Email Notifier
Rules outputs first. AI commentary second. Clearly labelled.
"""
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
            print("  No email credentials - skipping digest")
            return
        receivers = [r.strip() for r in self.config.EMAIL_RECEIVERS.split(",") if r.strip()]
        if not receivers: receivers = [self.config.EMAIL_SENDER]
        et  = pytz.timezone("US/Eastern")
        now = datetime.now(et)
        date_str = now.strftime("%A, %B %-d %Y")
        n_buy = sum(1 for p in portfolio if p["factor_score"].verdict == "BUY")
        subject = f"INVESTOR 101 - AXIOM US - {date_str} - {n_buy} BUY signals"
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
            print(f"  Email sent to {', '.join(receivers)}")
        except Exception as e:
            print(f"  Email failed: {e}")

    def _text(self, portfolio, pulse, date_str):
        fear = pulse.get("fear_level","NEUTRAL")
        lines = [f"INVESTOR 101 - AXIOM US - {date_str}", f"Fear: {fear}", ""]
        for p in portfolio:
            fs=p["factor_score"]; gr=p["guardrails"]
            lines.append(f"{fs.verdict:5s} {p['symbol']:6s} ${p['price']:.2f}  Score:{fs.total:.0f}  Stop:${gr.stop_loss:.2f}  Target:${gr.target:.2f}  Alloc:{p.get('alloc_pct',0):.1f}% ${p.get('alloc_dollar',0):.0f}")
            lines.append(f"       Rules: {' | '.join(fs.reasons[-3:])}")
            lines.append(f"       AI: {p.get('ai_why','')}")
            lines.append("")
        lines += ["Educational purposes only. Not investment advice."]
        return "
".join(lines)

    def _html(self, portfolio, pulse, date_str):
        fear=pulse.get("fear_level","NEUTRAL")
        fc={"EXTREME FEAR":"#DC2626","HIGH FEAR":"#DC2626","ELEVATED":"#D97706","NEUTRAL":"#57534E","GREED":"#059669"}.get(fear,"#57534E")
        n_buy=sum(1 for p in portfolio if p["factor_score"].verdict=="BUY")
        n_hold=sum(1 for p in portfolio if p["factor_score"].verdict=="HOLD")
        rows=""
        for p in portfolio:
            fs=p["factor_score"]; gr=p["guardrails"]
            vc={"BUY":"#059669","HOLD":"#D97706","PASS":"#DC2626"}.get(fs.verdict,"#57534E")
            rows+=f"""<tr style="border-bottom:1px solid #E2DDD4">
<td style="padding:14px 12px;vertical-align:top;min-width:80px">
  <div style="font-family:Georgia,serif;font-size:22px;font-weight:800;color:{vc}">{p['symbol']}</div>
  <div style="font-size:11px;color:#9D9690">{p['sector']}</div>
  <div style="margin-top:6px;display:inline-block;background:{'#F0FDF4' if fs.verdict=='BUY' else '#FFFBEB'};color:{vc};border:1.5px solid {vc};border-radius:20px;padding:2px 10px;font-size:11px;font-weight:800">{fs.verdict}</div>
</td>
<td style="padding:14px 12px;vertical-align:top">
  <div style="font-family:monospace;font-size:18px;font-weight:700">${p['price']:.2f}</div>
  <div style="font-size:12px;font-weight:700;color:#1A1614;margin:4px 0">Score: {fs.total:.0f}/100</div>
  <div style="font-size:11px;color:#57534E">Tech:{fs.technical:.0f} Risk:{fs.risk:.0f} Quality:{fs.quality:.0f} Macro:{fs.macro:.0f}</div>
  <div style="font-size:11px;color:#9D9690;margin-top:4px">{gr.no_chase_detail}</div>
  <div style="margin-top:6px;font-size:12px;color:#57534E;background:#EFF6FF;border-left:3px solid #1D4ED8;border-radius:4px;padding:5px 8px"><span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#1D4ED8">AI: </span>{p.get('ai_why','')}</div>
</td>
<td style="padding:14px 12px;vertical-align:top;text-align:right;min-width:120px">
  <div style="font-size:11px;color:#9D9690;text-transform:uppercase;letter-spacing:.5px">Buy Range</div>
  <div style="font-size:14px;font-weight:700;color:#059669;font-family:monospace">${gr.buy_lo:.2f}–${gr.buy_hi:.2f}</div>
  <div style="font-size:11px;color:#9D9690;margin-top:5px">Stop Loss</div>
  <div style="font-size:14px;font-weight:700;color:#DC2626;font-family:monospace">${gr.stop_loss:.2f}</div>
  <div style="font-size:11px;color:#9D9690;margin-top:5px">Target</div>
  <div style="font-size:14px;font-weight:700;color:#1D4ED8;font-family:monospace">${gr.target:.2f}</div>
  <div style="margin-top:8px;font-size:12px;font-weight:600;color:#57534E">{p.get('alloc_pct',0):.1f}% · ${p.get('alloc_dollar',0):.0f}</div>
</td></tr>"""
        return f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#F5F0E8;font-family:sans-serif">
<div style="max-width:640px;margin:0 auto;padding:20px 12px">
<div style="background:#1A1614;border-radius:12px;padding:20px 24px;margin-bottom:16px;color:#fff">
  <div style="font-family:Georgia,serif;font-size:22px;font-weight:800">INVESTOR <span style="color:#059669">101</span> · AXIOM US</div>
  <div style="font-size:13px;color:rgba(255,255,255,.6)">{date_str}</div>
  <div style="margin-top:10px;display:flex;gap:20px;flex-wrap:wrap">
    <div><div style="font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1px">Fear</div><div style="font-weight:700;color:{fc}">{fear}</div></div>
    <div><div style="font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1px">Buy</div><div style="font-weight:700;color:#059669">{n_buy}</div></div>
    <div><div style="font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1px">Hold</div><div style="font-weight:700;color:#D97706">{n_hold}</div></div>
  </div>
  <div style="margin-top:8px;font-size:11px;color:rgba(255,255,255,.5)">Decisions: rules-based Python model · AI: commentary only</div>
</div>
<div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)">
  <table style="width:100%;border-collapse:collapse">{rows}</table>
</div>
<div style="margin-top:16px;font-size:11px;color:#9D9690;text-align:center;line-height:1.8">
  Educational purposes only · Not investment advice · All investments carry risk
</div></div></body></html>"""
