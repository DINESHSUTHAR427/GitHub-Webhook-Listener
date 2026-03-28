from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WebhookResponse(BaseModel):
    success: bool
    message: str
    event_id: Optional[str] = None
    event_type: Optional[str] = None
    already_processed: bool = False


class EventStats(BaseModel):
    total_events: int
    push_events: int
    pull_request_events: int
    issue_events: int
    processed_events: int
    failed_events: int
