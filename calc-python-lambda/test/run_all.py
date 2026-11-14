"""Run every unit test under test/unit as a plain Python file.

Usage:
    python3 test/run_all.py

Exits 0 when all tests pass, 1 otherwise.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIP_MODULES = os.path.join(PROJECT_ROOT, "pip-modules")
for _path in (PIP_MODULES, PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

sys.pycache_prefix = os.path.join(PIP_MODULES, ".pycache")

suite = unittest.TestLoader().discover(
    os.path.join(PROJECT_ROOT, "test", "unit"),
    top_level_dir=PROJECT_ROOT,
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
