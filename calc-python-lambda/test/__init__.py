"""Test package.

`load_event` is the single helper that maps an event file name under
`test/events/` to a Python dict, keeping event <-> test case mapping obvious.
"""

import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_event(name):
    """Load `test/events/<name>` as a dict."""
    path = os.path.join(PROJECT_ROOT, "test", "events", name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
