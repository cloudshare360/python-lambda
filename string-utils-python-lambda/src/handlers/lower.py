"""Handler for the lower flow."""

import json
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PIP_MODULES = os.path.join(_PROJECT_ROOT, "pip-modules")
for _path in (_PROJECT_ROOT, _PIP_MODULES):
    if _path not in sys.path:
        sys.path.insert(0, _path)

sys.pycache_prefix = os.path.join(_PIP_MODULES, ".pycache")

from src.common.errors import AppError, ValidationError
from src.common.logger import get_logger
from src.common.response import build_response
from src.services import string_service

logger = get_logger(__name__)

OPERATION = "lower"
REQUIRED_KEYS = ("a", "b")


def _validate(event: dict) -> tuple:
    if not isinstance(event, dict) or any(key not in event for key in REQUIRED_KEYS):
        raise ValidationError("Event must contain 'operation', 'a' and 'b'")
    return event["a"], event["b"]


def handle(event: dict) -> dict:
    logger.debug("handling %s event: %s", OPERATION, event)
    try:
        a, b = _validate(event)
        result = string_service.operate(OPERATION, a, b)
        response = build_response(200, {"operation": OPERATION, "result": result})
    except AppError as exc:
        logger.error("app error: %s", exc.message)
        response = build_response(exc.status_code, {"error": exc.message})
    except Exception:  # noqa: BLE001
        logger.exception("unexpected error")
        response = build_response(500, {"error": "Internal server error"})

    logger.debug("handler response: %s", response)
    return response


def _main():
    """Run this flow locally as a plain Python module.

    Usage:
        python3 src/handlers/lower.py [test/events/event-lower.json]
    """
    default_event = os.path.join(_PROJECT_ROOT, "test", "events", "event-lower.json")
    event_path = sys.argv[1] if len(sys.argv) > 1 else default_event
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)
    print(json.dumps(handle(event), indent=2))


if __name__ == "__main__":
    _main()
