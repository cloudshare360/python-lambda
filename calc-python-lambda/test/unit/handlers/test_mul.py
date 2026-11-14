"""mul flow: test/events/event-mul.json -> 200 {"operation": "mul", "result": 50}."""

import json
import unittest

from src.handlers import mul
from test import load_event


class TestMul(unittest.TestCase):
    def test_mul(self):
        event = load_event("event-mul.json")

        response = mul.handle(event)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {"operation": "mul", "result": 50},
        )


if __name__ == "__main__":
    unittest.main()
