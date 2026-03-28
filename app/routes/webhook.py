from fastapi import APIRouter, Request, Depends, HTTPException, Header, Response
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.schemas.webhook import WebhookResponse
from app.schemas.notification import NotificationResponse
from app.services.event_processor import EventProcessor
from app.services.notification_service import NotificationService
from app.utils.signature import verify_github_signature
from app.utils.logging import get_logger
from app.utils.formatters import format_push_message, format_pr_message, format_issue_message

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = get_logger(__name__)


@router.post("/github", response_model=WebhookResponse)
async def receive_github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not x_github_event:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")
    
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Delivery header")
    
    raw_body = await request.body()
    
    if x_hub_signature_256:
        if not verify_github_signature(raw_body, x_hub_signature_256):
            logger.warning(f"Invalid signature for event {x_github_delivery}")
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.warning(f"No signature provided for event {x_github_delivery}")
    
    try:
        payload: Dict[str, Any] = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    processor = EventProcessor(db)
    
    if processor.check_duplicate(x_github_delivery):
        logger.info(f"Duplicate event received: {x_github_delivery}")
        return WebhookResponse(
            success=True,
            message="Event already processed",
            event_id=x_github_delivery,
            event_type=x_github_event,
            already_processed=True
        )
    
    try:
        formatted_message = None
        if x_github_event == "push":
            formatted_message = format_push_message(payload)
        elif x_github_event == "pull_request":
            formatted_message = format_pr_message(payload)
        elif x_github_event == "issues":
            formatted_message = format_issue_message(payload)
        
        event = processor.create_event(
            event_id=x_github_delivery,
            event_type=x_github_event,
            payload=payload,
            formatted_message=formatted_message
        )
        
        logger.info(f"Event {x_github_delivery} ({x_github_event}) stored successfully")
        
        if formatted_message:
            notification_service = NotificationService()
            await notification_service.send_notifications(
                event_type=x_github_event,
                message=formatted_message
            )
            processor.mark_notification_sent(x_github_delivery)
        
        processor.mark_as_processed(x_github_delivery, success=True)
        
        return WebhookResponse(
            success=True,
            message=f"Event {x_github_event} processed successfully",
            event_id=x_github_delivery,
            event_type=x_github_event
        )
        
    except Exception as e:
        logger.error(f"Error processing event {x_github_delivery}: {str(e)}")
        processor.mark_as_processed(x_github_delivery, success=False, error=str(e))
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "github-webhook-listener"}
