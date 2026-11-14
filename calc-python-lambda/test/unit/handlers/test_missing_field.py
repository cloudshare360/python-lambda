"""Missing field: test/events/event-missing-field.json -> 400 missing-keys error."""

import json
import unittest

from src.lambda_function import lambda_handler
from test import load_event

MISSING_FIELDS_ERROR = "Event must contain 'operation', 'a' and 'b'"


class TestMissingField(unittest.TestCase):
    def test_missing_field(self):
        event = load_event("event-missing-field.json")

        response = lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            json.loads(response["body"]),
            {"error": MISSING_FIELDS_ERROR},
        )


if __name__ == "__main__":
    unittest.main()
