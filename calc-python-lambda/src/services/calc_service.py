"""Calculator business logic.

The service knows the arithmetic rules and the operation model. It does not
know about Lambda, HTTP, or any I/O.
"""

from src.common.errors import ValidationError
from src.common.logger import get_logger
from src.models.operation import Operation

logger = get_logger(__name__)


def operate(operation, a, b):
    """Apply `operation` to `a` and `b`, returning the result as a float."""
    op = Operation.from_str(operation)
    try:
        a = float(a)
        b = float(b)
    except (TypeError, ValueError) as exc:
        raise ValidationError("'a' and 'b' must be numbers") from exc

    logger.debug("operate operation=%s a=%s b=%s", op.value, a, b)

    if op is Operation.ADD:
        return a + b
    if op is Operation.SUB:
        return a - b
    if op is Operation.MUL:
        return a * b

    try:
        return a / b
    except ZeroDivisionError as exc:
        logger.debug("operate divide by zero operation=%s", op.value)
        raise ValidationError("Cannot divide by zero") from exc
