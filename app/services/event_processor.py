import json
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.webhook_event import WebhookEvent
from app.utils.logging import get_logger
from app.utils.formatters import format_push_message, format_pr_message, format_issue_message

logger = get_logger(__name__)


class EventProcessor:
    def __init__(self, db: Session):
        self.db = db
    
    def check_duplicate(self, event_id: str) -> bool:
        existing = self.db.query(WebhookEvent).filter(
            WebhookEvent.event_id == event_id
        ).first()
        return existing is not None
    
    def process_push_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        commits = payload.get("commits", [])
        commit_messages = "; ".join([
            c.get("message", "").split("\n")[0][:100] 
            for c in commits[:10]
        ])
        
        author = None
        timestamp = None
        if commits:
            author = commits[0].get("author", {}).get("name")
            timestamp = commits[0].get("timestamp")
        
        return {
            "commit_messages": commit_messages,
            "author": author,
            "timestamp": timestamp,
        }
    
    def process_pr_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pr = payload.get("pull_request", {})
        return {
            "pr_title": pr.get("title"),
            "pr_action": payload.get("action"),
            "pr_user": pr.get("user", {}).get("login"),
        }
    
    def process_issue_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        issue = payload.get("issue", {})
        return {
            "issue_title": issue.get("title"),
            "issue_status": issue.get("state"),
        }
    
    def create_event(
        self,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any],
        formatted_message: Optional[str] = None
    ) -> WebhookEvent:
        event_data = {
            "event_id": event_id,
            "event_type": event_type,
            "payload": json.dumps(payload),
        }
        
        if event_type == "push":
            event_data.update(self.process_push_event(payload))
        elif event_type == "pull_request":
            event_data.update(self.process_pr_event(payload))
        elif event_type == "issues":
            event_data.update(self.process_issue_event(payload))
        
        event = WebhookEvent(**event_data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def mark_as_processed(self, event_id: str, success: bool = True, error: str = None):
        event = self.db.query(WebhookEvent).filter(
            WebhookEvent.event_id == event_id
        ).first()
        
        if event:
            event.processed = success
            event.delivery_status = "processed" if success else "failed"
            if error:
                event.error_message = error
            self.db.commit()
    
    def mark_notification_sent(self, event_id: str):
        event = self.db.query(WebhookEvent).filter(
            WebhookEvent.event_id == event_id
        ).first()
        
        if event:
            event.notification_sent = True
            self.db.commit()
