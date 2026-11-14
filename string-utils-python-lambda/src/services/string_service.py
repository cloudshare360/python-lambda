"""Business logic for string operations.

The service knows nothing about HTTP or AWS. It maps a validated operation name
to a pure string transformation and raises `ValidationError` for unknown
operations.
"""

from src.common.logger import get_logger
from src.models.text_operation import TextOperation

logger = get_logger(__name__)


def _upper(a, b) -> str:
    return str(a).upper()


def _lower(a, b) -> str:
    return str(a).lower()


def _reverse(a, b) -> str:
    return str(a)[::-1]


def _concat(a, b) -> str:
    return str(a) + str(b)


_OPERATIONS = {
    TextOperation.UPPER: _upper,
    TextOperation.LOWER: _lower,
    TextOperation.REVERSE: _reverse,
    TextOperation.CONCAT: _concat,
}


def operate(operation: str, a, b) -> str:
    logger.debug("operate called: operation=%s a=%s b=%s", operation, a, b)
    op = TextOperation.from_str(operation)
    result = _OPERATIONS[op](a, b)
    logger.debug("operate result: %s", result)
    return result
