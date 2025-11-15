# src/observability/observability.py
import logging, json
from config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("smartsupport")

def log_event(event_type: str, data: dict):
    # Structured log for easy parsing
    payload = {"event": event_type}
    payload.update(data or {})
    logger.info(json.dumps(payload))
