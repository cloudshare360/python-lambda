"""get-order flow: test/events/event-get-order.json."""

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

from src.handlers.get_order import handle
from src.local import build_local_service


def load_event(name):
    with open(os.path.join(PROJECT_ROOT, "test", "events", name), encoding="utf-8") as f:
        return json.load(f)


class GetOrderHandlerTest(unittest.TestCase):
    def test_get_order(self):
        event = load_event("event-get-order.json")
        response = handle(event, build_local_service())

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["order_id"], "A1")
        self.assertEqual(body["customer"], "Sri")
        self.assertEqual(body["amount"], 99.5)


if __name__ == "__main__":
    unittest.main()
