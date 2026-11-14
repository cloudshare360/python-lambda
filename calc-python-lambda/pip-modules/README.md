# pip-modules

The single place for third-party Python dependencies (like `node_modules`) and
the source for a Lambda Layer. This calculator is stdlib-only, so the directory
is intentionally empty apart from this README.

## Usage

```bash
# Install a dependency locally (no virtualenv needed)
pip install -t pip-modules <package>

# Create a Lambda Layer zip (contents must live under python/)
mkdir -p layer/python
cp -R pip-modules/. layer/python/
cd layer && zip -r ../calc-layer.zip python
```

## Notes

- `src/lambda_function.py`, the per-flow handler `_main()` functions, and
  `test/run_all.py` add this directory to `sys.path`.
- Bytecode caches are written to `pip-modules/.pycache` (via
  `sys.pycache_prefix`) so `src/` stays clean.
- `boto3` is provided by the Lambda runtime and must not be bundled here.
