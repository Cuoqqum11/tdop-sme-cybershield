from app.models import NormalizedEvent


def calculate_simple_risk(event: NormalizedEvent) -> int:
    """
    Initial simple risk engine.

    Later this will combine:
    - Wazuh severity
    - anomaly score
    - asset criticality
    - repeat frequency
    """

    if event.rule_level is None:
        return 0

    risk = event.rule_level * 10

    if risk < 0:
        return 0

    if risk > 100:
        return 100

    return risk