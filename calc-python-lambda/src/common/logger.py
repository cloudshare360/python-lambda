"""Logger factory.

`get_logger` configures DEBUG logging once. On Lambda the runtime forwards
stdout to CloudWatch; locally the same records print to the terminal.
"""

import logging

from src.config.settings import settings

_CONFIGURED = False


def get_logger(name):
    """Return a logger configured for the application."""
    global _CONFIGURED
    if not _CONFIGURED:
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG)
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        _CONFIGURED = True
    return logging.getLogger(name)
