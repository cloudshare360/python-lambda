# python-lambda

A monorepo of **production-ready Python AWS Lambda templates** built on the **MVC + hexagonal (ports & adapters)** architecture described in [`python-lambda-mvc-agent.md`](python-lambda-mvc-agent.md).

Each subproject is a **self-contained, independently deployable Lambda** that:
- Runs locally as a plain Python file (`python3 src/lambda_function.py`)
- Has zero AWS credentials / network requirements for local runs and unit tests
- Is fully unit-testable with `python3 test/run_all.py`
- Follows the AWS Well-Architected Framework
- Uses only the Python standard library (third-party deps go in `pip-modules/`)

---

## Workspace Contents

```
python-lambda/
├── python-lambda-mvc-agent.md          # The agent blueprint / architecture rules
├── .gitignore                          # excludes .env
├── calc-python-lambda/                 # Stdlib-only calculator (4 operations)
├── order-service-python-lambda/        # Full AWS app: DynamoDB, S3, Secrets Manager, REST client
├── string-utils-python-lambda/         # Stdlib-only string utilities (4 operations)
```

| Project | Complexity | AWS Services | External I/O | Purpose |
|---------|------------|--------------|--------------|---------|
| **calc-python-lambda** | Beginner | None | None | Minimal template — arithmetic only, no persistence, no external calls |
| **string-utils-python-lambda** | Beginner | None | None | Minimal template — string transforms, demonstrates unary + binary ops |
| **order-service-python-lambda** | Advanced | DynamoDB, S3, Secrets Manager | REST (stdlib `urllib`) | Reference app — full hexagonal layers, local fakes in `src/local.py` |

All three share the **same folder layout, dependency rule, and run/test commands**.

---

## `python-lambda-mvc-agent.md` — The Blueprint

This document is the **single source of truth** for the architecture. It defines:

1. **Goals** — Lambda as controller, independently testable layers, local runnability
2. **Folder structure (required)** — every directory and file name with its role
3. **Layer responsibilities & dependency rule** — inward-only dependencies, MVC mapping
4. **Entry point rules** — composition root, `sys.path` setup, runnable `_main()`
5. **Handler rules** — one flow = one module, validation → service → response
6. **Service / adapter / repository rules** — lazy boto3, injected clients, stdlib REST
7. **Local execution** — lambda file IS the local runner; `src/local.py` for AWS apps
8. **Unit testing** — `test/unit/` mirrors `src/`, event↔test mapping, `run_all.py`
9. **Events** — one JSON per case, documented mapping table
10. **Logging** — DEBUG once via `common/logger.get_logger(__name__)`
11. **Documentation rules** — README, test/README, events/README templates
12. **AWS Well-Architected mapping** — 6 pillars → concrete practices
13. **Deployment packaging** — zip `src/` + `pip-modules/`, layer instructions
14. **Verification checklist** — 5-step smoke test for every project
15. **Deliverables** — exact file list for a compliant project

**Use it** by copying it into a new project (or referencing it from an agent) whenever you scaffold a new Python Lambda that must meet these standards.

---

## Template Projects — How to Choose

| If you need… | Start from |
|--------------|------------|
| A pure-logic Lambda (no AWS, no HTTP) | `calc-python-lambda` or `string-utils-python-lambda` |
| A Lambda with DynamoDB / S3 / Secrets Manager | `order-service-python-lambda` |
| A Lambda calling external REST APIs | `order-service-python-lambda` (see `adapters/external/secret_server/`) |
| A Lambda with multiple flows sharing a domain model | Any — add handlers to `_HANDLERS` in `lambda_function.py` |

All templates are **production-shaped**: they include `infra/README.md` (SAM/CDK notes), `pip-modules/` for layers, and `test/` with event↔test mapping.

---

## Common Commands (run inside any subproject)

```bash
# Run the Lambda locally (uses default test event)
python3 src/lambda_function.py

# Run with a specific event file
python3 src/lambda_function.py test/events/event-<case>.json

# Run a single flow handler directly
python3 src/handlers/<flow>.py test/events/event-<case>.json

# Run ALL unit tests (stdlib unittest, no AWS, no network)
python3 test/run_all.py

# Build deployment package (zip src + pip-modules at root)
zip -r ../<project>.zip src pip-modules
```

### Per-project defaults

| Project | Default event | Flow handlers |
|---------|---------------|---------------|
| calc-python-lambda | `test/events/event-add.json` | `add`, `sub`, `mul`, `div` |
| string-utils-python-lambda | `test/events/event-upper.json` | `upper`, `lower`, `reverse`, `concat` |
| order-service-python-lambda | `test/events/event-create-order.json` | `create-order`, `get-order` |

---

## Generating New Lambda-Python Projects

### Option 1 — Manual scaffold (recommended for first time)

```bash
# 1. Pick the closest template
cp -r python-lambda/calc-python-lambda python-lambda/<your-domain>-python-lambda

# 2. Rename files that embed the domain
cd python-lambda/<your-domain>-python-lambda
# e.g. calc_service.py → <domain>_service.py
#       operation.py → <model>.py
#       test_<case>.py → test_<new_case>.py

# 3. Update imports and references
#    - src/services/<domain>_service.py
#    - src/models/<model>.py
#    - src/handlers/*.py
#    - src/lambda_function.py (_HANDLERS dict)
#    - test/unit/** (mirror src/)

# 4. Add event files in test/events/ and update test/events/README.md

# 5. Verify
python3 src/lambda_function.py
python3 test/run_all.py
```

### Option 2 — Cookiecutter / script (for automation)

The blueprint is deterministic enough to script. A minimal generator would:

1. Accept: `domain`, `operations[]` (list of `{name, params[], is_unary?}`)
2. Produce: full folder tree from `python-lambda-mvc-agent.md` §2
3. Render: `lambda_function.py` with `_HANDLERS` from `operations`
4. Render: `handlers/<op>.py` (validate + call service + `__main__`)
5. Render: `services/<domain>_service.py` with one method per op
6. Render: `models/` with enum + parser
6. Render: `test/events/event-<op>.json` + `test/unit/handlers/test_<op>.py`
7. Wire `config/settings.py`, `common/`, `pip-modules/`, `infra/README.md`

### Option 3 — Use with an agent

Copy `python-lambda-mvc-agent.md` into your agent's context (or reference it) and prompt:

> "Scaffold a new Python Lambda project named `inventory-python-lambda` with operations `check-stock` (sku) and `reserve` (sku, qty). Follow the blueprint in `python-lambda-mvc-agent.md` exactly."

The agent will generate every file per the blueprint.

---

## Adding a Flow to an Existing Project

1. Add the operation to the enum in `src/models/`
2. Implement business logic in `src/services/<domain>_service.py`
3. Create `src/handlers/<flow>.py` with `handle(event, service)` + `__main__`
4. Register in `_HANDLERS` in `src/lambda_function.py`
5. Add `test/events/event-<flow>.json` and `test/unit/handlers/test_<flow>.py`
6. Update `test/events/README.md` mapping table
7. Run `python3 test/run_all.py` — must pass

---

## pip-modules & Lambda Layers

- `pip-modules/` = `node_modules` equivalent. Add deps with:
  ```bash
  pip3 install <package> -t <project>/pip-modules
  ```
- Both `src/lambda_function.py` and `test/run_all.py` add `pip-modules/` to `sys.path`
- Bytecode caches go to `pip-modules/.pycache` (clean source tree)
- **Build a Layer**: zip `pip-modules/` contents under `python/`
- `boto3` is provided by the Lambda runtime — **do not bundle it** unless you need a specific version

---

## Deployment

| Setting | Value |
|---------|-------|
| Handler | `src.lambda_function.lambda_handler` |
| Runtime | Python 3.13 (or 3.12) |
| Architecture | `arm64` (preferred) / `x86_64` |
| Memory | 128 MB (adjust per workload) |
| Package | `zip -r ../<name>.zip src pip-modules` (exclude `test/`, `infra/`, `README.md`) |
| Env vars | Defined in each project's `infra/README.md` and `config/settings.py` |

See `infra/README.md` in each subproject for SAM / CDK deployment notes.

---

## License

MIT — use freely as templates for your own Lambda projects.