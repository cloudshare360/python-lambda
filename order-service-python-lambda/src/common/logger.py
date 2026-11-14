"""Logger factory.

`get_logger` returns a DEBUG-level logger. On Lambda the logs are captured by the
runtime and written to CloudWatch; locally they print to the terminal.
"""

import logging

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    global _CONFIGURED
    if not _CONFIGURED:
        logging.basicConfig(level=logging.DEBUG)
        _CONFIGURED = True
    return logging.getLogger(name)
