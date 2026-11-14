# calc-python-lambda

A testability-first Python AWS Lambda for a four-operation calculator
(`add`, `sub`, `mul`, `div`), structured with MVC + hexagonal (ports & adapters)
layers. The Lambda is a thin controller; arithmetic lives in a service; every
flow is runnable and testable without AWS.

## Folder structure

```
calc-python-lambda/
├── README.md
├── requirements.txt                 # stdlib only
├── src/
│   ├── __init__.py
│   ├── lambda_function.py           # ENTRY: controller + composition root
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # env-driven settings
│   ├── common/
│   │   ├── __init__.py
│   │   ├── logger.py                # get_logger()
│   │   ├── errors.py                # AppError hierarchy
│   │   └── response.py              # build_response()  [VIEW]
│   ├── handlers/                    # one module per flow
│   │   ├── __init__.py
│   │   ├── add.py
│   │   ├── sub.py
│   │   ├── mul.py
│   │   └── div.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── calc_service.py          # business logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── operation.py             # Operation enum + from_str()
│   └── adapters/
│       └── __init__.py              # no AWS/external I/O in this app
├── test/
│   ├── __init__.py                  # load_event() helper
│   ├── run_all.py                   # run all unit tests
│   ├── README.md
│   ├── events/                      # one JSON per case + mapping table
│   └── unit/                        # mirrors src/; one test per case
├── pip-modules/
│   └── README.md                    # pip deps / Lambda Layer source
└── infra/
    └── README.md                    # SAM / CDK notes
```

There is no `repositories/` or `adapters/aws` in this app because the calculator
has no persistence or external calls. The package boundaries are in place so
they can be added without moving existing code.

## Layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Controller | `src/lambda_function.py` | Validate the event, route `event["operation"]`, return the response |
| Handler | `src/handlers/<flow>.py` | One flow: validate input, call the service, build the response |
| Service | `src/services/calc_service.py` | Arithmetic rules and domain errors |
| Model | `src/models/operation.py` | `Operation` enum and parsing |
| View | `src/common/response.py` | Lambda proxy JSON serialization |
| Common | `src/common/` | Logging and typed errors |
| Config | `src/config/settings.py` | Environment settings (no secrets) |

Dependencies point inward: `lambda_function -> handlers -> services -> models`,
with `common/` and `config/` shared by all layers. Services import no adapters
and no HTTP/AWS code.

## Event format

```json
{ "operation": "add", "a": 10, "b": 5 }
```

`operation` is one of `add`, `sub`, `mul`, `div`. `a` and `b` must be numbers.

Response shape (Lambda proxy integration; `body` is a JSON string):

```json
{
  "statusCode": 200,
  "headers": { "Content-Type": "application/json" },
  "body": "{\"operation\": \"add\", \"result\": 15}"
}
```

### Success

HTTP 200 with body `{"operation": "<op>", "result": <num>}`.

Integral results are rendered as integers (`15`), non-integral results as
floats (`2.5`).

### Errors

HTTP 400 with body `{"error": "<message>"}`:

| Case | Message |
|------|---------|
| Missing `operation`, `a`, or `b` | `Event must contain 'operation', 'a' and 'b'` |
| Unknown operation | `Unsupported operation: <op>` |
| Division by zero | `Cannot divide by zero` |

## Run locally

The Lambda file is the local runner:

```bash
cd calc-python-lambda

# Default test/events/event-add.json
python3 src/lambda_function.py

# Explicit event
python3 src/lambda_function.py test/events/event-div.json
```

Each flow can also run on its own:

```bash
python3 src/handlers/add.py test/events/event-add.json
python3 src/handlers/sub.py test/events/event-sub.json
python3 src/handlers/mul.py test/events/event-mul.json
python3 src/handlers/div.py test/events/event-div.json
python3 src/handlers/div.py test/events/event-div-zero.json
```

## Unit tests

```bash
python3 test/run_all.py
```

Tests use stdlib `unittest` only, require no AWS credentials or network, and
load their input from `test/events/` by matching file name. `test/unit/`
mirrors `src/`. See `test/README.md` and `test/events/README.md`.

## Adding a flow

1. Add the value to `Operation` in `src/models/operation.py`.
2. Add a `handle(event)` module in `src/handlers/` that validates input, calls
   `calc_service.operate(...)`, and returns `build_response(...)`.
3. Add the arithmetic branch to `src/services/calc_service.py`.
4. Register the handler in `_HANDLERS` in `src/lambda_function.py`.
5. Add `test/events/event-<case>.json` and the matching
   `test/unit/handlers/test_<case>.py`.
6. Document the new row in `test/events/README.md`.

## pip-modules and Lambda Layers

`pip-modules/` is the single place for pip dependencies (like `node_modules`)
and the source for a Lambda Layer. This project is stdlib-only, so it only
contains a README. Both `src/lambda_function.py` and `test/run_all.py` add the
project root and `pip-modules` to `sys.path`, and route bytecode caches to
`pip-modules/.pycache`.

## Invoke & Test from AWS Console

Once deployed, test the function without any local setup.

### AWS Console

1. Open the function in the [Lambda Console](https://console.aws.amazon.com/lambda/)
2. Go to **Test** tab → **Create new event**
3. Paste an event, e.g. `{"operation": "add", "a": 10, "b": 5}`
4. Click **Test** — the response appears under *Execution results*

### AWS CLI

```bash
aws lambda invoke \
  --function-name calc-python-lambda \
  --payload '{"operation": "add", "a": 10, "b": 5}' \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

### Expected response

```json
{
  "statusCode": 200,
  "headers": { "Content-Type": "application/json" },
  "body": "{\"operation\": \"add\", \"result\": 15}"
}
```

Error cases return `statusCode` 400 with body `{"error": "<message>"}`.

### Console test events

| Operation | Test event |
|-----------|-----------|
| add | `{"operation": "add", "a": 10, "b": 5}` |
| sub | `{"operation": "sub", "a": 10, "b": 5}` |
| mul | `{"operation": "mul", "a": 10, "b": 5}` |
| div | `{"operation": "div", "a": 10, "b": 4}` |
| div by zero | `{"operation": "div", "a": 10, "b": 0}` |
| unknown op | `{"operation": "pow", "a": 10, "b": 5}` |
| missing field | `{"operation": "add", "a": 10}` |

Logs: **Monitor** tab → **View CloudWatch logs** → log group `/aws/lambda/calc-python-lambda`.

## Deployment

Package `src/` and `pip-modules/` at the archive root (exclude `test/`,
`infra/`, and docs):

```bash
cd calc-python-lambda
zip -r ../calc-python-lambda.zip src pip-modules
```

- Handler: `src.lambda_function.lambda_handler`
- Runtime: Python 3.13 (or 3.12)
- Architecture: `arm64` (preferred) or `x86_64`
- Memory: 128 MB
- `boto3` is provided by the runtime and is not needed here.

See `infra/README.md` for SAM/CDK options.

## Logging

`common.logger.get_logger(__name__)` configures DEBUG logging once. The
controller logs invocation, routing, and response status; handlers and the
service log entry, result, and errors. On Lambda, logs go to the function's
CloudWatch log group `/aws/lambda/<function-name>`.
