"""Secret server REST resource client.

One class per vendor resource, with one method per operation. All transport
concerns live in `RestClient`; this class only maps operations to paths.
"""

import logging

from src.adapters.external.secret_server.restapi.client import RestClient
from src.config import settings

logger = logging.getLogger(__name__)


class SecretServerClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, client=None):
        self.client = client or RestClient(
            base_url or settings.SECRET_SERVER_URL,
            token=token if token is not None else settings.SECRET_SERVER_TOKEN,
        )

    def get_secret(self, secret_id: str) -> dict:
        logger.debug("SecretServerClient.get_secret secret_id=%s", secret_id)
        return self.client.request("GET", f"/secrets/{secret_id}")

    def create_secret(self, payload: dict) -> dict:
        logger.debug("SecretServerClient.create_secret keys=%s", sorted(payload))
        return self.client.request("POST", "/secrets", payload)

    def rotate_secret(self, secret_id: str) -> dict:
        logger.debug("SecretServerClient.rotate_secret secret_id=%s", secret_id)
        return self.client.request("POST", f"/secrets/{secret_id}/rotate")
