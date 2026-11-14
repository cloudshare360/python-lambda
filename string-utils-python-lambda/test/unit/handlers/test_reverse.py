import json
import os
import unittest

from src.handlers.reverse import handle

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
EVENTS_DIR = os.path.join(PROJECT_ROOT, "test", "events")


def load_event(name):
    with open(os.path.join(EVENTS_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class ReverseHandlerTest(unittest.TestCase):
    def test_reverse(self):
        response = handle(load_event("event-reverse.json"))
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {"operation": "reverse", "result": "olleh"},
        )


if __name__ == "__main__":
    unittest.main()
