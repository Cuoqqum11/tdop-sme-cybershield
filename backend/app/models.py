from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


def utcnow():
    return datetime.now(timezone.utc)


class RawEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(default="wazuh")
    payload: Dict[str, Any] = Field(sa_column=Column(JSON))
    received_at: datetime = Field(default_factory=utcnow)


class NormalizedEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    raw_event_id: Optional[int] = None

    timestamp: Optional[datetime] = None
    event_type: str = "unknown"

    rule_id: Optional[str] = None
    rule_level: Optional[int] = None
    rule_description: Optional[str] = None

    agent_name: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    username: Optional[str] = None

    raw_message: Optional[str] = None


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    normalized_event_id: Optional[int] = None

    title: str
    severity: Optional[int] = None
    risk_score: int = 0
    anomaly_score: Optional[float] = None

    status: str = "new"

    created_at: datetime = Field(default_factory=utcnow)


class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    status: str = "open"

    risk_score: int = 0

    explanation: Optional[str] = None
    recommended_action: Optional[str] = None

    first_seen: datetime = Field(default_factory=utcnow)
    last_seen: datetime = Field(default_factory=utcnow)


class ResponseAction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    incident_id: Optional[int] = None

    action_type: str
    status: str = "proposed"
    mode: str = "dry_run"

    details: Optional[str] = None

    created_at: datetime = Field(default_factory=utcnow)


class SMEProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    company_type: str
    company_size: str

    services: Optional[str] = None

    security_mode: str = "monitoring"
    language: str = "vi"

    created_at: datetime = Field(default_factory=utcnow)