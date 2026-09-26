from typing import List
from sqlmodel import Session, select

from app.models import Incident, ResponseAction
from app.core.config import settings


def generate_response_actions(session: Session, incident: Incident) -> List[ResponseAction]:
    """
    Generates response actions based on the incident's risk score and context.
    """
    actions = []
    
    # 1. Always notify admin for high-risk incidents
    if incident.risk_score >= 70:
        actions.append(ResponseAction(
            incident_id=incident.id,
            action_type="notify_admin",
            status="executed", # Notifications are "executed" even in dry_run
            mode=settings.response_mode,
            details=f"High risk incident detected: {incident.title}. Risk Score: {incident.risk_score}"
        ))
        
    # 2. Block IP if entity is an IP and risk is high
    if incident.entity_type == "src_ip" and incident.entity_value != "unknown" and incident.risk_score >= 80:
        actions.append(ResponseAction(
            incident_id=incident.id,
            action_type="block_ip",
            status="proposed",
            mode=settings.response_mode,
            details=f"Block malicious source IP: {incident.entity_value} via Wazuh Active Response."
        ))
        
    # 3. Isolate host if risk is critical
    if incident.risk_score >= 90:
         actions.append(ResponseAction(
            incident_id=incident.id,
            action_type="isolate_host",
            status="proposed",
            mode=settings.response_mode,
            details="Isolate affected endpoint from the network to prevent lateral movement."
        ))

    # Save to database
    for action in actions:
        session.add(action)
        
    if actions:
        session.commit()
        
    return actions