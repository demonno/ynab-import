from collections import Counter
from typing import List

from ynab_import.common.models import Transaction, YnabTransaction
from ynab_import.swedbank.models import SwedbankTransaction


class Transformer(object):
    def __init__(self, account_id: str) -> None:
        self.counter = Counter()
        self.account_id = account_id

    def _to_milliunit(self, amount: float) -> int:
        return int(amount * 1000)

    def _to_float(self, amount: str) -> float:
        return float(amount.replace(",", "."))

    def ynab_amount(self, amount: str) -> int:
        return self._to_milliunit(self._to_float(amount))

    def generate_import_id(self, client_account: str, amount: str, iso_date: str):
        import_id = "YNAB:{milliunit_amount}:{iso_date}:{occurrence}".format(
            milliunit_amount=amount, iso_date=iso_date, occurrence=self.counter[(client_account, amount, iso_date)],
        )
        self.counter[(client_account, amount, iso_date)] += 1
        return import_id

    def prepare_data(self, swedbank: SwedbankTransaction) -> SwedbankTransaction:
        raise NotImplemented

    def to_ynab_transactions(self, transactions: List[Transaction]) -> List[YnabTransaction]:
        raise NotImplemented
