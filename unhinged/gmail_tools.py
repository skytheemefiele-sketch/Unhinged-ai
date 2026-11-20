"""Optional Gmail IMAP/SMTP integration; credentials are never persisted."""
import imaplib, smtplib, ssl, email, re
from email.message import EmailMessage
from email.header import decode_header, make_header
import os

class GmailClient:
    def __init__(self):
        self.user = os.getenv("AI_GMAIL_USER")
        self.password = os.getenv("AI_GMAIL_APP_PASS")
        if not self.user or not self.password:
            raise RuntimeError("Set AI_GMAIL_USER and AI_GMAIL_APP_PASS privately in .env")

    def recent_messages(self, limit=10):
        with imaplib.IMAP4_SSL("imap.gmail.com", 993) as box:
            box.login(self.user, self.password); box.select("INBOX", readonly=True)
            _, data = box.search(None, "ALL")
            ids = data[0].split()[-max(1, min(limit, 30)):]
            out=[]
            for mid in reversed(ids):
                _, parts = box.fetch(mid, "(RFC822)")
                msg=email.message_from_bytes(parts[0][1])
                subject=str(make_header(decode_header(msg.get("Subject",""))))
                sender=msg.get("From","")
                body=""
                for part in msg.walk():
                    if part.get_content_type()=="text/plain" and not part.get_filename():
                        raw=part.get_payload(decode=True) or b""
                        body += raw.decode(part.get_content_charset() or "utf-8",errors="replace")
                codes=re.findall(r"(?<!\\d)\\d{4,8}(?!\\d)", body)
                out.append({"from":sender,"subject":subject,"codes":codes,"snippet":body[:700]})
            return out

    def send(self, to, subject, body, confirmed=False):
        if not confirmed: raise RuntimeError("Email sending requires explicit confirmation")
        msg=EmailMessage(); msg["From"]=self.user; msg["To"]=to
        msg["Subject"]=subject; msg.set_content(body)
        context=ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
            smtp.login(self.user,self.password); smtp.send_message(msg)
        return "Email sent"
