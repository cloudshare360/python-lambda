"""div flow: test/events/event-div.json -> 200 {"operation": "div", "result": 2.5}."""

import json
import unittest

from src.handlers import div
from test import load_event


class TestDiv(unittest.TestCase):
    def test_div(self):
        event = load_event("event-div.json")

        response = div.handle(event)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {"operation": "div", "result": 2.5},
        )


if __name__ == "__main__":
    unittest.main()
