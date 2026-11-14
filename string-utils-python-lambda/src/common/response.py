"""View layer: serialize a status code and body into an API-style response."""

import json


def build_response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "body": json.dumps(body),
    }
