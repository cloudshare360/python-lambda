"""Handler for the div flow.

Runnable on its own:
    python3 src/handlers/div.py test/events/event-div.json
"""

import json
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PIP_MODULES = os.path.join(_PROJECT_ROOT, "pip-modules")
for _path in (_PIP_MODULES, _PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)
sys.pycache_prefix = os.path.join(_PIP_MODULES, ".pycache")

from src.common.errors import AppError, ValidationError
from src.common.logger import get_logger
from src.common.response import build_response
from src.handlers import MISSING_FIELDS_MESSAGE, has_missing_fields, json_number
from src.services import calc_service

logger = get_logger(__name__)


def handle(event):
    """Divide `a` by `b`, returning a Lambda proxy response."""
    logger.debug("handle div event=%s", event)
    try:
        if has_missing_fields(event):
            raise ValidationError(MISSING_FIELDS_MESSAGE)
        result = calc_service.operate("div", event["a"], event["b"])
        return build_response(200, {"operation": "div", "result": json_number(result)})
    except AppError as exc:
        logger.debug("handle div error=%s", exc.message)
        return build_response(exc.status_code, {"error": exc.message})


def _main():
    event_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(_PROJECT_ROOT, "test", "events", "event-div.json")
    )
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)
    print(json.dumps(handle(event), indent=2))


if __name__ == "__main__":
    _main()
