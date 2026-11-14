"""Run every unit test as a plain Python file.

Usage:
    python3 test/run_all.py
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "pip-modules"))
sys.pycache_prefix = os.path.join(PROJECT_ROOT, "pip-modules", ".pycache")

suite = unittest.TestLoader().discover(os.path.join(PROJECT_ROOT, "test", "unit"))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
