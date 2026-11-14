"""Calculator operation model."""

from enum import Enum

from src.common.errors import ValidationError


class Operation(Enum):
    """Supported calculator operations."""

    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"

    @classmethod
    def from_str(cls, value):
        """Resolve an operation name, or raise a ValidationError."""
        for member in cls:
            if member.value == value:
                return member
        raise ValidationError(f"Unsupported operation: {value}")
