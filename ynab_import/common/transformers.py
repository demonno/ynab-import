import abc
from collections import Counter
from typing import List

from ynab_import.common.models import YnabTransaction
from ynab_import.core.interactions import Transaction


class Transformer(abc.ABC):
    def __init__(self, account_id: str) -> None:
        self.counter: Counter = Counter()
        self.account_id = account_id

    @staticmethod
    def _to_milliunit(amount: float) -> int:
        return int(amount * 1000)

    @staticmethod
    def _to_float(amount: str) -> float:
        return float(amount.replace(",", "."))

    def ynab_amount(self, amount: str) -> int:
        if not amount.strip():
            return 0
        return self._to_milliunit(self._to_float(amount))

    def generate_import_id(self, account_id: str, amount: str, iso_date: str):
        import_id = "YNAB:{milliunit_amount}:{iso_date}:{occurrence}".format(
            milliunit_amount=amount,
            iso_date=iso_date,
            occurrence=self.counter[(account_id, amount, iso_date)],
        )
        self.counter[(account_id, amount, iso_date)] += 1
        return import_id

    @abc.abstractmethod
    def prepare_data(self, transaction: Transaction) -> Transaction:
        raise NotImplementedError

    @abc.abstractmethod
    def transform(self, transactions: List[Transaction]) -> List[YnabTransaction]:
        raise NotImplementedError
