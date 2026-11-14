import json
import os
import unittest

from src.lambda_function import lambda_handler

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
EVENTS_DIR = os.path.join(PROJECT_ROOT, "test", "events")


def load_event(name):
    with open(os.path.join(EVENTS_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class InvalidOperationTest(unittest.TestCase):
    def test_invalid_operation(self):
        response = lambda_handler(load_event("event-invalid-operation.json"), None)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            json.loads(response["body"]),
            {"error": "Unsupported operation: capitalize"},
        )


if __name__ == "__main__":
    unittest.main()
