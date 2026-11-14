"""DynamoDB adapter.

Wraps exactly one DynamoDB table. boto3 is imported lazily so the module is
importable (and testable with an injected client) without AWS credentials.
"""

import logging

from src.common.errors import IntegrationError
from src.config import settings

logger = logging.getLogger(__name__)


class DynamoDBClient:
    def __init__(self, table_name: str | None = None, client=None):
        self.table_name = table_name or settings.TABLE_NAME
        self._client = client
        self._table = None

    def _get_table(self):
        if self._client is not None:
            return self._client
        if self._table is None:
            import boto3

            resource = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
            self._table = resource.Table(self.table_name)
        return self._table

    def put_item(self, item: dict) -> None:
        logger.debug("DynamoDBClient.put_item table=%s item=%s", self.table_name, item)
        try:
            self._get_table().put_item(Item=item)
        except Exception as exc:
            raise IntegrationError(f"DynamoDB put_item failed: {exc}") from exc

    def get_item(self, key: dict) -> dict | None:
        logger.debug("DynamoDBClient.get_item table=%s key=%s", self.table_name, key)
        try:
            response = self._get_table().get_item(Key=key)
        except Exception as exc:
            raise IntegrationError(f"DynamoDB get_item failed: {exc}") from exc
        return response.get("Item")
