from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock

from ynab_import.core.interactions import Transaction
from ynab_import.infra.ynab import YnabAPIBasedRepository


class FakeHttpClient:
    def __init__(self) -> None:
        self.posted_bodies: List[Dict[str, Any]] = []

    def post(self, endpoint: str, *, json: Dict[str, Any]):
        self.posted_bodies.append(json)
        response = MagicMock()
        response.json.return_value = {}
        response.status_code = 200
        return response


def test_import_id_counter_suffixes_collisions():
    client = FakeHttpClient()
    repo = YnabAPIBasedRepository(
        http_client=client,
        budget_id="budget-1",
        account_id="account-1",
    )

    same_day = datetime(2026, 4, 19)
    transactions = [
        Transaction(date=same_day, amount=-1500, payee_name="Coffee", description="a"),
        Transaction(date=same_day, amount=-1500, payee_name="Coffee", description="b"),
        Transaction(date=same_day, amount=-2000, payee_name="Lunch", description="c"),
    ]

    repo.create_many(transactions)

    assert len(client.posted_bodies) == 1
    sent = client.posted_bodies[0]["transactions"]
    assert [t["import_id"] for t in sent] == [
        "YNAB:-1500:2026-04-19T00:00:00:0",
        "YNAB:-1500:2026-04-19T00:00:00:1",
        "YNAB:-2000:2026-04-19T00:00:00:0",
    ]
