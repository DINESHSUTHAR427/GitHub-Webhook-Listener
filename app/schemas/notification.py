from pydantic import BaseModel
from typing import Optional


class NotificationResponse(BaseModel):
    telegram_sent: bool = False
    email_sent: bool = False
    telegram_error: Optional[str] = None
    email_error: Optional[str] = None
