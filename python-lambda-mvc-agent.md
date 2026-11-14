# Python Lambda MVC Agent Blueprint

A reusable agent instruction document. Copy this file into any project (or
reference it from your agent) whenever you need to scaffold a Python AWS Lambda
application that follows **MVC + hexagonal (ports & adapters)**, respects the
**AWS Well-Architected Framework**, and is fully testable locally — every service,
adapter, and flow testable independently, with the Lambda itself runnable as a
plain Python file.

Follow every rule below. Do not invent new patterns unless this document says so.

---

## 1. Goals

- **Lambda entry = controller/orchestrator.** `src/lambda_function.py` is the
  entry point and composition root. It parses the event, delegates to a handler,
  and returns the response. No business logic, no direct AWS/HTTP calls.
- **Dependent files grouped by category**: `handlers/` (per flow), `services/`
  (business logic), `adapters/aws` + `adapters/external` (all I/O), `repositories/`,
  `models/`, `common/`, `config/`.
- **Independently testable**: dependencies point inward; services depend on
  abstractions, not boto3. Tests mirror `src/`.
- **Runs locally as a python file**: `python3 src/lambda_function.py [test/events/event-<case>.json]`.
- **All unit tests runnable as a python file**: `python3 test/run_all.py`.

---

## 2. Folder structure (required)

```
<domain>-python-lambda/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── lambda_function.py           # ENTRY / controller / composition root
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
│   │   └── <flow>.py                # handle(event, deps) + local __main__
│   ├── services/
│   │   ├── __init__.py
│   │   └── <domain>_service.py      # business logic (depends on abstractions)
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── aws/
│   │   │   ├── __init__.py
│   │   │   ├── dynamodb.py
│   │   │   ├── s3.py
│   │   │   └── secret_manager.py
│   │   └── external/
│   │       ├── __init__.py
│   │       └── <vendor>/restapi/
│   │           ├── __init__.py
│   │           ├── client.py        # base REST client (urllib, injectable)
│   │           └── <resource>.py    # one class per resource, individual methods
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── <repo>.py                # data access over adapters
│   └── models/
│       ├── __init__.py
│       └── <model>.py               # dataclasses / enums
├── test/
│   ├── __init__.py
│   ├── run_all.py                   # RUN ALL unit tests as a python file
│   ├── README.md                    # maps event files <-> test cases <-> expected
│   ├── events/                      # one JSON per test case
│   │   ├── README.md                # event-file -> test-case table
│   │   └── event-<case>.json
│   └── unit/                        # mirrors src/; one test per case
│       ├── __init__.py
│       ├── handlers/test_<case>.py
│       ├── services/test_<service>.py
│       ├── adapters/aws/test_<adapter>.py
│       └── adapters/external/test_<client>.py
├── pip-modules/                     # third-party deps / layer source
│   └── README.md
└── infra/                           # SAM / CDK
    └── README.md
```

Rules:
- **One flow = one handler module** in `handlers/`.
- **One resource = one adapter file**; a vendor with several operations gets one
  file per resource with **individual methods**.
- `test/unit/` mirrors `src/` so every service/adapter/handler has an isolated test.
- **Event file ↔ test case mapping must be obvious.** Use the same `<case>`
  token in both: `test/events/event-<case>.json` and
  `test/unit/.../test_<case>.py`. Each test loads its event file by that name.
  Document the mapping in `test/events/README.md`.
- `pip-modules/` is the single place for pip deps (like `node_modules`) and the
  source for a Lambda Layer.

---

## 3. Layer responsibilities & dependency rule

```
lambda_function.py (composition root: builds real clients)
      │ injects
      ▼
handlers/<flow>.py ──► services/ ──► repositories/ ──► adapters/aws|external
                              ▲
                        models/, common/
```

| Layer | Location | Responsibility | Must NOT |
|-------|----------|----------------|----------|
| Controller | `lambda_function.py` | Parse event, route to handler, return response | business logic, AWS/HTTP calls |
| Handler | `handlers/` | Flow-specific: validate + call service | business rules, AWS/HTTP |
| Service | `services/` | Business logic | import boto3 / know HTTP |
| Repository | `repositories/` | Data access | business logic |
| Adapter | `adapters/aws`, `adapters/external` | Wrap one AWS service or REST resource | business decisions |
| Model | `models/` | Dataclasses/enums | I/O |
| View | `common/response.py` | JSON serialization | business logic |
| Common | `common/` | Logging, errors, response | — |
| Config | `config/settings.py` | Env-driven settings | hard-coded secrets |

**Dependencies point inward only.** Services never import adapters directly.

### MVC mapping
- **Model** → `models/` (+ `repositories/`).
- **View** → `common/response.py`.
- **Controller** → `lambda_function.py` + `handlers/`.

---

## 4. Entry point (`src/lambda_function.py`)

- Add project root **and** `pip-modules` to `sys.path`; set
  `sys.pycache_prefix` under `pip-modules/.pycache` (keeps the tree clean).
- Build logger; define `lambda_handler(event, context)`.
- **Composition root**: build real clients (lazy boto3) and inject into the
  service/handlers.
- Route by `event["operation"]` to the matching `handlers/<flow>.handle(...)`.
- **Directly runnable**:
  ```python
  def _main():
      event_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_ROOT, "test", "events", "event-<default>.json")
      with open(event_path) as f:
          event = json.load(f)
      response = lambda_handler(event, None)
      print(json.dumps(response, indent=2))

  if __name__ == "__main__":
      _main()
  ```
- For AWS/REST apps, `_main()` must use in-memory fakes (`src/local.py`) so it
  runs with no credentials/network.

---

## 5. Handler rules (`handlers/<flow>.py`)

- `handle(event: dict, deps) -> dict` — flow-specific orchestration.
- Validate required keys (`common.errors.ValidationError`).
- Map `AppError` → `build_response(status, body)`.
- No AWS/HTTP calls, no business rules.
- Include a `__main__` so one flow can be run locally:
  `python3 src/handlers/<flow>.py test/events/event-<case>.json`.

---

## 6. Service / adapter / repository rules

- Services: one class/module per capability; constructor takes injected deps.
- Adapters (AWS): lazy-init boto3 once; accept injected `client` for tests; map
  AWS errors to `common/errors`.
- Adapters (external): `RestClient` on stdlib `urllib` with timeout + retry and
  injectable transport; one class per resource with individual methods.
- Repositories: map items ↔ models; no business logic.

---

## 7. Local execution (lambda as a python file)

Both must work:

```bash
python3 src/lambda_function.py                                # uses a default test/events/*.json
python3 src/lambda_function.py test/events/event-create-order.json
```

- AWS/REST apps: `src/local.py` provides in-memory fakes; `_main()` uses them.
- There is **no separate local runner** — the lambda file itself is the local
  runner.
- Per-flow run: `python3 src/handlers/<flow>.py test/events/event-<case>.json`.

---

## 8. Unit testing (run all as a python file)

- `test/unit/` mirrors `src/` (handlers, services, adapters, repositories).
- Use stdlib `unittest` (or pytest). **No AWS credentials, no network** — inject
  fakes; use `moto` only in `test/integration/` if needed.
- **Event↔test mapping:** `test/events/event-<case>.json` is loaded by
  `test/unit/.../test_<case>.py`. A small helper loads the event:
  ```python
  def load_event(name):
      path = os.path.join(PROJECT_ROOT, "test", "events", name)
      with open(path) as f:
          return json.load(f)
  ```
- `test/run_all.py` discovers and runs **all** unit tests and exits non-zero on
  failure:
  ```python
  import os, sys, unittest
  PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  sys.path.insert(0, PROJECT_ROOT)
  sys.path.insert(0, os.path.join(PROJECT_ROOT, "pip-modules"))
  suite = unittest.TestLoader().discover(os.path.join(PROJECT_ROOT, "test", "unit"))
  result = unittest.TextTestRunner(verbosity=2).run(suite)
  sys.exit(0 if result.wasSuccessful() else 1)
  ```
- Run: `python3 test/run_all.py`.

---

## 9. Events (`test/events/`)

- One file per flow and per error case, named `test/events/event-<case>.json`.
- Each file must be obviously tied to its test: same `<case>` token as
  `test/unit/.../test_<case>.py`, and listed in `test/events/README.md`:
  `event file | test file | flow | expected result`.
- Shape: `{ "operation": "<flow>", ... }`.

---

## 10. Logging (CloudWatch)

- `common/logger.get_logger(__name__)` sets DEBUG once.
- Controller logs invocation/routing/response; services log entry/result/error.
- On Lambda logs go to `/aws/lambda/<function-name>`.

---

## 11. Documentation rules

`README.md`: overview, folder tree, layer explanation, event format, local run
(`python3 src/lambda_function.py`), per-flow run, unit tests (`python3
test/run_all.py`), **console invocation (AWS Console, CLI, cURL)**, adding a flow,
pip-modules/layer, deployment.

`test/README.md` and `test/events/README.md`: prerequisites, call chain,
event↔test mapping table, per-case commands with expected response + logs,
error cases, run-all, CloudWatch, troubleshooting.

---

## 12. AWS Well-Architected mapping

| Pillar | How this blueprint satisfies it |
|--------|----------------------------------|
| Operational Excellence | Structured DEBUG logs, request id, no `print` in libs. |
| Security | Secrets in Secrets Manager, no hard-coded creds, least-privilege IAM. |
| Reliability | Typed errors, timeouts, retries, idempotency. |
| Performance Efficiency | Reuse clients, lazy init, right-size memory, arm64. |
| Cost Optimization | Minimal deps, arm64, scale-to-zero. |
| Sustainability | Efficient code, small packages. |

---

## 13. Deployment packaging

- Zip `src/` and `pip-modules/` at the root (exclude `test/`, `infra/`,
  `README.md`). `boto3` is provided by the runtime.
- Build:
  ```bash
  cd <domain>-python-lambda
  zip -r ../<domain>.zip src pip-modules
  ```
- Lambda Layer: zip `pip-modules` contents under `python/`.
- Handler: `src.lambda_function.lambda_handler`. Runtime Python 3.13/3.12,
  architecture `arm64`/`x86_64`, memory 128 MB.

---

## 14. Verification checklist

1. `python3 src/lambda_function.py test/events/event-<case>.json` → expected status/body.
2. `python3 src/handlers/<flow>.py test/events/event-<case>.json` → same result (per flow).
3. `python3 test/run_all.py` → all unit tests pass, **no AWS calls**.
4. DEBUG logs appear for controller, handler, service, adapters.
5. Exit code 0.
6. **After deployment**: AWS Console Test tab, `aws lambda invoke`, and cURL all
   return the same expected response as local runs.

## 15. Console invocation (post-deployment)

Every project README must document how to invoke the deployed Lambda:

- **AWS Console**: function → **Test** tab → create event → **Test**
- **AWS CLI**: `aws lambda invoke --function-name <name> --payload '<event>' --cli-binary-format raw-in-base64-out response.json`
- **cURL** (if API Gateway front): `curl -X POST <url> -H "Content-Type: application/json" -d '<event>'`
- **Response format**: Lambda proxy integration — `{"statusCode": 200|400|404|502, "headers": {"Content-Type": "application/json"}, "body": "<JSON string>"}`
- **Logs**: AWS Console → **Monitor** → **View CloudWatch logs** → log group `/aws/lambda/<function-name>`

## 16. Deliverables

- `README.md`, `requirements.txt`
- `src/lambda_function.py`, `src/config/`, `src/common/`, `src/handlers/`,
  `src/services/`, `src/adapters/{aws,external}/`, `src/repositories/`,
  `src/models/`, `src/local.py` (AWS/REST apps only)
- `test/run_all.py`, `test/unit/**` (mirrors `src/`), `test/README.md`
- `test/events/event-<case>.json` + `test/events/README.md`
- `pip-modules/README.md`, `infra/README.md`