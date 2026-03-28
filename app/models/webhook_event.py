from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func
from app.database.connection import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    delivery_status = Column(String(20), default="received")
    payload = Column(Text, nullable=False)
    commit_messages = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    timestamp = Column(String(50), nullable=True)
    pr_title = Column(String(500), nullable=True)
    pr_action = Column(String(50), nullable=True)
    pr_user = Column(String(100), nullable=True)
    issue_title = Column(String(500), nullable=True)
    issue_status = Column(String(50), nullable=True)
    processed = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_event_type', 'event_type'),
        Index('idx_created_at', 'created_at'),
        Index('idx_processed', 'processed'),
    )
