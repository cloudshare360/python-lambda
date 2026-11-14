# test/events/

One JSON event per test case. The `<case>` token in the filename is identical to
the test module: `event-<case>.json` ↔ `test/unit/.../test_<case>.py`. Each test
loads its event file by that name from this directory.

## Mapping

| Event file | Test file | Flow | Expected result |
|------------|-----------|------|-----------------|
| `event-upper.json` | `test/unit/handlers/test_upper.py` | `upper` | 200, `{"operation": "upper", "result": "HELLO"}` |
| `event-lower.json` | `test/unit/handlers/test_lower.py` | `lower` | 200, `{"operation": "lower", "result": "hello"}` |
| `event-reverse.json` | `test/unit/handlers/test_reverse.py` | `reverse` | 200, `{"operation": "reverse", "result": "olleh"}` |
| `event-concat.json` | `test/unit/handlers/test_concat.py` | `concat` | 200, `{"operation": "concat", "result": "foobar"}` |
| `event-invalid-operation.json` | `test/unit/handlers/test_invalid_operation.py` | controller validation | 400, `{"error": "Unsupported operation: capitalize"}` |
| `event-missing-field.json` | `test/unit/handlers/test_missing_field.py` | controller validation | 400, `{"error": "Event must contain 'operation', 'a' and 'b'"}` |

## Event shape

```json
{
  "operation": "<upper|lower|reverse|concat>",
  "a": "<string>",
  "b": "<string; may be empty>"
}
```

All three keys are required. `a` and `b` may be any JSON values for the service
layer (`str(...)` is applied), but the fixtures use strings.

## Commands

```bash
python3 src/lambda_function.py test/events/event-upper.json
python3 src/lambda_function.py test/events/event-invalid-operation.json
python3 src/handlers/reverse.py test/events/event-reverse.json
python3 test/run_all.py
```

View one event file:

```bash
python3 -m json.tool test/events/event-concat.json
```

## Expected output

```json
{
  "statusCode": 200,
  "body": "{\"operation\": \"concat\", \"result\": \"foobar\"}"
}
```

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Event must contain 'operation', 'a' and 'b'\"}"
}
```

Add a new case by creating `event-<case>.json` here, creating
`test/unit/handlers/test_<case>.py` that loads it, and adding a row to both this
table and `test/README.md`.
