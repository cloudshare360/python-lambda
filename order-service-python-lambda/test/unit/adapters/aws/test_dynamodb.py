"""DynamoDBClient unit tests (injected fake table, no AWS)."""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
for _path in (os.path.join(PROJECT_ROOT, "pip-modules"), PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from src.adapters.aws.dynamodb import DynamoDBClient
from src.common.errors import IntegrationError


class FakeTable:
    def __init__(self):
        self.items = {}
        self.put_calls = []
        self.get_calls = []

    def put_item(self, Item):
        self.put_calls.append(Item)
        self.items[Item["order_id"]] = dict(Item)

    def get_item(self, Key):
        self.get_calls.append(Key)
        item = self.items.get(Key["order_id"])
        return {"Item": item} if item is not None else {}


class DynamoDBClientTest(unittest.TestCase):
    def test_put_item(self):
        table = FakeTable()
        client = DynamoDBClient(table_name="orders", client=table)

        client.put_item({"order_id": "A1", "customer": "Sri", "amount": 99.5})

        self.assertEqual(table.put_calls, [{"order_id": "A1", "customer": "Sri", "amount": 99.5}])

    def test_get_item_found_and_missing(self):
        table = FakeTable()
        table.items["A1"] = {"order_id": "A1"}
        client = DynamoDBClient(table_name="orders", client=table)

        self.assertEqual(client.get_item({"order_id": "A1"}), {"order_id": "A1"})
        self.assertIsNone(client.get_item({"order_id": "NOPE"}))
        self.assertEqual(table.get_calls, [{"order_id": "A1"}, {"order_id": "NOPE"}])

    def test_errors_map_to_integration_error(self):
        class BrokenTable:
            def put_item(self, **kwargs):
                raise RuntimeError("boom")

        client = DynamoDBClient(table_name="orders", client=BrokenTable())
        with self.assertRaises(IntegrationError):
            client.put_item({"order_id": "A1"})


if __name__ == "__main__":
    unittest.main()
