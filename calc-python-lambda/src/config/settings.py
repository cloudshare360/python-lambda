"""Environment-driven settings.

Every value is read from the environment. This project has no secrets and no
external integrations, so there are no credentials to configure.
"""

import os


class Settings:
    """Runtime settings resolved from environment variables."""

    def __init__(self):
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


settings = Settings()
