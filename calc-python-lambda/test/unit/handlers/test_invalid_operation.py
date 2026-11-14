"""Unknown operation: test/events/event-invalid-operation.json -> 400 unsupported."""

import json
import unittest

from src.lambda_function import lambda_handler
from test import load_event


class TestInvalidOperation(unittest.TestCase):
    def test_invalid_operation(self):
        event = load_event("event-invalid-operation.json")

        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            json.loads(response["body"]),
            {"error": "Unsupported operation: mod"},
        )


if __name__ == "__main__":
    unittest.main()
