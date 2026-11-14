# test/events/

One JSON event per test case. Each file shares its `<case>` token with the test
that loads it: `event-<case>.json` ↔ `test/unit/.../test_<case>.py`.

| Event file | Test file | Flow | Expected result |
| --- | --- | --- | --- |
| `event-create-order.json` | `test/unit/handlers/test_create_order.py` | `create-order` | `200` — `order_id=A1`, `customer=Sri`, `amount=99.5`, `invoice_s3_key=invoices/A1.json`, `api_key_source=secret_server`, `db_user=admin` |
| `event-get-order.json` | `test/unit/handlers/test_get_order.py` | `get-order` | `200` — seeded order `A1` (`customer=Sri`, `amount=99.5`) |
| `event-invalid-operation.json` | `test/unit/handlers/test_invalid_operation.py` | any | `400` — `{"error":"Unsupported operation: delete-order"}` |
| `event-missing-field.json` | `test/unit/handlers/test_missing_field.py` | `create-order` | `400` — `{"error":"Event must contain 'operation', 'order_id', 'customer' and 'amount'"}` |

## Files

- `event-create-order.json`
  ```json
  {"operation": "create-order", "order_id": "A1", "customer": "Sri", "amount": 99.5}
  ```
- `event-get-order.json`
  ```json
  {"operation": "get-order", "order_id": "A1"}
  ```
- `event-invalid-operation.json`
  ```json
  {"operation": "delete-order", "order_id": "A1"}
  ```
- `event-missing-field.json` (no `amount`)
  ```json
  {"operation": "create-order", "order_id": "A1", "customer": "Sri"}
  ```

## Run one case

```bash
cd order-service-python-lambda
python3 src/lambda_function.py test/events/event-create-order.json
python3 src/lambda_function.py test/events/event-get-order.json
```

When no path is given, `src/lambda_function.py` defaults to
`test/events/event-create-order.json`. All local runs use the in-memory fakes in
`src/local.py` — no AWS, no network.
