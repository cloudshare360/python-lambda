"""Domain model: the supported text operations."""

from enum import Enum

from src.common.errors import ValidationError


class TextOperation(Enum):
    UPPER = "upper"
    LOWER = "lower"
    REVERSE = "reverse"
    CONCAT = "concat"

    @classmethod
    def from_str(cls, value: str) -> "TextOperation":
        for member in cls:
            if member.value == value:
                return member
        raise ValidationError(f"Unsupported operation: {value}")
