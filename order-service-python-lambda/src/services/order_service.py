"""Business orchestration for the order service.

`OrderService` owns the business logic: it coordinates DynamoDB, S3, AWS
Secrets Manager and the external secret server. It holds no AWS/HTTP client
creation of its own - all collaborators are injected at the composition root.

No boto3 and no HTTP libraries are imported here.
"""

import json
import logging

from src.common.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, dynamodb, s3, secrets_manager, secret_server):
        self.dynamodb = dynamodb
        self.s3 = s3
        self.secrets_manager = secrets_manager
        self.secret_server = secret_server

    def create_order(self, order_id: str, customer: str, amount) -> dict:
        logger.debug(
            "create_order order_id=%s customer=%s amount=%s", order_id, customer, amount
        )
        try:
            amount = float(amount)
        except (TypeError, ValueError) as exc:
            raise ValidationError("'amount' must be a number") from exc

        api_key = self.secret_server.get_secret("external-api-key")["api_key"]
        db_user = self.secrets_manager.get_secret("db-creds")["username"]
        logger.debug("create_order api_key resolved=%s db_user=%s", bool(api_key), db_user)

        self.dynamodb.put_item(
            {"order_id": order_id, "customer": customer, "amount": amount}
        )

        invoice = {"order_id": order_id, "customer": customer, "amount": amount}
        invoice_key = f"invoices/{order_id}.json"
        self.s3.put_object(invoice_key, json.dumps(invoice).encode("utf-8"))
        logger.debug("create_order invoice stored at %s", invoice_key)

        return {
            "order_id": order_id,
            "customer": customer,
            "amount": amount,
            "invoice_s3_key": invoice_key,
            "api_key_source": "secret_server",
            "db_user": db_user,
        }

    def get_order(self, order_id: str) -> dict:
        logger.debug("get_order order_id=%s", order_id)
        item = self.dynamodb.get_item({"order_id": order_id})
        if item is None:
            raise NotFoundError(f"Order not found: {order_id}")
        return item
