"""OrderService unit tests (fakes only, no AWS/network)."""

import json
import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
for _path in (os.path.join(PROJECT_ROOT, "pip-modules"), PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from src.common.errors import NotFoundError, ValidationError
from src.local import FakeDynamoDB, FakeS3, FakeSecretsManager, FakeSecretServer
from src.services.order_service import OrderService


def build_service(dynamodb=None):
    return OrderService(
        dynamodb=dynamodb or FakeDynamoDB(),
        s3=FakeS3(),
        secrets_manager=FakeSecretsManager(),
        secret_server=FakeSecretServer(),
    )


class OrderServiceTest(unittest.TestCase):
    def test_create_order(self):
        dynamodb = FakeDynamoDB()
        s3 = FakeS3()
        service = OrderService(
            dynamodb=dynamodb,
            s3=s3,
            secrets_manager=FakeSecretsManager(),
            secret_server=FakeSecretServer(),
        )

        result = service.create_order(order_id="A1", customer="Sri", amount=99.5)

        self.assertEqual(result["order_id"], "A1")
        self.assertEqual(result["customer"], "Sri")
        self.assertEqual(result["amount"], 99.5)
        self.assertEqual(result["invoice_s3_key"], "invoices/A1.json")
        self.assertEqual(result["api_key_source"], "secret_server")
        self.assertEqual(result["db_user"], "admin")
        self.assertEqual(dynamodb.items["A1"]["customer"], "Sri")
        invoice = json.loads(s3.objects["invoices/A1.json"].decode("utf-8"))
        self.assertEqual(invoice, {"order_id": "A1", "customer": "Sri", "amount": 99.5})

    def test_create_order_rejects_non_numeric_amount(self):
        with self.assertRaises(ValidationError):
            build_service().create_order(order_id="A1", customer="Sri", amount="abc")

    def test_get_order_returns_item(self):
        dynamodb = FakeDynamoDB()
        dynamodb.put_item({"order_id": "A1", "customer": "Sri", "amount": 99.5})

        result = build_service(dynamodb).get_order("A1")

        self.assertEqual(result, {"order_id": "A1", "customer": "Sri", "amount": 99.5})

    def test_get_order_not_found(self):
        with self.assertRaises(NotFoundError) as ctx:
            build_service().get_order("missing")
        self.assertEqual(str(ctx.exception), "Order not found: missing")


if __name__ == "__main__":
    unittest.main()
