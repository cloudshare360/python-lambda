"""add flow: test/events/event-add.json -> 200 {"operation": "add", "result": 15}."""

import json
import unittest

from src.handlers import add
from test import load_event


class TestAdd(unittest.TestCase):
    def test_add(self):
        event = load_event("event-add.json")

        response = add.handle(event)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {"operation": "add", "result": 15},
        )


if __name__ == "__main__":
    unittest.main()
