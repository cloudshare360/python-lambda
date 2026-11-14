"""AWS Lambda entry point and composition root.

`lambda_handler` is the controller/orchestrator. It validates the event shape,
routes `operation` to the matching flow handler, and returns the response. It
contains no business logic and makes no AWS or HTTP calls.
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIP_MODULES = os.path.join(PROJECT_ROOT, "pip-modules")
for _path in (PROJECT_ROOT, PIP_MODULES):
    if _path not in sys.path:
        sys.path.insert(0, _path)

sys.pycache_prefix = os.path.join(PIP_MODULES, ".pycache")

from src.common.errors import AppError, ValidationError
from src.common.logger import get_logger
from src.common.response import build_response
from src.config import settings
from src.handlers import concat, lower, reverse, upper

logger = get_logger(__name__)

REQUIRED_KEYS = ("operation", "a", "b")

_HANDLERS = {
    "upper": upper.handle,
    "lower": lower.handle,
    "reverse": reverse.handle,
    "concat": concat.handle,
}


def lambda_handler(event, context):
    request_id = getattr(context, "aws_request_id", None)
    logger.debug(
        "invocation start app=%s request_id=%s event=%s",
        settings.APP_NAME,
        request_id,
        event,
    )
    try:
        if not isinstance(event, dict) or any(key not in event for key in REQUIRED_KEYS):
            raise ValidationError("Event must contain 'operation', 'a' and 'b'")

        operation = event["operation"]
        handler = _HANDLERS.get(operation)
        if handler is None:
            raise ValidationError(f"Unsupported operation: {operation}")

        response = handler(event)
    except AppError as exc:
        logger.error("app error: %s", exc.message)
        response = build_response(exc.status_code, {"error": exc.message})
    except Exception:  # noqa: BLE001
        logger.exception("unexpected error")
        response = build_response(500, {"error": "Internal server error"})

    logger.debug("invocation response status=%s", response.get("statusCode"))
    return response


def _main():
    """Run the lambda locally as a plain Python file.

    Usage:
        python3 src/lambda_function.py [test/events/event-<case>.json]
    """
    event_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(PROJECT_ROOT, "test", "events", "event-upper.json")
    )
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)
    print(json.dumps(lambda_handler(event, None), indent=2))


if __name__ == "__main__":
    _main()
