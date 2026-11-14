"""Environment-driven settings.

All values are read from environment variables. No credentials or secrets are
hard-coded here; sensitive values live in AWS Secrets Manager / the external
secret server and are fetched at runtime by the integration layer.
"""

import os


def _get(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


AWS_REGION = _get("AWS_REGION", "us-east-1")
TABLE_NAME = _get("TABLE_NAME", "orders")
BUCKET_NAME = _get("BUCKET_NAME", "order-invoices")
SECRET_SERVER_URL = _get("SECRET_SERVER_URL", "http://localhost:8080")
SECRET_SERVER_TOKEN = _get("SECRET_SERVER_TOKEN", "")
