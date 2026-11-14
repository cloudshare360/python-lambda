"""CloudWatch-friendly logger factory.

`get_logger` configures each named logger exactly once. The default level is
DEBUG (or `LOG_LEVEL` from the environment), and records are kept out of the
root logger so a Lambda invocation emits a single stream. On AWS Lambda these
records land in `/aws/lambda/<function-name>`.
"""

import logging

from src.config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(handler)
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG)
        logger.setLevel(level)
        logger.propagate = False
    return logger
