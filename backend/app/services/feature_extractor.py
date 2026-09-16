from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Session, select

from app.core.config import settings
from app.models import NormalizedEvent


FEATURE_COLUMNS = [
    "event_count",
    "unique_rule_id_count",
    "unique_src_ip_count",
    "unique_username_count",
    "max_rule_level",
    "avg_rule_level",
    "rule_level_sum",
    "high_severity_count",
    "failed_login_count",
    "off_hours_event_count",
    "failed_login_ratio",
    "high_severity_ratio",
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(value: datetime) -> datetime:
    """
    Ensure datetime has timezone information.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _floor_to_window(
    value: datetime,
    window_minutes: Optional[int] = None,
) -> datetime:
    """
    Round timestamp down to the beginning of the feature window.

    Example:
    09:07 -> 09:05 if window_minutes = 5
    """
    if window_minutes is None:
        window_minutes = settings.feature_window_minutes

    value = _ensure_aware(value)

    floored_minute = (value.minute // window_minutes) * window_minutes

    return value.replace(
        minute=floored_minute,
        second=0,
        microsecond=0,
    )


def _get_entity(event: NormalizedEvent) -> Tuple[str, str]:
    """
    Decide which entity the feature vector belongs to.

    For MVP:
    - If source IP exists, group by source IP.
    - Else if agent name exists, group by agent.
    - Else use global.
    """
    if event.src_ip:
        return "src_ip", event.src_ip

    if event.agent_name:
        return "agent_name", event.agent_name

    return "global", "global"


def _filter_events_by_entity(
    events: List[NormalizedEvent],
    entity_type: str,
    entity_value: str,
) -> List[NormalizedEvent]:
    if entity_type == "src_ip":
        return [event for event in events if event.src_ip == entity_value]

    if entity_type == "agent_name":
        return [event for event in events if event.agent_name == entity_value]

    return list(events)


def _is_failed_login(event: NormalizedEvent) -> bool:
    """
    Simple heuristic to detect failed login events from normalized Wazuh data.

    Later this can be improved using rule groups, decoder names, or MITRE mapping.
    """
    raw_message = (event.raw_message or "").lower()
    event_type = (event.event_type or "").lower()

    if "authentication_failures" in event_type:
        return True

    if "failed" in raw_message and (
        "password" in raw_message
        or "login" in raw_message
        or "authentication" in raw_message
    ):
        return True

    return False


def _is_off_hour(value: datetime) -> bool:
    """
    Simple SME office-hours heuristic.

    Suspicious if activity happens:
    - before 06:00
    - after 22:00
    """
    value = _ensure_aware(value)

    return value.hour < 6 or value.hour >= 22


def build_feature_vector_for_event(
    session: Session,
    event: NormalizedEvent,
) -> Dict[str, Any]:
    """
    Build a feature vector for a normalized event.

    This is an MVP feature extractor.

    It groups events by:
    - time window
    - source IP / agent / global entity

    Then it calculates behavioral features.
    """
    timestamp = _ensure_aware(event.timestamp or _utcnow())

    window_start = _floor_to_window(timestamp)
    window_end = window_start + timedelta(minutes=settings.feature_window_minutes)

    all_events = session.exec(select(NormalizedEvent)).all()

    window_events: List[NormalizedEvent] = []

    for item in all_events:
        if not item.timestamp:
            continue

        item_time = _ensure_aware(item.timestamp)

        if window_start <= item_time <= window_end:
            window_events.append(item)

    entity_type, entity_value = _get_entity(event)

    window_events = _filter_events_by_entity(
        window_events,
        entity_type,
        entity_value,
    )

    # Ensure the current event is included.
    if event.id is not None and not any(item.id == event.id for item in window_events):
        window_events.append(event)

    event_count = len(window_events)

    rule_levels = [
        item.rule_level if item.rule_level is not None else 0
        for item in window_events
    ]

    max_rule_level = max(rule_levels) if rule_levels else 0
    rule_level_sum = sum(rule_levels)
    avg_rule_level = rule_level_sum / event_count if event_count else 0.0

    high_severity_count = sum(1 for level in rule_levels if level >= 7)

    failed_login_count = sum(
        1 for item in window_events if _is_failed_login(item)
    )

    off_hours_event_count = sum(
        1
        for item in window_events
        if item.timestamp and _is_off_hour(item.timestamp)
    )

    unique_rule_id_count = len({
        item.rule_id
        for item in window_events
        if item.rule_id
    })

    unique_src_ip_count = len({
        item.src_ip
        for item in window_events
        if item.src_ip
    })

    unique_username_count = len({
        item.username
        for item in window_events
        if item.username
    })

    failed_login_ratio = failed_login_count / event_count if event_count else 0.0
    high_severity_ratio = high_severity_count / event_count if event_count else 0.0

    return {
        "window_start": window_start.isoformat(),
        "entity_type": entity_type,
        "entity_value": entity_value or "unknown",

        "event_count": event_count,
        "unique_rule_id_count": unique_rule_id_count,
        "unique_src_ip_count": unique_src_ip_count,
        "unique_username_count": unique_username_count,

        "max_rule_level": max_rule_level,
        "avg_rule_level": avg_rule_level,
        "rule_level_sum": rule_level_sum,

        "high_severity_count": high_severity_count,
        "failed_login_count": failed_login_count,
        "off_hours_event_count": off_hours_event_count,

        "failed_login_ratio": failed_login_ratio,
        "high_severity_ratio": high_severity_ratio,
    }