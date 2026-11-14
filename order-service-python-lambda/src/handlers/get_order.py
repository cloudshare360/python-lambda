"""Handler for the get-order flow.

Thin flow orchestrator: validates the event, calls the service, and maps
application errors to HTTP-shaped responses. No business rules, no AWS/HTTP.
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PIP_MODULES = os.path.join(PROJECT_ROOT, "pip-modules")
for _path in (PIP_MODULES, PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

sys.pycache_prefix = os.path.join(PIP_MODULES, ".pycache")

from src.common.errors import AppError, ValidationError
from src.common.response import build_response


def handle(event: dict, service) -> dict:
    try:
        if not isinstance(event, dict):
            raise ValidationError("Event must be a JSON object")
        if event.get("operation") != "get-order":
            if not event.get("operation"):
                raise ValidationError("Event must contain 'operation' and 'order_id'")
            raise ValidationError(f"Unsupported operation: {event['operation']}")
        if event.get("order_id") is None:
            raise ValidationError("Event must contain 'operation' and 'order_id'")

        result = service.get_order(order_id=event["order_id"])
        return build_response(200, result)
    except AppError as exc:
        return build_response(exc.status_code, {"error": exc.message})


def _main():
    from src.local import build_local_service

    event_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(PROJECT_ROOT, "test", "events", "event-get-order.json")
    )
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)
    print(json.dumps(handle(event, build_local_service()), indent=2))


if __name__ == "__main__":
    _main()
