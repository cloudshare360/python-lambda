"""Run all unit tests as a plain Python file.

Usage:
    python3 test/run_all.py

Discovers every test under `test/unit` and exits non-zero on failure.
No AWS credentials or network access are required.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _path in (os.path.join(PROJECT_ROOT, "pip-modules"), os.path.join(PROJECT_ROOT, "src"), PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

sys.pycache_prefix = os.path.join(PROJECT_ROOT, "pip-modules", ".pycache")


def main() -> int:
    suite = unittest.TestLoader().discover(
        os.path.join(PROJECT_ROOT, "test", "unit"),
        top_level_dir=PROJECT_ROOT,
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
