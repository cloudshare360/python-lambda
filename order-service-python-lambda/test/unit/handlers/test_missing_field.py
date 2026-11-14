"""Missing required field: test/events/event-missing-field.json."""

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


class MissingFieldTest(unittest.TestCase):
    def test_missing_field(self):
        event = load_event("event-missing-field.json")
        self.assertNotIn("amount", event)

        response = handle(event, build_local_service())

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            json.loads(response["body"]),
            {
                "error": "Event must contain 'operation', 'order_id', 'customer' and 'amount'"
            },
        )


if __name__ == "__main__":
    unittest.main()
