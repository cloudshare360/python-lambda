# Test events

One JSON event per test case. The `<case>` token is identical in the event file
and its test file: `event-<case>.json` is loaded by
`test/unit/.../test_<case>.py` through `test.load_event(...)`.

| Event file | Test file | Flow | Expected |
|------------|-----------|------|----------|
| `event-add.json` | `test/unit/handlers/test_add.py` | add | 200 `{"operation": "add", "result": 15}` |
| `event-sub.json` | `test/unit/handlers/test_sub.py` | sub | 200 `{"operation": "sub", "result": 5}` |
| `event-mul.json` | `test/unit/handlers/test_mul.py` | mul | 200 `{"operation": "mul", "result": 50}` |
| `event-div.json` | `test/unit/handlers/test_div.py` | div | 200 `{"operation": "div", "result": 2.5}` |
| `event-div-zero.json` | `test/unit/handlers/test_div_zero.py` | div | 400 `{"error": "Cannot divide by zero"}` |
| `event-invalid-operation.json` | `test/unit/handlers/test_invalid_operation.py` | router | 400 `{"error": "Unsupported operation: mod"}` |
| `event-missing-field.json` | `test/unit/handlers/test_missing_field.py` | router | 400 `{"error": "Event must contain 'operation', 'a' and 'b'"}` |

The service unit tests (`test/unit/services/test_calc_service.py`) exercise the
arithmetic contract directly and do not use an event file.

## Event contents

| File | Payload |
|------|---------|
| `event-add.json` | `{"operation": "add", "a": 10, "b": 5}` |
| `event-sub.json` | `{"operation": "sub", "a": 10, "b": 5}` |
| `event-mul.json` | `{"operation": "mul", "a": 10, "b": 5}` |
| `event-div.json` | `{"operation": "div", "a": 10, "b": 4}` |
| `event-div-zero.json` | `{"operation": "div", "a": 10, "b": 0}` |
| `event-invalid-operation.json` | `{"operation": "mod", "a": 10, "b": 5}` |
| `event-missing-field.json` | `{"operation": "add", "a": 10}` (no `b`) |

## Adding a case

1. Add `test/events/event-<case>.json`.
2. Add `test/unit/handlers/test_<case>.py` (or under `services/` for a service
   contract test) that loads it with `load_event("event-<case>.json")`.
3. Add a row to the table above.
