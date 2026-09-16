from typing import Optional

from app.models import NormalizedEvent


def _clamp_risk(value: int) -> int:
    if value < 0:
        return 0

    if value > 100:
        return 100

    return value


def calculate_simple_risk(event: NormalizedEvent) -> int:
    """
    Old simple risk engine.

    Kept for backward compatibility.
    """
    if event.rule_level is None:
        return 0

    risk = event.rule_level * 10

    return _clamp_risk(risk)


def calculate_risk(
    event: NormalizedEvent,
    anomaly_score: Optional[float] = None,
) -> int:
    """
    Combine Wazuh severity and Isolation Forest anomaly score.

    MVP formula:

    risk_score =
        0.60 * Wazuh severity score
      + 0.40 * anomaly score

    Wazuh severity score:
        rule_level * 10

    Anomaly score:
        0 to 100
    """
    if event.rule_level is None:
        severity_score = 0
    else:
        severity_score = event.rule_level * 10

    if anomaly_score is None:
        return _clamp_risk(int(severity_score))

    anomaly_component = anomaly_score * 100

    risk = int(
        round(
            (0.60 * severity_score)
            + (0.40 * anomaly_component)
        )
    )

    return _clamp_risk(risk)