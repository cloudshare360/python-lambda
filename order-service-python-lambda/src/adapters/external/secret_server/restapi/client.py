"""Base REST client for external vendors.

Stdlib `urllib` only. Supports a configurable timeout, bounded retries (on
transport errors and 5xx responses), and an injectable `transport` so tests can
run with no network.

A transport is any callable:
    transport(method, url, headers, body) -> (status_code: int, body: bytes)
"""

import json
import logging
import time
from urllib import error, request

from src.common.errors import IntegrationError

logger = logging.getLogger(__name__)


def urllib_transport(method, url, headers, body, timeout):
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read()
    except error.HTTPError as exc:
        return exc.code, exc.read()


class RestClient:
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 5.0,
        retries: int = 2,
        backoff: float = 0.0,
        transport=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._transport = transport or self._default_transport

    def _default_transport(self, method, url, headers, body):
        return urllib_transport(method, url, headers, body, self.timeout)

    def _headers(self) -> dict:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = self._headers()
        last_error = None

        for attempt in range(self.retries + 1):
            try:
                status, raw = self._transport(method, url, headers, payload)
            except Exception as exc:
                last_error = exc
                logger.debug(
                    "RestClient %s %s attempt %s failed: %s", method, url, attempt + 1, exc
                )
                if attempt < self.retries:
                    if self.backoff:
                        time.sleep(self.backoff * (attempt + 1))
                    continue
                break

            if 500 <= status < 600 and attempt < self.retries:
                last_error = IntegrationError(f"HTTP {status} from {method} {url}")
                logger.debug("RestClient %s %s got %s, retrying", method, url, status)
                if self.backoff:
                    time.sleep(self.backoff * (attempt + 1))
                continue

            if status >= 400:
                raise IntegrationError(f"HTTP {status} from {method} {url}: {raw!r}")

            if not raw:
                return {}
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode("utf-8")
            return json.loads(raw)

        raise IntegrationError(f"Request failed for {method} {url}: {last_error}")
