from typing import List

import requests

from ynab_import.common import settings
from ynab_import.common.models import YnabTransaction
from ynab_import.common.providers import APIProvider


class YnabBudget(APIProvider):
    def __init__(self, api_key: str, budget_id: str) -> None:
        self.api_key = api_key
        self.budget_id = budget_id

    def create_transactions(self, transactions: List[YnabTransaction]) -> int:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        transactions = [t.to_dict() for t in transactions]
        data = {"transactions": transactions}
        response = requests.post(
            settings.YNAB_API_BASE_URL + f"budgets/{self.budget_id}/transactions",
            json=data,
            headers=headers,
        )
        if response.status_code != 200:
            print(response.json())
        response.raise_for_status()
        return response.status_code
