# services/ingest_service/app/influx.py
import json
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import (
    INFLUX_ENABLED,
    INFLUX_HOST,
    INFLUX_TOKEN,
    INFLUX_DATABASE,
    INFLUX_TABLE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_to_epoch_seconds(ts: str) -> int:
    """
    Convert ISO timestamp to epoch seconds.
    Handles:
      - "2026-02-10T16:59:10.239950Z"
      - "2026-02-10T16:59:10+00:00"
    """
    ts = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def parse_topic(topic: str) -> tuple[str, str]:
    """
    Upgrade 2:
    Convert topic -> safe tags.

    Expected topics:
      tennis/sensor/1/events  -> stream="sensor", source_id="1"
      tennis/camera/1/ball    -> stream="camera", source_id="1"
    """
    parts = topic.split("/")
    stream = parts[1] if len(parts) > 1 else "unknown"
    source_id = parts[2] if len(parts) > 2 else "unknown"
    return stream, source_id


def _write_lp_v3(line_protocol: str, db: str, precision: str = "s") -> None:
    """
    Upgrade 3:
    Write line protocol via InfluxDB 3 Core v3 endpoint.
    This avoids /api/v2/write completely.
    """
    if not INFLUX_TOKEN:
        raise RuntimeError("INFLUX_TOKEN is empty")

    params = urlencode({"db": db, "precision": precision})
    url = f"{INFLUX_HOST}/api/v3/write_lp?{params}"

    req = Request(url, data=line_protocol.encode("utf-8"), method="POST")
    req.add_header("Authorization", f"Bearer {INFLUX_TOKEN}")
    req.add_header("Content-Type", "text/plain; charset=utf-8")

    # Success is usually 204 No Content (sometimes 200)
    with urlopen(req, timeout=10) as resp:
        if resp.status not in (204, 200):
            raise RuntimeError(f"Influx write failed HTTP {resp.status}")


def write_event_to_influx(ev: Dict[str, Any]) -> None:
    """
    Main write function used by ingest.
    - Builds line protocol
    - Sends it to /api/v3/write_lp

    Event format expected:
      {
        "ts": "...",
        "topic": "...",
        "payload": {...}
      }
    """
    if not INFLUX_ENABLED:
        return

    topic = ev.get("topic", "unknown")
    stream, source_id = parse_topic(topic)

    ts_epoch = iso_to_epoch_seconds(ev.get("ts") or now_iso())

    # Store payload as a JSON string field (simple MVP)
    payload_str = json.dumps(ev.get("payload", {}), ensure_ascii=False)
    escaped_payload = payload_str.replace('"', '\\"')

    # line protocol:
    # measurement,tag=value field="..." timestamp
    line = f'{INFLUX_TABLE},stream={stream},source_id={source_id} payload="{escaped_payload}" {ts_epoch}'

    _write_lp_v3(line, db=INFLUX_DATABASE, precision="s")


def query_influx_sql(sql: str) -> list[dict]:
    """
    Query InfluxDB 3 using the v3 SQL endpoint.
    Returns a list[dict] rows (JSON array).
    """
    if not INFLUX_TOKEN:
        raise RuntimeError("INFLUX_TOKEN is empty")

    params = urlencode({"db": INFLUX_DATABASE, "q": sql})
    url = f"{INFLUX_HOST}/api/v3/query_sql?{params}"

    req = Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {INFLUX_TOKEN}")

    with urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)
