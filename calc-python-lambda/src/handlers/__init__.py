"""Flow handlers package.

Each module handles exactly one calculator flow. Shared input validation and
JSON number presentation live here so all flows behave identically.
"""

REQUIRED_FIELDS = ("operation", "a", "b")
MISSING_FIELDS_MESSAGE = "Event must contain 'operation', 'a' and 'b'"


def has_missing_fields(event):
    """Return True when the event is not an object or lacks a required field."""
    if not isinstance(event, dict):
        return True
    return any(event.get(field) is None for field in REQUIRED_FIELDS)


def json_number(value):
    """Render an integral float as an int so results read as 15, not 15.0."""
    return int(value) if float(value).is_integer() else value
