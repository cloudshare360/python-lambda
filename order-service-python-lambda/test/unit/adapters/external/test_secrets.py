"""Secret server adapter unit tests (injected transport/client, no network)."""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
for _path in (os.path.join(PROJECT_ROOT, "pip-modules"), PROJECT_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from src.adapters.external.secret_server.restapi.client import RestClient
from src.adapters.external.secret_server.restapi.secrets import SecretServerClient
from src.common.errors import IntegrationError


class RecordingClient:
    def __init__(self):
        self.calls = []

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        return {"ok": True, "path": path}


class SecretServerClientTest(unittest.TestCase):
    def test_get_create_rotate_map_to_paths(self):
        recording = RecordingClient()
        client = SecretServerClient(base_url="http://secret", client=recording)

        self.assertEqual(client.get_secret("external-api-key"), {"ok": True, "path": "/secrets/external-api-key"})
        self.assertEqual(
            client.create_secret({"name": "x", "value": "y"}),
            {"ok": True, "path": "/secrets"},
        )
        self.assertEqual(
            client.rotate_secret("external-api-key"),
            {"ok": True, "path": "/secrets/external-api-key/rotate"},
        )
        self.assertEqual(
            recording.calls,
            [
                ("GET", "/secrets/external-api-key", None),
                ("POST", "/secrets", {"name": "x", "value": "y"}),
                ("POST", "/secrets/external-api-key/rotate", None),
            ],
        )


class RestClientTest(unittest.TestCase):
    def test_sends_bearer_token_and_parses_json(self):
        seen = {}

        def transport(method, url, headers, body):
            seen["method"] = method
            seen["url"] = url
            seen["headers"] = headers
            seen["body"] = body
            return 200, b'{"api_key": "abc"}'

        rest = RestClient("http://secret", token="tok", transport=transport)

        self.assertEqual(rest.request("GET", "/secrets/k"), {"api_key": "abc"})
        self.assertEqual(seen["url"], "http://secret/secrets/k")
        self.assertEqual(seen["headers"]["Authorization"], "Bearer tok")

    def test_retries_transport_errors_then_succeeds(self):
        attempts = {"count": 0}

        def transport(method, url, headers, body):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise OSError("connection reset")
            return 200, b"{}"

        rest = RestClient("http://secret", retries=2, transport=transport)

        self.assertEqual(rest.request("GET", "/secrets/k"), {})
        self.assertEqual(attempts["count"], 3)

    def test_retries_5xx_then_succeeds(self):
        statuses = iter([503, 200])

        def transport(method, url, headers, body):
            return next(statuses), b"{}"

        rest = RestClient("http://secret", retries=1, transport=transport)

        self.assertEqual(rest.request("GET", "/secrets/k"), {})

    def test_client_error_raises_integration_error(self):
        rest = RestClient(
            "http://secret", retries=0, transport=lambda *args: (404, b"missing")
        )
        with self.assertRaises(IntegrationError):
            rest.request("GET", "/secrets/k")

    def test_exhausted_retries_raise_integration_error(self):
        def transport(method, url, headers, body):
            raise OSError("down")

        rest = RestClient("http://secret", retries=1, transport=transport)
        with self.assertRaises(IntegrationError):
            rest.request("GET", "/secrets/k")


if __name__ == "__main__":
    unittest.main()
