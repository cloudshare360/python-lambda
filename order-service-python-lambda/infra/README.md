# infra/

Infrastructure-as-code for the order-service Lambda (SAM or CDK). This
directory is intentionally documentation-only in the reference project; no
template is bundled.

## What to define

- **Function:** handler `src.lambda_function.lambda_handler`, runtime Python
  3.13/3.12, architecture `arm64` (or `x86_64`), memory 128 MB, timeout ~10 s.
- **Package:** zip `src/` + `pip-modules/` at the project root. `boto3` is
  provided by the runtime and must not be bundled.
- **Layer (optional):** `pip-modules/` contents under `python/` in the zip.
- **Environment variables:** `AWS_REGION`, `TABLE_NAME`, `BUCKET_NAME`,
  `SECRET_SERVER_URL`, `SECRET_SERVER_TOKEN` (point the last one at a Secrets
  Manager or SSM value, never a literal in source).
- **IAM (least privilege):**
  - `dynamodb:PutItem`, `dynamodb:GetItem` on the orders table.
  - `s3:PutObject`, `s3:GetObject` on the invoices bucket.
  - `secretsmanager:GetSecretValue` on the `db-creds` secret.
  - Outbound HTTPS to the secret server endpoint.
- **Observability:** CloudWatch Logs at `/aws/lambda/<function-name>`; the code
  already emits DEBUG structured logs.

## Example packaging

```bash
cd order-service-python-lambda
zip -r ../order-service.zip src pip-modules
```
