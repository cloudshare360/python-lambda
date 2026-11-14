# test/

Prerequisites: Python 3.12/3.13 and this project's root as the working
directory. No third-party packages, AWS credentials, or network access are
required.

## Layout

```
test/
├── __init__.py
├── run_all.py
├── README.md
├── events/
│   ├── README.md
│   └── event-<case>.json
└── unit/
    ├── __init__.py
    ├── handlers/
    │   ├── __init__.py
    │   ├── test_<case>.py
    │   └── ...
    └── services/
        ├── __init__.py
        └── test_string_service.py
```

`test/unit/` mirrors `src/`. Each event case reuses the same `<case>` token in
`test/events/event-<case>.json` and `test/unit/.../test_<case>.py`.

## Call chain

```
test/unit/.../test_<case>.py
  -> load test/events/event-<case>.json
  -> src.lambda_function.lambda_handler  (or src.handlers.<flow>.handle)
     -> src.handlers.<flow>             (validates a, b)
        -> src.services.string_service  (business logic)
           -> src.models.TextOperation
        -> src.common.response.build_response
     -> src.common.errors.AppError mapped to status/body
```

## Event ↔ test mapping

| Event file | Test file | Flow | Expected result |
|------------|-----------|------|-----------------|
| `test/events/event-upper.json` | `test/unit/handlers/test_upper.py` | `upper` | 200, `{"operation": "upper", "result": "HELLO"}` |
| `test/events/event-lower.json` | `test/unit/handlers/test_lower.py` | `lower` | 200, `{"operation": "lower", "result": "hello"}` |
| `test/events/event-reverse.json` | `test/unit/handlers/test_reverse.py` | `reverse` | 200, `{"operation": "reverse", "result": "olleh"}` |
| `test/events/event-concat.json` | `test/unit/handlers/test_concat.py` | `concat` | 200, `{"operation": "concat", "result": "foobar"}` |
| `test/events/event-invalid-operation.json` | `test/unit/handlers/test_invalid_operation.py` | controller error | 400, `{"error": "Unsupported operation: capitalize"}` |
| `test/events/event-missing-field.json` | `test/unit/handlers/test_missing_field.py` | controller error | 400, `{"error": "Event must contain 'operation', 'a' and 'b'"}` |

`test/unit/services/test_string_service.py` covers the service directly,
independent of an event file.

## Per-case commands

Run through the lambda entry point:

```bash
python3 src/lambda_function.py test/events/event-upper.json
python3 src/lambda_function.py test/events/event-lower.json
python3 src/lambda_function.py test/events/event-reverse.json
python3 src/lambda_function.py test/events/event-concat.json
python3 src/lambda_function.py test/events/event-invalid-operation.json
python3 src/lambda_function.py test/events/event-missing-field.json
```

Run one flow directly:

```bash
python3 src/handlers/upper.py test/events/event-upper.json
python3 src/handlers/lower.py test/events/event-lower.json
python3 src/handlers/reverse.py test/events/event-reverse.json
python3 src/handlers/concat.py test/events/event-concat.json
```

Expected success response (upper):

```json
{
  "statusCode": 200,
  "body": "{\"operation\": \"upper\", \"result\": \"HELLO\"}"
}
```

Expected error responses:

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Unsupported operation: capitalize\"}"
}
```

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Event must contain 'operation', 'a' and 'b'\"}"
}
```

`body` is a JSON string, matching the Lambda proxy response shape.

## Run all unit tests

```bash
python3 test/run_all.py
```

Expected summary: every test passes, the last line is `OK`, and the exit code is
`0`. A failure prints the traceback and exits `1`.

## Logs

Every controller, handler, and service call emits DEBUG records. Locally they
appear on stderr in the form:

```
<timestamp> DEBUG src.services.string_service operate called: ...
```

On AWS Lambda the same records appear in CloudWatch Logs under
`/aws/lambda/<function-name>`. Set `LOG_LEVEL` in the environment when you need
a different level in deployed code.

## Troubleshooting

- `ModuleNotFoundError: No module named 'src'`: run commands from the
  `string-utils-python-lambda/` directory.
- `FileNotFoundError` for an event: pass a path under `test/events/` or use the
  per-flow default (no argument).
- `python3 src/handlers/<flow>.py` fails: use the Python 3 environment that can
  see this directory, not another checkout.
- Stale bytecode: remove `pip-modules/.pycache` and any `__pycache__`
  directories, then rerun.
- `run_all.py` exits non-zero: read the failing test's expected vs. actual
  status/body and fix the code or the event fixture, not the assertion.
