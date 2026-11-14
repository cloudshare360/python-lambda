# infra

Infrastructure-as-code definitions for deploying this Lambda.

## Options

- **SAM** - add a `template.yaml` and deploy with `sam build && sam deploy`.
- **CDK** - add a CDK app under `cdk/`.

## Lambda settings

- Handler: `src.lambda_function.lambda_handler`
- Runtime: Python 3.13 (or 3.12)
- Architecture: `arm64` (preferred) or `x86_64`
- Memory: 128 MB
- Timeout: a few seconds is sufficient; the function does no I/O

## Deployment package

Per the blueprint, zip `src/` and `pip-modules/` at the archive root and exclude
`test/`, `infra/`, and documentation:

```bash
cd calc-python-lambda
zip -r ../calc-python-lambda.zip src pip-modules
```

`boto3` is provided by the runtime and is not needed in this project.

## Pre-deploy verification

```bash
python3 src/lambda_function.py
python3 src/lambda_function.py test/events/event-add.json
python3 src/handlers/div.py test/events/event-div-zero.json
python3 test/run_all.py
```
