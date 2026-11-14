"""Response serialization (the View layer).

`build_response` turns a status code and body into the Lambda proxy response
shape. It contains no business logic.
"""

import json


def build_response(status, body):
    """Build a Lambda proxy response with a JSON body."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
