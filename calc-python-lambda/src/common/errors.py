"""Typed application errors.

Each error carries the HTTP status the controller should return, so handlers can
map failures to responses without knowing implementation details.
"""


class AppError(Exception):
    """Base class for all application errors (HTTP 500)."""

    status_code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    """Raised when the event is missing fields or contains invalid values."""

    status_code = 400


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404


class IntegrationError(AppError):
    """Raised when an AWS or external dependency fails."""

    status_code = 502
