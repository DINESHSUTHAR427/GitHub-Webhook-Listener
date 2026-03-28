import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
import httpx
from app.utils.logging import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)


class NotificationService:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.email_from = os.getenv("EMAIL_FROM", "")
        self.email_to = os.getenv("EMAIL_TO", "")
    
    async def send_telegram(self, message: str, event_type: str) -> Tuple[bool, Optional[str]]:
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured")
            return False, "Telegram not configured"
        
        if self.telegram_token == "your_telegram_bot_token":
            logger.warning("Telegram bot token not set")
            return False, "Telegram bot token not set"
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Telegram notification sent for {event_type}")
                    return True, None
                else:
                    error = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"Telegram error: {error}")
                    return False, error
        except Exception as e:
            logger.error(f"Telegram exception: {str(e)}")
            return False, str(e)
    
    def send_email(self, subject: str, body: str, html: bool = True) -> Tuple[bool, Optional[str]]:
        if not self.smtp_user or not self.smtp_password:
            logger.warning("Email not configured")
            return False, "Email not configured"
        
        if self.smtp_user == "your_email@gmail.com":
            logger.warning("Email not set")
            return False, "Email not configured"
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_from
            msg["To"] = self.email_to
            
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject}")
            return True, None
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return False, str(e)
    
    async def send_notifications(
        self,
        event_type: str,
        message: str,
        email_html: str = None
    ) -> dict:
        results = {
            "telegram_sent": False,
            "email_sent": False,
            "telegram_error": None,
            "email_error": None,
        }
        
        tg_sent, tg_error = await self.send_telegram(message, event_type)
        results["telegram_sent"] = tg_sent
        results["telegram_error"] = tg_error
        
        email_subject = f"GitHub Webhook: {event_type.upper()}"
        email_sent, email_error = self.send_email(email_subject, message, html=False)
        results["email_sent"] = email_sent
        results["email_error"] = email_error
        
        return results
