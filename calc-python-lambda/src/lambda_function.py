"""AWS Lambda entry point and composition root.

`lambda_handler` is the controller: it parses the event, routes by
`event["operation"]` to the matching flow handler, and returns the response.
It contains no arithmetic logic and makes no I/O calls.

Runnable locally as a plain Python file:
    python3 src/lambda_function.py [test/events/event-<case>.json]
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIP_MODULES = os.path.join(PROJECT_ROOT, "pip-modules")
for _path in (PIP_MODULES, PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Keep bytecode caches under pip-modules/.pycache so the source tree stays clean.
sys.pycache_prefix = os.path.join(PIP_MODULES, ".pycache")

from src.common.errors import AppError, ValidationError
from src.common.logger import get_logger
from src.common.response import build_response
from src.handlers import MISSING_FIELDS_MESSAGE, add, div, has_missing_fields, mul, sub

logger = get_logger(__name__)

_HANDLERS = {
    "add": add.handle,
    "sub": sub.handle,
    "mul": mul.handle,
    "div": div.handle,
}


def lambda_handler(event, context):
    """Controller: validate, route to one flow handler, and return its response."""
    request_id = getattr(context, "aws_request_id", None)
    logger.debug("invocation start request_id=%s event=%s", request_id, event)

    try:
        if has_missing_fields(event):
            raise ValidationError(MISSING_FIELDS_MESSAGE)

        operation = event["operation"]
        handler = _HANDLERS.get(operation) if isinstance(operation, str) else None
        if handler is None:
            raise ValidationError(f"Unsupported operation: {operation}")

        logger.debug("routing operation=%s", operation)
        response = handler(event)
    except AppError as exc:
        logger.debug("invocation error=%s", exc.message)
        response = build_response(exc.status_code, {"error": exc.message})

    logger.debug("invocation response status=%s", response.get("statusCode"))
    return response


def _main():
    event_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(PROJECT_ROOT, "test", "events", "event-add.json")
    )
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)
    print(json.dumps(lambda_handler(event, None), indent=2))


if __name__ == "__main__":
    _main()
