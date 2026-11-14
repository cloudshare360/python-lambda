"""AWS Lambda entry point and composition root.

`lambda_handler` is the controller/orchestrator. It only parses the event,
routes it to a flow handler, and returns the response. Real integration clients
are wired here in `build_service()` (lazy boto3) and injected into the service.

This file contains no business logic and makes no direct boto3/HTTP calls.
"""

import json
import os
import sys

# Make the project root and pip-modules importable both locally and on Lambda.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIP_MODULES = os.path.join(PROJECT_ROOT, "pip-modules")
for _path in (PIP_MODULES, PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Keep bytecode caches under pip-modules/.pycache so the source tree stays clean.
sys.pycache_prefix = os.path.join(PIP_MODULES, ".pycache")

from src.adapters.aws.dynamodb import DynamoDBClient
from src.adapters.aws.s3 import S3Service
from src.adapters.aws.secret_manager import SecretsManager
from src.adapters.external.secret_server.restapi.secrets import SecretServerClient
from src.common.errors import AppError, ValidationError
from src.common.logger import get_logger
from src.common.response import build_response
from src.config import settings
from src.handlers import create_order, get_order
from src.services.order_service import OrderService

logger = get_logger(__name__)

_HANDLERS = {
    "create-order": create_order.handle,
    "get-order": get_order.handle,
}


def build_service() -> OrderService:
    """Composition root: wire the real clients from settings."""
    return OrderService(
        dynamodb=DynamoDBClient(table_name=settings.TABLE_NAME),
        s3=S3Service(bucket=settings.BUCKET_NAME),
        secrets_manager=SecretsManager(),
        secret_server=SecretServerClient(
            base_url=settings.SECRET_SERVER_URL,
            token=settings.SECRET_SERVER_TOKEN,
        ),
    )


def lambda_handler(event, context, service=None):
    """Controller: log the invocation, route by operation, log the response."""
    request_id = getattr(context, "aws_request_id", None)
    logger.debug("lambda_handler invoked: event=%s request_id=%s", event, request_id)

    if service is None:
        service = build_service()

    try:
        if not isinstance(event, dict) or not event.get("operation"):
            raise ValidationError(
                "Event must contain 'operation', 'order_id', 'customer' and 'amount'"
            )
        handler = _HANDLERS.get(event["operation"])
        if handler is None:
            raise ValidationError(f"Unsupported operation: {event['operation']}")
        response = handler(event, service)
    except AppError as exc:
        response = build_response(exc.status_code, {"error": exc.message})

    logger.debug("lambda_handler response: status=%s", response.get("statusCode"))
    return response


def _main():
    """Run the lambda locally as a plain Python file, using in-memory fakes.

    Usage:
        python3 src/lambda_function.py [test/events/event-<case>.json]

    On AWS Lambda the real clients from `build_service()` are used; locally the
    fakes in `src/local.py` avoid any AWS credentials or network access.
    """
    from src.local import build_local_service

    event_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(PROJECT_ROOT, "test", "events", "event-create-order.json")
    )
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    print(json.dumps(lambda_handler(event, None, build_local_service()), indent=2))


if __name__ == "__main__":
    _main()
