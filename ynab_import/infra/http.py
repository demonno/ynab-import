from dataclasses import dataclass
from typing import Any, Dict, Protocol, TypeVar

import requests
from requests import Response

T = TypeVar("T")


class HttpClient(Protocol[T]):
    def post(self, endpoint: str, *, json: Dict[str, Any]) -> T:
        ...


@dataclass
class RequestsClient:
    def __init__(self):
        self.base_url: str = ""
        self.kwargs: Dict[str, Any] = {}

    def with_base_url(self, base_url: str) -> "RequestsClient":
        self.base_url = base_url

        return self

    def with_timeout(self, timeout: float) -> "RequestsClient":
        self.kwargs.setdefault("timeout", timeout)

        return self

    def with_header(self, key: str, value: str) -> "RequestsClient":
        headers = self.kwargs.setdefault("headers", {})
        headers[key] = value

        return self

    def with_api_key_auth(self, api_key: str) -> "RequestsClient":
        self.with_header("Authorization", f"Bearer {api_key}")

        return self

    def request(self, method: str, endpoint: str, **kwargs: Any) -> Response:
        url = f'{self.base_url.rstrip("/")}/{endpoint.lstrip("/")}'
        return requests.request(method, url, **kwargs, **self.kwargs)

    def post(self, endpoint: str, *, json: Dict[str, Any]) -> Response:
        return self.request("POST", endpoint, json=json)
