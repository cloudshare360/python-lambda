"""create-order flow: test/events/event-create-order.json."""

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

from src.handlers.create_order import handle
from src.local import build_local_service


def load_event(name):
    with open(os.path.join(PROJECT_ROOT, "test", "events", name), encoding="utf-8") as f:
        return json.load(f)


class CreateOrderHandlerTest(unittest.TestCase):
    def test_create_order(self):
        event = load_event("event-create-order.json")
        response = handle(event, build_local_service())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["order_id"], "A1")
        self.assertEqual(body["customer"], "Sri")
        self.assertEqual(body["amount"], 99.5)
        self.assertEqual(body["invoice_s3_key"], "invoices/A1.json")
        self.assertEqual(body["api_key_source"], "secret_server")
        self.assertEqual(body["db_user"], "admin")


if __name__ == "__main__":
    unittest.main()
