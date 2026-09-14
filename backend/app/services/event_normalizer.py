from datetime import datetime
from typing import Any, Dict, Optional


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def normalize_wazuh_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    rule = payload.get("rule") or {}
    agent = payload.get("agent") or {}
    data = payload.get("data") or {}

    groups = rule.get("groups") or []

    if groups:
        event_type = groups[0]
    else:
        event_type = payload.get("name") or "unknown"

    return {
        "timestamp": _parse_timestamp(payload.get("timestamp")),
        "event_type": event_type,
        "rule_id": str(rule.get("id")) if rule.get("id") is not None else None,
        "rule_level": _as_int(rule.get("level")),
        "rule_description": rule.get("description"),
        "agent_name": agent.get("name"),
        "src_ip": payload.get("srcip") or data.get("srcip"),
        "dst_ip": payload.get("dstip") or data.get("dstip"),
        "username": payload.get("srcuser") or data.get("srcuser"),
        "raw_message": payload.get("full_log"),
    }