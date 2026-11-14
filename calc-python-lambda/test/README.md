# Testing guide

All tests are stdlib `unittest`, runnable as a plain Python file, with no AWS
credentials and no network access.

## Prerequisites

- Python 3.10+ (`sys.pycache_prefix` is used)
- Run from the project root: `calc-python-lambda/`
- No installation step; `requirements.txt` is stdlib-only

## Run everything

```bash
python3 test/run_all.py
```

`run_all.py` adds the project root and `pip-modules` to `sys.path`, discovers
every `test_*.py` under `test/unit/`, and exits non-zero if any test fails.

## Call chain exercised by the tests

```
lambda_handler(event, context)        src/lambda_function.py
  -> handlers/<flow>.handle(event)    src/handlers/
    -> calc_service.operate(op, a, b) src/services/calc_service.py
      -> Operation.from_str(op)       src/models/operation.py
  -> build_response(status, body)     src/common/response.py
```

Handler tests call `handle(event)` directly. The unknown-operation and
missing-field tests call `lambda_handler` to cover routing and validation.
Service tests call `operate` directly.

## Event <-> test mapping

Every event file shares its `<case>` token with its test file. The test loads
the event with `test.load_event("<file>")`.

| Event file | Test file | Flow | Expected |
|------------|-----------|------|----------|
| `test/events/event-add.json` | `test/unit/handlers/test_add.py` | add | 200 `{"operation": "add", "result": 15}` |
| `test/events/event-sub.json` | `test/unit/handlers/test_sub.py` | sub | 200 `{"operation": "sub", "result": 5}` |
| `test/events/event-mul.json` | `test/unit/handlers/test_mul.py` | mul | 200 `{"operation": "mul", "result": 50}` |
| `test/events/event-div.json` | `test/unit/handlers/test_div.py` | div | 200 `{"operation": "div", "result": 2.5}` |
| `test/events/event-div-zero.json` | `test/unit/handlers/test_div_zero.py` | div | 400 `{"error": "Cannot divide by zero"}` |
| `test/events/event-invalid-operation.json` | `test/unit/handlers/test_invalid_operation.py` | router | 400 `{"error": "Unsupported operation: mod"}` |
| `test/events/event-missing-field.json` | `test/unit/handlers/test_missing_field.py` | router | 400 `{"error": "Event must contain 'operation', 'a' and 'b'"}` |

`test/unit/services/test_calc_service.py` covers the service contract directly:
all four operations, division by zero, unknown operation, and non-numeric
operands. It uses no event file.

## Per-case commands and expected output

All commands run from `calc-python-lambda/`.

### add

```bash
python3 src/handlers/add.py test/events/event-add.json
```

Expected `statusCode` 200 and body `{"operation": "add", "result": 15}`.
Expected logs: `handle add event=...` and `operate operation=add a=10.0 b=5.0`.

### sub

```bash
python3 src/handlers/sub.py test/events/event-sub.json
```

Expected `statusCode` 200 and body `{"operation": "sub", "result": 5}`.

### mul

```bash
python3 src/handlers/mul.py test/events/event-mul.json
```

Expected `statusCode` 200 and body `{"operation": "mul", "result": 50}`.

### div

```bash
python3 src/handlers/div.py test/events/event-div.json
```

Expected `statusCode` 200 and body `{"operation": "div", "result": 2.5}`.

### div by zero

```bash
python3 src/handlers/div.py test/events/event-div-zero.json
```

Expected `statusCode` 400 and body `{"error": "Cannot divide by zero"}`.

### unknown operation

```bash
python3 src/lambda_function.py test/events/event-invalid-operation.json
```

Expected `statusCode` 400 and body `{"error": "Unsupported operation: mod"}`.
Logs include `routing` only for valid operations; this case logs
`invocation error=Unsupported operation: mod`.

### missing field

```bash
python3 src/lambda_function.py test/events/event-missing-field.json
```

Expected `statusCode` 400 and body
`{"error": "Event must contain 'operation', 'a' and 'b'"}`.

## Error cases

| Condition | Raised at | Response |
|-----------|-----------|----------|
| Missing required key | handler / controller validation | 400 missing-keys message |
| Unknown operation | controller routing or `Operation.from_str` | 400 `Unsupported operation: <op>` |
| Divide by zero | `calc_service.operate` | 400 `Cannot divide by zero` |
| Non-numeric operand | `calc_service.operate` | 400 `'a' and 'b' must be numbers` |

`AppError` subclasses carry their own HTTP status (`ValidationError` 400,
`NotFoundError` 404, `IntegrationError` 502), so new error types map to
responses without changing the controller.

## Logs and CloudWatch

Locally, DEBUG logs print to the terminal in the format
`<time> <level> <logger> <message>`. On Lambda the same records are written to
CloudWatch Logs under `/aws/lambda/<function-name>`.

Key records:

- controller: `invocation start`, `routing operation=...`, `invocation response status=...`
- handler: `handle <flow> event=...`, `handle <flow> error=...`
- service: `operate operation=... a=... b=...`

## Troubleshooting

- **`ModuleNotFoundError: src`** — run from `calc-python-lambda/`, or use
  `python3 test/run_all.py` / `python3 src/handlers/<flow>.py` so the project
  root is on `sys.path`.
- **No logs** — set `LOG_LEVEL=DEBUG` (the default) or a higher level in the
  environment; logging is configured once on first `get_logger` call.
- **Unexpected `15.0` in service tests** — `operate` always returns a float;
  handlers render integral floats as ints in the JSON body.
- **Bytecode caches** — `__pycache__` is redirected to
  `pip-modules/.pycache`; delete that directory to force recompilation.
