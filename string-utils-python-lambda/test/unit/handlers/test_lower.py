import json
import os
import unittest

from src.handlers.lower import handle

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
EVENTS_DIR = os.path.join(PROJECT_ROOT, "test", "events")


def load_event(name):
    with open(os.path.join(EVENTS_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class LowerHandlerTest(unittest.TestCase):
    def test_lower(self):
        response = handle(load_event("event-lower.json"))
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {"operation": "lower", "result": "hello"},
        )


if __name__ == "__main__":
    unittest.main()
