# order-service-python-lambda

A reference AWS Lambda project for an **order service**, built on **MVC +
hexagonal (ports & adapters)** as described in
[`python-lambda-mvc-agent.md`](../python-lambda-mvc-agent.md).

It demonstrates:

- **AWS integrations:** DynamoDB, S3 and Secrets Manager (lazy boto3 clients).
- **External REST API:** a "secret server" vendor client on stdlib `urllib`.
- **Full local testability:** every flow runs locally with in-memory fakes — **no
  AWS credentials and no network access** required.

## Overview

`src/lambda_function.py` is the entry point, controller and composition root. It
parses the event, routes by `operation` to a flow handler in `src/handlers/`, and
returns the response. Business logic lives in `src/services/`; all AWS/HTTP work
lives in `src/adapters/`. Real clients are wired once in `build_service()` and
injected inward.

### Operations

| Operation | Event | Result |
| --- | --- | --- |
| `create-order` | `{"operation":"create-order","order_id":"A1","customer":"Sri","amount":99.5}` | Fetches an API key from the secret server, DB creds from Secrets Manager, writes the order to DynamoDB, stores an invoice JSON in S3, and returns a summary. |
| `get-order` | `{"operation":"get-order","order_id":"A1"}` | Returns the stored order, or `404` `{"error":"Order not found: <id>"}`. |

### Errors

| Case | Status | Body |
| --- | --- | --- |
| Missing required fields | `400` | `{"error":"Event must contain 'operation', 'order_id', 'customer' and 'amount'"}` |
| Unknown operation | `400` | `{"error":"Unsupported operation: <op>"}` |
| Order not found | `404` | `{"error":"Order not found: <id>"}` |
| AWS/REST failure | `502` | `{"error":"<integration message>"}` |

## Folder structure

```
order-service-python-lambda/
├── requirements.txt                    # stdlib only (boto3 is provided by Lambda)
├── README.md
├── src/
│   ├── __init__.py
│   ├── lambda_function.py              # ENTRY / controller / composition root
│   ├── local.py                        # in-memory fakes + build_local_service()
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                 # env-driven settings (no secrets)
│   ├── common/
│   │   ├── __init__.py
│   │   ├── logger.py                   # get_logger()
│   │   ├── errors.py                   # AppError / ValidationError(400) / NotFoundError(404) / IntegrationError(502)
│   │   └── response.py                 # build_response(status, body)  [VIEW]
│   ├── handlers/                       # one module per flow
│   │   ├── __init__.py
│   │   ├── create_order.py             # handle(event, service) + local __main__
│   │   └── get_order.py                # handle(event, service) + local __main__
│   ├── services/
│   │   ├── __init__.py
│   │   └── order_service.py            # business logic (no boto3/HTTP)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── aws/
│   │   │   ├── __init__.py
│   │   │   ├── dynamodb.py             # DynamoDBClient (lazy boto3)
│   │   │   ├── s3.py                   # S3Service (lazy boto3)
│   │   │   └── secret_manager.py       # SecretsManager (lazy boto3)
│   │   └── external/
│   │       ├── __init__.py
│   │       └── secret_server/
│   │           ├── __init__.py
│   │           └── restapi/
│   │               ├── __init__.py
│   │               ├── client.py       # RestClient (urllib, timeout+retry, injectable transport)
│   │               └── secrets.py      # SecretServerClient (get/create/rotate)
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── order_repository.py         # OrderRepository over DynamoDBClient
│   └── models/
│       ├── __init__.py
│       └── order.py                    # @dataclass Order (from_dict/to_dict)
├── test/
│   ├── __init__.py
│   ├── run_all.py                      # runs all unit tests as a python file
│   ├── README.md
│   ├── events/                         # one JSON per test case
│   │   ├── README.md
│   │   ├── event-create-order.json
│   │   ├── event-get-order.json
│   │   ├── event-invalid-operation.json
│   │   └── event-missing-field.json
│   └── unit/                           # mirrors src/
│       ├── __init__.py
│       ├── handlers/
│       │   ├── test_create_order.py
│       │   ├── test_get_order.py
│       │   ├── test_invalid_operation.py
│       │   └── test_missing_field.py
│       ├── services/
│       │   └── test_order_service.py
│       └── adapters/
│           ├── aws/test_dynamodb.py
│           └── external/test_secrets.py
├── pip-modules/                        # third-party deps / layer source
│   └── README.md
└── infra/                              # SAM / CDK
    └── README.md
```

## Layers

| Layer | Location | Responsibility |
| --- | --- | --- |
| Controller | `src/lambda_function.py` | Parse event, route by operation, return response |
| Handler | `src/handlers/` | Flow-specific validation + service call |
| Service | `src/services/` | Business logic |
| Repository | `src/repositories/` | Item ↔ model mapping over adapters |
| Adapter | `src/adapters/aws`, `src/adapters/external` | Wrap one AWS service or REST resource |
| Model | `src/models/` | Dataclasses/enums |
| View | `src/common/response.py` | JSON serialization |
| Config | `src/config/settings.py` | Env-driven settings |

Dependencies point inward only. Services never import adapters or boto3.

## Event format

```json
{ "operation": "create-order", "order_id": "A1", "customer": "Sri", "amount": 99.5 }
```

```json
{ "operation": "get-order", "order_id": "A1" }
```

## Run locally

The Lambda is directly runnable as a plain Python file. Local runs use the
in-memory fakes in `src/local.py`; no AWS credentials or network are required.

```bash
cd order-service-python-lambda

# default test/events/event-create-order.json
python3 src/lambda_function.py

# a specific event case
python3 src/lambda_function.py test/events/event-create-order.json
python3 src/lambda_function.py test/events/event-get-order.json
```

Run one flow on its own:

```bash
python3 src/handlers/create_order.py test/events/event-create-order.json
python3 src/handlers/get_order.py test/events/event-get-order.json
```

## Unit tests

```bash
cd order-service-python-lambda
python3 test/run_all.py
```

`test/run_all.py` adds the project root, `src/` and `pip-modules/` to
`sys.path`, discovers every test under `test/unit/`, and exits non-zero on
failure. Tests inject fakes for AWS and REST clients and make **no AWS calls and
no network calls**.

Event files and tests share the same `<case>` token
(`test/events/event-<case>.json` ↔ `test/unit/.../test_<case>.py`). See
[test/events/README.md](test/events/README.md) for the full mapping.

## Adding a flow

1. Add the business method to `src/services/order_service.py`.
2. Add `src/handlers/<flow>.py` with `handle(event, service)` and a `__main__`.
3. Register the operation in `_HANDLERS` in `src/lambda_function.py`.
4. Add `test/events/event-<case>.json`, `test/unit/handlers/test_<case>.py`, and
   update `test/events/README.md`.

## pip-modules

`pip-modules/` holds third-party dependencies (like `node_modules`) and is the
source for a Lambda Layer. Both `src/lambda_function.py` and `test/run_all.py`
add the project root, `src/` and `pip-modules/` to `sys.path`, and bytecode
caches are kept in `pip-modules/.pycache`.

```bash
pip3 install <package> -t order-service-python-lambda/pip-modules
```

`boto3` is provided by the Lambda runtime and must **not** be bundled here. This
project otherwise uses only the Python standard library.

## Invoke & Test from AWS Console

Once deployed, test the function without local setup.

### AWS Console

1. Open the function in the [Lambda Console](https://console.aws.amazon.com/lambda/)
2. Go to **Test** tab → **Create new event**
3. Paste an event, e.g. `{"operation":"create-order","order_id":"A1","customer":"Sri","amount":99.5}`
4. Click **Test** — response and logs appear under *Execution results*

### AWS CLI

```bash
aws lambda invoke \
  --function-name order-service-python-lambda \
  --payload '{"operation":"create-order","order_id":"A1","customer":"Sri","amount":99.5}' \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

### Expected response (create-order)

```json
{
  "statusCode": 200,
  "headers": { "Content-Type": "application/json" },
  "body": "{\"operation\": \"create-order\", \"order_id\": \"A1\", \"status\": \"created\", \"invoice\": \"<s3-url>\"}"
}
```

Error cases: 400 with `{"error": "..."}`, 404 with `{"error": "Order not found: <id>"}`, 502 with `{"error": "<integration message>"}`.

### Console test events

| Operation | Test event |
|-----------|-----------|
| create-order | `{"operation":"create-order","order_id":"A1","customer":"Sri","amount":99.5}` |
| get-order | `{"operation":"get-order","order_id":"A1"}` |
| unknown operation | `{"operation":"pow","order_id":"A1"}` |
| missing fields | `{"operation":"create-order"}` |

Logs: **Monitor** tab → **View CloudWatch logs** → log group `/aws/lambda/order-service-python-lambda`.

## Deployment

- **Handler:** `src.lambda_function.lambda_handler`
- **Package:** zip `src/` and `pip-modules/` at the root (exclude `test/`,
  `infra/`, `README.md`):

  ```bash
  cd order-service-python-lambda
  zip -r ../order-service.zip src pip-modules
  ```

- **Layer:** zip `pip-modules/` contents under `python/`.
- **Runtime:** Python 3.13/3.12, architecture `arm64`/`x86_64`, memory 128 MB.
- **Environment variables:** `AWS_REGION`, `TABLE_NAME`, `BUCKET_NAME`,
  `SECRET_SERVER_URL`, `SECRET_SERVER_TOKEN`. DB credentials live in Secrets
  Manager (`db-creds`); the external API key lives in the secret server
  (`external-api-key`). No secrets are hard-coded.
- **IAM:** least-privilege — `dynamodb:PutItem`/`GetItem` on the table,
  `s3:PutObject`/`GetObject` on the bucket, and
  `secretsmanager:GetSecretValue` on the DB secret.
