import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlmodel import Session, select

from app.models import Alert, Incident, NormalizedEvent

CORRELATION_WINDOW_MINUTES = 15


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _build_explanation(reasons: Dict[str, str]) -> str:
    return "Why is this suspicious?\n- " + "\n- ".join(reasons.values())


def correlate_and_update_incident(
    session: Session,
    alert: Alert,
    event: NormalizedEvent,
    features: Dict[str, Any],
    title: str,
    reasons: Dict[str, str],
    recommended_action: str,
) -> Incident:

    entity_type = features.get("entity_type", "unknown")
    entity_value = features.get("entity_value", "unknown")

    event_time = _aware(event.timestamp) if event.timestamp else datetime.now(timezone.utc)
    window_start = event_time - timedelta(minutes=CORRELATION_WINDOW_MINUTES)

    statement = select(Incident).where(
        Incident.entity_type == entity_type,
        Incident.entity_value == entity_value,
        Incident.status == "open",
        Incident.last_seen >= window_start,
    )

    existing_incident = session.exec(statement).first()

    if existing_incident:
        # --- UPDATE EXISTING INCIDENT ---
        if event_time > _aware(existing_incident.last_seen):
            existing_incident.last_seen = event_time

        if alert.risk_score > existing_incident.risk_score:
            existing_incident.risk_score = alert.risk_score

        # Merge reasons by key: no duplicates, latest values win
        merged: Dict[str, str] = {}
        if existing_incident.reasons_json:
            try:
                merged = json.loads(existing_incident.reasons_json)
            except json.JSONDecodeError:
                merged = {}
        merged.update(reasons)

        existing_incident.reasons_json = json.dumps(merged)
        existing_incident.explanation = _build_explanation(merged)
        existing_incident.alert_count = (existing_incident.alert_count or 0) + 1

        session.add(existing_incident)
        session.commit()
        session.refresh(existing_incident)

        alert.incident_id = existing_incident.id
        session.add(alert)
        session.commit()

        return existing_incident

    else:
        # --- CREATE NEW INCIDENT ---
        new_incident = Incident(
            title=title,
            status="open",
            risk_score=alert.risk_score,
            reasons_json=json.dumps(reasons),
            explanation=_build_explanation(reasons),
            recommended_action=recommended_action,
            entity_type=entity_type,
            entity_value=entity_value,
            alert_count=1,
            first_seen=event_time,
            last_seen=event_time,
        )
        session.add(new_incident)
        session.commit()
        session.refresh(new_incident)

        alert.incident_id = new_incident.id
        session.add(alert)
        session.commit()

        return new_incident