from fastapi import FastAPI, Depends
from sqlmodel import Session, select

from app.core.database import init_db, get_session
from app.models import RawEvent, NormalizedEvent, Alert, Incident
from app.services.event_normalizer import normalize_wazuh_event
from app.services.risk_engine import calculate_simple_risk


app = FastAPI(
    title="SME CyberShield API",
    description="Lightweight AI-Assisted XDR for Vietnamese SMEs",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "product": "SME CyberShield",
    }


@app.post("/api/v1/wazuh/webhook")
def receive_wazuh_event(
    payload: dict,
    session: Session = Depends(get_session),
):
    raw_event = RawEvent(payload=payload)
    session.add(raw_event)
    session.commit()
    session.refresh(raw_event)

    normalized_data = normalize_wazuh_event(payload)

    normalized_event = NormalizedEvent(
        raw_event_id=raw_event.id,
        **normalized_data,
    )

    session.add(normalized_event)
    session.commit()
    session.refresh(normalized_event)

    risk_score = calculate_simple_risk(normalized_event)

    if normalized_event.rule_level is not None and normalized_event.rule_level >= 7:
        alert = Alert(
            normalized_event_id=normalized_event.id,
            title=normalized_event.rule_description or "Wazuh security alert",
            severity=normalized_event.rule_level,
            risk_score=risk_score,
        )

        session.add(alert)
        session.commit()

    return {
        "status": "received",
        "raw_event_id": raw_event.id,
        "normalized_event_id": normalized_event.id,
        "risk_score": risk_score,
    }


@app.get("/api/v1/alerts")
def list_alerts(session: Session = Depends(get_session)):
    alerts = session.exec(select(Alert)).all()
    return alerts


@app.get("/api/v1/incidents")
def list_incidents(session: Session = Depends(get_session)):
    incidents = session.exec(select(Incident)).all()
    return incidents


@app.get("/api/v1/dashboard/summary")
def dashboard_summary(session: Session = Depends(get_session)):
    alerts = session.exec(select(Alert)).all()
    incidents = session.exec(select(Incident)).all()

    return {
        "total_alerts": len(alerts),
        "total_incidents": len(incidents),
        "system_status": "monitoring",
    }