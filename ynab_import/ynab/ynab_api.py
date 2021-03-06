from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List
from urllib.parse import urljoin

import requests
from requests import Response

from ynab_import.common.models import YnabTransaction


class YnabClient(ABC):  # pragma: no cover
    @abstractmethod
    def create_transactions(self, transactions: List[YnabTransaction]) -> int:
        pass


@dataclass
class YnabApi(YnabClient):
    api_key: str
    budget_id: str
    api_url: str = "https://api.youneedabudget.com/v1/"
    timeout: float = 5.0

    def __post_init__(self):
        assert self.api_key, "Invalid api_key"
        assert self.budget_id, "Invalid budget_id"

    def create_transactions(self, transactions: List[YnabTransaction]) -> int:
        transactions = [t.to_dict() for t in transactions]
        data = {"transactions": transactions}
        response = self._request(
            f"budgets/{self.budget_id}/transactions", "POST", json=data
        )
        response.raise_for_status()
        return response.status_code

    def _request(self, endpoint: str, method: str, **kwargs: Any,) -> Response:
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("headers", {"Authorization": f"Bearer {self.api_key}"})

        return requests.request(
            method, urljoin(self.api_url, endpoint), **kwargs,
        )