#!/usr/bin/env bash
# Post-create setup for python-lambda devcontainer

set -euo pipefail

echo "=== python-lambda devcontainer setup ==="

echo "Python: $(python3 --version)"
echo "pip: $(pip3 --version)"

for proj in calc-python-lambda order-service-python-lambda string-utils-python-lambda; do
  if [ -d "$proj" ]; then
    echo ""
    echo "--- Setting up $proj ---"
    cd "$proj"
    if [ -f requirements.txt ]; then
      echo "Installing deps from requirements.txt..."
      pip3 install --user -r requirements.txt 2>/dev/null || true
    fi
    if [ -d pip-modules ]; then
      echo "pip-modules/ present (no pip install needed for stdlib-only projects)"
    fi
    echo "Running unit tests..."
    python3 test/run_all.py
    cd ..
  fi
done

echo ""
echo "=== Setup complete. You can now run: ==="
echo "  cd calc-python-lambda && python3 src/lambda_function.py"
echo "  cd string-utils-python-lambda && python3 src/lambda_function.py"
echo "  cd order-service-python-lambda && python3 src/lambda_function.py"
echo ""
echo "All three projects are ready for local development and testing."