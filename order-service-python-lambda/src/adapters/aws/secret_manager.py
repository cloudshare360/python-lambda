"""AWS Secrets Manager adapter.

Fetches one secret by id and returns it as a parsed dict. boto3 is imported
lazily so the module is importable (and testable with an injected client)
without AWS credentials.
"""

import base64
import json
import logging

from src.common.errors import IntegrationError
from src.config import settings

logger = logging.getLogger(__name__)


class SecretsManager:
    def __init__(self, client=None):
        self._client = client
        self._secrets_manager = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if self._secrets_manager is None:
            import boto3

            self._secrets_manager = boto3.client(
                "secretsmanager", region_name=settings.AWS_REGION
            )
        return self._secrets_manager

    def get_secret(self, secret_id: str) -> dict:
        logger.debug("SecretsManager.get_secret secret_id=%s", secret_id)
        try:
            response = self._get_client().get_secret_value(SecretId=secret_id)
        except Exception as exc:
            raise IntegrationError(f"Secrets Manager get_secret failed: {exc}") from exc

        payload = response.get("SecretString")
        if payload is None:
            payload = base64.b64decode(response["SecretBinary"]).decode("utf-8")
        return json.loads(payload)
