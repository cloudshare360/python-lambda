"""Environment-driven settings (no secrets, no hard-coded credentials)."""

import os

APP_NAME = os.getenv("APP_NAME", "string-utils-python-lambda")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
