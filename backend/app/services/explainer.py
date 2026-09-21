from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.models import NormalizedEvent


def generate_explanation(
    event: NormalizedEvent,
    features: Dict[str, Any],
    anomaly_score: Optional[float],
) -> Tuple[str, Dict[str, str], str]:
    """
    Returns: (title, reasons_dict, recommended_action)

    reasons_dict is keyed by reason type so incidents can merge
    reasons without duplicating them.
    """
    reasons: Dict[str, str] = {}
    title = "Suspicious Activity Detected"
    recommended_action = "Monitor the affected asset and review logs."

    # 1. Brute force / failed logins
    failed_logins = features.get("failed_login_count", 0)
    if failed_logins >= 3:
        reasons["failed_logins"] = (
            f"Multiple failed login attempts detected "
            f"({failed_logins} in the last {settings.feature_window_minutes} minutes)."
        )
        title = "Possible Brute Force or Credential Stuffing"
        recommended_action = (
            "Block the source IP and force a password reset for the targeted account."
        )

    # 2. Off-hours activity
    if features.get("off_hours_event_count", 0) > 0:
        reasons["off_hours"] = (
            "Activity occurred outside normal business hours "
            "(before 06:00 or after 22:00)."
        )

    # 3. Wazuh rule severity
    if event.rule_level and event.rule_level >= 10:
        reasons["critical_rule"] = (
            f"Critical Wazuh rule triggered: {event.rule_description or 'Unknown'}"
        )
        title = event.rule_description or "Critical Security Alert"
        recommended_action = (
            "Immediately isolate the affected endpoint and investigate."
        )
    elif event.rule_level and event.rule_level >= 7:
        reasons["high_severity_rule"] = (
            f"High severity Wazuh rule triggered: {event.rule_description or 'Unknown'}"
        )

    # 4. AI anomaly score
    if anomaly_score is not None and anomaly_score >= settings.anomaly_threshold:
        reasons["ai_anomaly"] = (
            f"AI anomaly detection flagged this behavior as highly unusual "
            f"(Score: {anomaly_score:.2f})."
        )

    # 5. Possible scanning
    if features.get("unique_src_ip_count", 0) > 10:
        reasons["scanning"] = (
            f"High number of unique source IPs observed "
            f"({features['unique_src_ip_count']}). Possible network scanning."
        )

    if not reasons:
        reasons["generic"] = (
            "Event matched alert thresholds but lacks specific behavioral context."
        )

    return title, reasons, recommended_action