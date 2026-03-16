import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz


class Notifier:
    def __init__(self, config):
        self.config = config

    def send(self, subject, html_body, recipients=None):
        cfg = self.config
        if recipients is None:
            recipients = cfg.EMAIL_RECIPIENTS

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg.EMAIL_FROM
        msg["To"]      = ", ".join(recipients)
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(cfg.EMAIL_FROM, cfg.EMAIL_PASSWORD)
                server.sendmail(cfg.EMAIL_FROM, recipients, msg.as_string())
            print("Email sent to: " + ", ".join(recipients))
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

    def notify(self, portfolio, pulse, budget, html_dashboard):
        subject = self.build_subject(portfolio, pulse)
        self.send(subject, html_dashboard)
