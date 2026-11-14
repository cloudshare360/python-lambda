# pip-modules

This folder holds third-party pip dependencies (like `node_modules` for
Node.js) and is the source for a Lambda Layer. The project root, `src/` and
`pip-modules/` are added to `sys.path` by both `src/lambda_function.py` and
`test/run_all.py`, so anything installed here is importable locally and on
Lambda. Bytecode caches are kept in `pip-modules/.pycache`.

## boto3

`boto3` is provided by the AWS Lambda runtime. **Do not** install it here - only
bundle packages the runtime does not provide.

## Installing a package

```bash
pip3 install <package> -t order-service-python-lambda/pip-modules
```

Then `import <package>` works locally and after deployment.
