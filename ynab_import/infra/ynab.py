from dataclasses import asdict, dataclass
from pprint import pprint
from typing import List

from requests import Response

from ynab_import.common.models import YnabTransaction
from ynab_import.core.interactions import Transaction
from ynab_import.infra.http import HttpClient


@dataclass
class YnabAPIBasedRepository:
    http_client: HttpClient[Response]
    budget_id: str
    account_id: str

    def create_many(self, transactions: List[Transaction]) -> int:
        ynab_transactions = [asdict(self._to_ynab(t)) for t in transactions]
        pprint(ynab_transactions)
        response = self.http_client.post(
            f"/budgets/{self.budget_id}/transactions",
            json={"transactions": ynab_transactions},
        )

        print(response.json())
        response.raise_for_status()
        return response.status_code

    def _to_ynab(self, transaction: Transaction) -> YnabTransaction:
        import_id = "YNAB:{milliunit_amount}:{iso_date}".format(
            milliunit_amount=transaction.amount, iso_date=transaction.date.isoformat(),
        )

        return YnabTransaction(
            account_id=self.account_id,
            date=transaction.date.isoformat(),
            amount=str(transaction.amount),
            payee_name=transaction.payee_name,
            memo=transaction.description,
            cleared="cleared",
            approved=False,
            flag_color="red",
            import_id=import_id,
        )


@dataclass
class InMemoryBasedRepository:
    transactions: List[Transaction]

    def create_many(self, transactions: List[Transaction]) -> int:
        for transaction in transactions:
            self.transactions.append(transaction)
        return len(self.transactions)
