# test/

Unit tests for the order-service Lambda. Every test runs with in-memory fakes —
**no AWS credentials and no network access**.

## Prerequisites

- Python 3.11+ (developed on 3.13).
- Standard library only. `boto3` is not needed for tests.

## Layout

```
test/
├── __init__.py
├── run_all.py          # runs all unit tests, exits non-zero on failure
├── events/             # one JSON event per test case (+ mapping README)
└── unit/               # mirrors src/
    ├── handlers/       # one test per flow/error case
    ├── services/       # OrderService with injected fakes
    └── adapters/
        ├── aws/        # DynamoDBClient with an injected fake table
        └── external/   # SecretServerClient + RestClient with injected transport
```

Each test file loads its matching `test/events/event-<case>.json` by the same
`<case>` token and asserts both `statusCode` and the decoded `body`.

## Event ↔ test mapping

| Event file | Test file | Flow | Expected |
| --- | --- | --- | --- |
| `events/event-create-order.json` | `unit/handlers/test_create_order.py` | `create-order` | `200` + `order_id`, `customer`, `amount`, `invoice_s3_key`, `api_key_source`, `db_user` |
| `events/event-get-order.json` | `unit/handlers/test_get_order.py` | `get-order` | `200` + seeded order `A1` |
| `events/event-invalid-operation.json` | `unit/handlers/test_invalid_operation.py` | any | `400` `{"error":"Unsupported operation: delete-order"}` |
| `events/event-missing-field.json` | `unit/handlers/test_missing_field.py` | `create-order` | `400` `{"error":"Event must contain 'operation', 'order_id', 'customer' and 'amount'"}` |

## Run all

```bash
cd order-service-python-lambda
python3 test/run_all.py
```

Expected: `Ran 17 tests ... OK` and exit code `0`.

## Run a single test module

```bash
python3 -m unittest test.unit.handlers.test_create_order -v
python3 -m unittest test.unit.services.test_order_service -v
python3 -m unittest test.unit.adapters.aws.test_dynamodb -v
python3 -m unittest test.unit.adapters.external.test_secrets -v
```

## Per-case local runs (same fakes)

```bash
python3 src/lambda_function.py test/events/event-create-order.json
python3 src/lambda_function.py test/events/event-get-order.json
python3 src/handlers/create_order.py test/events/event-create-order.json
python3 src/handlers/get_order.py test/events/event-get-order.json
```

## Call chain

```
lambda_function.lambda_handler(event, context, service)
  → handlers.<flow>.handle(event, service)
    → services.order_service.OrderService.<method>
      → adapters.aws.dynamodb / s3 / secret_manager
      → adapters.external.secret_server.restapi.secrets
```

`src/local.py` supplies `FakeDynamoDB`, `FakeS3`, `FakeSecretsManager` and
`FakeSecretServer`; `build_local_service()` wires them and seeds order `A1`.

## Error cases

| Case | Status | Body |
| --- | --- | --- |
| Missing required fields | `400` | `{"error":"Event must contain 'operation', 'order_id', 'customer' and 'amount'"}` |
| Unknown operation | `400` | `{"error":"Unsupported operation: <op>"}` |
| Missing `order_id` for `get-order` | `400` | `{"error":"Event must contain 'operation' and 'order_id'"}` |
| Order not found | `404` | `{"error":"Order not found: <id>"}` |
| AWS/REST integration failure | `502` | `{"error":"<message>"}` |

## CloudWatch

On Lambda, DEBUG logs from the controller, handlers, service and adapters go to
`/aws/lambda/<function-name>`. Locally the same lines print to the terminal.

## Troubleshooting

- `ModuleNotFoundError: src...` — run from the project root (`order-service-python-lambda/`).
- Tests cannot be discovered — ensure `test/__init__.py` and every `test/unit/**/__init__.py` exist.
- `No module named boto3` — tests never need boto3; the adapters import it lazily only on real AWS runs.
