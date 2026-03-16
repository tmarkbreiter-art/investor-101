import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz


class Notifier:
    def __init__(self, config):
        self.config = config

    def send(self, subject, html_body):
        cfg = self.config
        receivers = [r.strip() for r in cfg.EMAIL_RECEIVERS.split(",") if r.strip()]
        if not receivers:
            print("No EMAIL_RECEIVERS configured, skipping email.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg.EMAIL_SENDER
        msg["To"]      = ", ".join(receivers)
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(cfg.EMAIL_SENDER, cfg.EMAIL_PASSWORD)
                server.sendmail(cfg.EMAIL_SENDER, receivers, msg.as_string())
            print("Email sent to: " + ", ".join(receivers))
            return True
        except Exception as e:
            print("Email failed: " + str(e))
            return False

    def build_subject(self, portfolio, pulse):
        n_buy  = sum(1 for p in portfolio if p["factor_score"].verdict == "BUY")
        n_hold = sum(1 for p in portfolio if p["factor_score"].verdict == "HOLD")
        fear   = pulse.get("fear_level", "NEUTRAL")
        et     = pytz.timezone("US/Eastern")
        now    = datetime.now(et)
        ds     = now.strftime("%b %d")
        return "AXIOM US - " + ds + " - " + str(n_buy) + " BUY / " + str(n_hold) + " HOLD - " + fear

    def send_digest(self, portfolio, pulse):
        subject = self.build_subject(portfolio, pulse)
        try:
            with open("docs/index.html", "r") as f:
                html = f.read()
        except Exception as e:
            print("Could not read dashboard: " + str(e))
            return False
        return self.send(subject, html)
