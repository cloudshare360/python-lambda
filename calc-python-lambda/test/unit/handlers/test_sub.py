"""sub flow: test/events/event-sub.json -> 200 {"operation": "sub", "result": 5}."""

import json
import unittest

from src.handlers import sub
from test import load_event


class TestSub(unittest.TestCase):
    def test_sub(self):
        event = load_event("event-sub.json")

        response = sub.handle(event)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {"operation": "sub", "result": 5},
        )


if __name__ == "__main__":
    unittest.main()
