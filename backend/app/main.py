from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from app.models import SMEProfile

from app.core.config import settings
from app.core.database import init_db, get_session
from app.models import (
    RawEvent,
    NormalizedEvent,
    Alert,
    Incident,
    ResponseAction,
) 
from app.services.event_normalizer import normalize_wazuh_event
from app.services.feature_extractor import build_feature_vector_for_event
from app.services.anomaly_scorer import score_feature_vector
from app.services.risk_engine import calculate_risk

# NEW IMPORTS
from app.services.explainer import generate_explanation
from app.services.incident_correlator import correlate_and_update_incident
from app.services.response_orchestrator import generate_response_actions
from fastapi.middleware.cors import CORSMiddleware

class SMEProfileInput(BaseModel):
    company_type: str
    company_size: str
    services: str = ""
    security_mode: str = "monitoring"
    language: str = "vi"

app = FastAPI(
    title="SME CyberShield API",
    description="Lightweight AI-Assisted XDR for Vietnamese SMEs",
    version="0.3.0", # Bumped version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

        # --- INCIDENT CORRELATION ---
        incident = correlate_and_update_incident(
            session=session,
            alert=alert,
            event=normalized_event,
            features=features,
            title=title,
            reasons=reasons,
            recommended_action=recommended_action,
        )
        
        # --- RESPONSE ORCHESTRATOR ---
        # Only generate response actions if this is a brand new incident
        existing_actions = session.exec(
            select(ResponseAction).where(ResponseAction.incident_id == incident.id)
        ).first()
        
        if not existing_actions:
            generate_response_actions(session, incident)

        incident_data = {
            "incident_id": incident.id,
            "title": incident.title,
            "risk_score": incident.risk_score,
            "alert_count": incident.alert_count
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

@app.get("/api/v1/response/history")
def get_response_history(session: Session = Depends(get_session)):
    """Returns all proposed and executed response actions."""
    actions = session.exec(select(ResponseAction)).all()
    return actions

@app.post("/api/v1/response/{action_id}/approve")
def approve_action(action_id: int, session: Session = Depends(get_session)):
    """
    Simulates an admin approving a proposed response action.
    In a real production system, this would trigger the Wazuh Active Response script.
    """
    action = session.get(ResponseAction, action_id)
    if not action:
        return {"error": "Action not found"}
    
    if action.status == "proposed":
        action.status = "approved"
        # Here you would normally call Wazuh API to execute the block/isolate command
        session.add(action)
        session.commit()
        return {
            "status": "approved", 
            "message": f"Action '{action.action_type}' approved and executed in {action.mode} mode."
        }
    
    return {"status": action.status, "message": "Action already processed."}

@app.get("/api/v1/onboarding/profile")
def get_profile(session: Session = Depends(get_session)):
    return session.exec(select(SMEProfile)).first()


@app.post("/api/v1/onboarding/profile")
def save_profile(payload: SMEProfileInput, session: Session = Depends(get_session)):
    profile = session.exec(select(SMEProfile)).first()

    if profile:
        profile.company_type = payload.company_type
        profile.company_size = payload.company_size
        profile.services = payload.services
        profile.security_mode = payload.security_mode
        profile.language = payload.language
    else:
        profile = SMEProfile(**payload.dict())

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile