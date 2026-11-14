# string-utils-python-lambda

## Overview

AWS Lambda function (Python 3.12/3.13) exposing string utility operations:
`upper`, `lower`, `reverse`, and `concat`. The project follows an MVC +
hexagonal (ports & adapters) layout aligned with the AWS Well-Architected
Framework and is testable locally without AWS credentials or network access.

The entry point (`src/lambda_function.py`) is the composition root and
controller. It validates the event envelope, routes `operation` to a thin flow
handler, and returns the response. Handlers validate their inputs and delegate
all business logic to `src/services/string_service.py`. No layer performs AWS
or HTTP calls.

## Folder tree

```
string-utils-python-lambda/
├── README.md
├── requirements.txt                 # stdlib only
├── src/
│   ├── __init__.py
│   ├── lambda_function.py           # entry / controller / composition root
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # env-driven settings (no secrets)
│   ├── common/
│   │   ├── __init__.py
│   │   ├── logger.py                # get_logger()
│   │   ├── errors.py                # AppError hierarchy
│   │   └── response.py              # build_response(status, body)  [VIEW]
│   ├── handlers/                    # one module per flow (thin adapters)
│   │   ├── __init__.py
│   │   ├── upper.py
│   │   ├── lower.py
│   │   ├── reverse.py
│   │   └── concat.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── string_service.py        # business logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── text_operation.py        # TextOperation enum + from_str
│   └── adapters/
│       └── __init__.py              # no AWS/external I/O in this project
├── test/
│   ├── __init__.py
│   ├── run_all.py                   # run all unit tests as a python file
│   ├── README.md
│   ├── events/                      # one JSON per test case
│   │   ├── README.md                # event-file -> test-case table
│   │   ├── event-upper.json
│   │   ├── event-lower.json
│   │   ├── event-reverse.json
│   │   ├── event-concat.json
│   │   ├── event-invalid-operation.json
│   │   └── event-missing-field.json
│   └── unit/                        # mirrors src/; one test per case
│       ├── __init__.py
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── test_upper.py
│       │   ├── test_lower.py
│       │   ├── test_reverse.py
│       │   ├── test_concat.py
│       │   ├── test_invalid_operation.py
│       │   └── test_missing_field.py
│       └── services/
│           ├── __init__.py
│           └── test_string_service.py
├── pip-modules/                     # third-party deps / Lambda Layer source
│   └── README.md
└── infra/                           # SAM / CDK placeholder
    └── README.md
```

## Layer responsibilities

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Controller | `src/lambda_function.py` | Parse/validate the event, route to a handler, return the response |
| Handler | `src/handlers/<flow>.py` | Flow-specific validation, call the service, map errors to a response |
| Service | `src/services/string_service.py` | Business logic: `operate(operation, a, b) -> str` |
| Model | `src/models/text_operation.py` | `TextOperation` enum and `from_str` |
| View | `src/common/response.py` | JSON serialization of responses |
| Common | `src/common/` | Logging, typed errors, response builder |
| Config | `src/config/settings.py` | Env-driven settings (`APP_NAME`, `LOG_LEVEL`) |
| Adapters | `src/adapters/` | I/O wrappers (none needed; stdlib only) |

Dependencies point inward: `lambda_function` → `handlers` → `services` →
`models` / `common`. Services never import adapters or know about HTTP.

## Operations and event format

```json
{ "operation": "upper", "a": "hello", "b": "" }
```

`a` and `b` are strings; `b` may be empty for unary operations.

| Operation | Result |
|-----------|--------|
| `upper` | `str(a).upper()` |
| `lower` | `str(a).lower()` |
| `reverse` | `str(a)[::-1]` |
| `concat` | `str(a) + str(b)` |

Success: HTTP 200, body `{"operation": "<op>", "result": "<string>"}`.

Errors (HTTP 400):

- missing key → `{"error": "Event must contain 'operation', 'a' and 'b'"}`
- unknown operation → `{"error": "Unsupported operation: <op>"}`

## Local run

```bash
# Default test/events/event-upper.json
python3 src/lambda_function.py

# Specific event file
python3 src/lambda_function.py test/events/event-upper.json
```

The lambda file is the local runner; no separate local harness is required.
`_main()` prints the event and the response, then exits 0.

## Per-flow run

Each handler module is runnable on its own. With no argument it loads the
matching `test/events/event-<flow>.json`.

```bash
python3 src/handlers/upper.py test/events/event-upper.json
python3 src/handlers/lower.py test/events/event-lower.json
python3 src/handlers/reverse.py test/events/event-reverse.json
python3 src/handlers/concat.py test/events/event-concat.json
```

## Unit tests

```bash
python3 test/run_all.py
```

Tests mirror `src/` under `test/unit/`, use stdlib `unittest`, and require no
AWS credentials or network access. `test/run_all.py` exits non-zero if any test
fails. Each handler test loads its event file from `test/events/` by the same
case token. See `test/README.md` and `test/events/README.md` for the full
event ↔ test mapping.

## Adding a flow

1. Add the operation to `TextOperation` in `src/models/text_operation.py`.
2. Implement the transformation in `src/services/string_service.py`.
3. Add `src/handlers/<flow>.py` (copy an existing handler and change
   `OPERATION`, the default event path, and the docs).
4. Register the handler in `_HANDLERS` in `src/lambda_function.py`.
5. Add `test/events/event-<flow>.json` and
   `test/unit/handlers/test_<flow>.py`, then update both README mapping tables.

## pip-modules / Lambda Layer

Third-party dependencies belong in `pip-modules/` (like `node_modules`) and are
added to `sys.path` by `src/lambda_function.py`. This project uses only the
standard library, so `pip-modules/` contains no packages. Bytecode caches from
local runs are written under `pip-modules/.pycache` so the source tree stays
clean.

To build a Lambda Layer, zip the contents of `pip-modules/` under a `python/`
folder.

## Deployment

- Handler: `src.lambda_function.lambda_handler`
- Runtime: Python 3.12 / 3.13
- Architecture: `arm64` or `x86_64`
- Memory: 128 MB

Build the deployment package (exclude `test/`, `infra/`, and `README.md`):

```bash
cd string-utils-python-lambda
zip -r ../string-utils-python-lambda.zip src pip-modules
```

`boto3` is provided by the Lambda runtime; do not bundle it unless you need a
different version.
