from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import init_db, get_session
from app.models import (
    RawEvent,
    NormalizedEvent,
    Alert,
    Incident,
)
from app.services.event_normalizer import normalize_wazuh_event
from app.services.feature_extractor import build_feature_vector_for_event
from app.services.anomaly_scorer import score_feature_vector
from app.services.risk_engine import calculate_risk

# NEW IMPORTS
from app.services.explainer import generate_explanation
from app.services.incident_correlator import correlate_and_update_incident

app = FastAPI(
    title="SME CyberShield API",
    description="Lightweight AI-Assisted XDR for Vietnamese SMEs",
    version="0.3.0", # Bumped version
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "product": "SME CyberShield"}

@app.post("/api/v1/wazuh/webhook")
def receive_wazuh_event(
    payload: dict,
    session: Session = Depends(get_session),
):
    # 1. Store raw Wazuh event
    raw_event = RawEvent(payload=payload)
    session.add(raw_event)
    session.commit()
    session.refresh(raw_event)

    # 2. Normalize event
    normalized_data = normalize_wazuh_event(payload)
    if normalized_data.get("timestamp") is None:
        normalized_data["timestamp"] = datetime.now(timezone.utc)

    normalized_event = NormalizedEvent(raw_event_id=raw_event.id, **normalized_data)
    session.add(normalized_event)
    session.commit()
    session.refresh(normalized_event)

    # 3. Extract features & 4. Score with AI
    features = build_feature_vector_for_event(session=session, event=normalized_event)
    anomaly_score = score_feature_vector(features)

    # 5. Calculate risk score
    risk_score = calculate_risk(event=normalized_event, anomaly_score=anomaly_score)

    # 6. Decide whether to create alert
    should_alert = False
    if normalized_event.rule_level is not None and normalized_event.rule_level >= 7:
        should_alert = True
    if anomaly_score is not None and anomaly_score >= settings.anomaly_threshold:
        should_alert = True

    incident_data = None

    if should_alert:
        # --- NEW: EXPLAINABILITY ---
        title, reasons, recommended_action = generate_explanation(
            event=normalized_event,
            features=features,
            anomaly_score=anomaly_score,
        )

        alert = Alert(
            normalized_event_id=normalized_event.id,
            title=title,
            severity=normalized_event.rule_level,
            risk_score=risk_score,
            anomaly_score=anomaly_score,
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)

        # --- NEW: INCIDENT CORRELATION ---
        incident = correlate_and_update_incident(
            session=session,
            alert=alert,
            event=normalized_event,
            features=features,
            title=title,
            reasons=reasons,
            recommended_action=recommended_action,
        )
        
        incident_data = {
            "incident_id": incident.id,
            "title": incident.title,
            "risk_score": incident.risk_score
        }

    return {
        "status": "received",
        "raw_event_id": raw_event.id,
        "normalized_event_id": normalized_event.id,
        "anomaly_score": anomaly_score,
        "risk_score": risk_score,
        "incident": incident_data
    }

@app.get("/api/v1/alerts")
def list_alerts(session: Session = Depends(get_session)):
    return session.exec(select(Alert)).all()

@app.get("/api/v1/incidents")
def list_incidents(session: Session = Depends(get_session)):
    return session.exec(select(Incident)).all()

@app.get("/api/v1/dashboard/summary")
def dashboard_summary(session: Session = Depends(get_session)):
    alerts = session.exec(select(Alert)).all()
    incidents = session.exec(select(Incident)).all()

    return {
        "total_alerts": len(alerts),
        "total_incidents": len(incidents),
        "system_status": "monitoring",
    }