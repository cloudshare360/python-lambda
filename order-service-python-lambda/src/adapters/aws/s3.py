"""S3 adapter.

Wraps exactly one bucket. boto3 is imported lazily so the module is importable
(and testable with an injected client) without AWS credentials.
"""

import logging

from src.common.errors import IntegrationError
from src.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self, bucket: str | None = None, client=None):
        self.bucket = bucket or settings.BUCKET_NAME
        self._client = client
        self._s3 = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if self._s3 is None:
            import boto3

            self._s3 = boto3.client("s3", region_name=settings.AWS_REGION)
        return self._s3

    def put_object(self, key: str, body: bytes) -> None:
        logger.debug("S3Service.put_object bucket=%s key=%s", self.bucket, key)
        try:
            self._get_client().put_object(Bucket=self.bucket, Key=key, Body=body)
        except Exception as exc:
            raise IntegrationError(f"S3 put_object failed for {key}: {exc}") from exc

    def get_object(self, key: str) -> bytes:
        logger.debug("S3Service.get_object bucket=%s key=%s", self.bucket, key)
        try:
            response = self._get_client().get_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            raise IntegrationError(f"S3 get_object failed for {key}: {exc}") from exc
        return response["Body"].read()
