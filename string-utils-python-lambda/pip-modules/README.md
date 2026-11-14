# pip-modules

Third-party dependencies installed into this directory are bundled with the
Lambda deployment package (`src` + `pip-modules`). This project uses only the
Python standard library, so no packages are vendored here.

Install a dependency into the layer source with:

```bash
pip3 install <package> -t pip-modules
```

`src/lambda_function.py` adds both the project root and `pip-modules` to
`sys.path`, and writes bytecode caches to `pip-modules/.pycache` so the source
tree stays clean.

The Lambda deployment zip should include `pip-modules/` at the root. On AWS
Lambda, `boto3` is provided by the runtime; bundle only packages the runtime
does not provide.

To build a Lambda Layer, zip the contents of this directory under a `python/`
folder:

```bash
mkdir -p layer/python
cp -R pip-modules/. layer/python/
cd layer && zip -r ../../pip-modules-layer.zip python
```
