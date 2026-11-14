"""div by zero: test/events/event-div-zero.json -> 400 {"error": "Cannot divide by zero"}."""

import json
import unittest

from src.handlers import div
from test import load_event


class TestDivZero(unittest.TestCase):
    def test_div_zero(self):
        event = load_event("event-div-zero.json")

        response = div.handle(event)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            json.loads(response["body"]),
            {"error": "Cannot divide by zero"},
        )


if __name__ == "__main__":
    unittest.main()
