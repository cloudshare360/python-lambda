"""Typed application errors.

Each error carries an HTTP-ish `status_code` so the controller and handlers can
map it to a response without knowing implementation details.
"""


class AppError(Exception):
    """Base class for all application errors."""

    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class ValidationError(AppError):
    """Raised when the incoming event is missing or has invalid fields."""

    status_code = 400


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404


class IntegrationError(AppError):
    """Raised when an AWS or external REST call fails."""

    status_code = 502
