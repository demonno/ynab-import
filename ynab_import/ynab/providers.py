from typing import List

import requests

from ynab_import.common.models import YnabTransaction

from ynab_import.common import settings
from ynab_import.common.providers import APIProvider


class YnabBudget(APIProvider):
    def __init__(self) -> None:
        self.api_key = settings.YNAB_API_KEY
        self.budget_id = settings.YNAB_BUDGET_ID

    def create_transactions(self, transactions: List[YnabTransaction]) -> int:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        transactions = list(map(lambda x: x.to_dict(), transactions))
        data = {"transactions": transactions}
        response = requests.post(
            settings.YNAB_API_BASE_URL + f"budgets/{self.budget_id}/transactions", json=data, headers=headers,
        )
        if response.status_code != 200:
            print(response.json())
        response.raise_for_status()
        return response.status_code
