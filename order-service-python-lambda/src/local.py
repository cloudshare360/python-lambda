"""Local development adapters.

In-memory fakes for every AWS/REST integration so the Lambda can be executed
locally as a plain Python file (no AWS credentials, no network).

Used by:
- `src/lambda_function.py` when run directly (`python3 src/lambda_function.py`)
- `src/handlers/<flow>.__main__` (`python3 src/handlers/create_order.py ...`)
- `test/unit/` tests

For local/dev use only. On AWS Lambda the real clients built in
`lambda_function.build_service()` are used instead.
"""

from src.services.order_service import OrderService


class FakeDynamoDB:
    def __init__(self):
        self.items = {}

    def put_item(self, item):
        self.items[item["order_id"]] = dict(item)

    def get_item(self, key):
        return self.items.get(key["order_id"])


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, key, body):
        self.objects[key] = body

    def get_object(self, key):
        return self.objects[key]


class FakeSecretsManager:
    def __init__(self, secrets=None):
        self._secrets = secrets or {"db-creds": {"username": "admin"}}

    def get_secret(self, secret_id):
        return self._secrets[secret_id]


class FakeSecretServer:
    def __init__(self, secret=None):
        self._secret = secret or {"api_key": "local-test-key"}

    def get_secret(self, secret_id):
        return self._secret

    def create_secret(self, payload):
        return payload

    def rotate_secret(self, secret_id):
        return self._secret


def build_local_service() -> OrderService:
    """Build an OrderService backed entirely by in-memory fakes."""
    dynamodb = FakeDynamoDB()
    # Seed a demo order so get-order returns something when run standalone.
    dynamodb.put_item({"order_id": "A1", "customer": "Sri", "amount": 99.5})
    return OrderService(
        dynamodb=dynamodb,
        s3=FakeS3(),
        secrets_manager=FakeSecretsManager(),
        secret_server=FakeSecretServer(),
    )
