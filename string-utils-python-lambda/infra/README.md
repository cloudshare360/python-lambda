# infra

Infrastructure-as-code (SAM or CDK) for the string-utils Lambda.

This project ships no infrastructure code. When deploying, package `src/` and
`pip-modules/` as the Lambda bundle (see the root `README.md`), or add a SAM
template / CDK stack here that points the handler at
`src.lambda_function.lambda_handler`.

Suggested runtime settings:

- Runtime: Python 3.12 / 3.13
- Handler: `src.lambda_function.lambda_handler`
- Architecture: `arm64` or `x86_64`
- Memory: 128 MB
- Environment: `APP_NAME`, `LOG_LEVEL` (no secrets; none are needed here)

The function needs no AWS permissions beyond basic CloudWatch Logs writing.
