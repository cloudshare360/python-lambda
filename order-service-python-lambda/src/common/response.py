"""Response serialization (the View layer).

`build_response` turns a status code and body dict into the Lambda proxy
response shape. It contains no business logic.
"""

import json


def build_response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "body": json.dumps(body),
    }
