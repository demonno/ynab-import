import csv
from dataclasses import dataclass
from datetime import datetime
from typing import List

from ynab_import.core.interactions import Transaction
from ynab_import.core.providers import CSVReader
from ynab_import.infra.tbc.models import TBCTransaction


@dataclass
class TBCCSVReader(CSVReader):
    SKIP_KEYWORDS = ["კონვერტაცია", "Currency Exchange", "Transfer between your accounts"]
    source_file_path: str
    exchange_rate: float = 2.9112

    def read_transactions(self) -> List[Transaction]:
        with open(self.source_file_path, "r", encoding="utf8") as f:
            data = csv.DictReader(f, delimiter=",")
            transactions: list[TBCTransaction] = []
            # SKIP the first row of headers(English Version)
            _ = next(data)
            for row in data:
                tr = TBCTransaction(
                    date=datetime.strptime(row[list(row.keys())[0]], "%d/%m/%Y"),
                    description=row["დანიშნულება"],
                    paid_in=row["შემოსული თანხა"],
                    paid_out=row["გასული თანხა"],
                    partners_name=row["პარტნიორი"],
                )
                transactions.append(tr)
        return [
            self._to_internal_transaction(tr)
            for tr in transactions
            if not any(tr.description.startswith(keyword) for keyword in self.SKIP_KEYWORDS)
        ]

    def _to_internal_transaction(self, transaction: TBCTransaction) -> Transaction:

        if transaction.paid_in:
            amount_float = self.to_float(transaction.paid_in)
        else:
            amount_float = self.to_float(transaction.paid_out) * -1

        amount_eur = self.convert_to_eur(amount_float)
        amount = self.to_milliunit(amount_eur)

        return Transaction(
            date=transaction.date,
            amount=amount,
            payee_name=transaction.partners_name,
            description=transaction.description,
        )

    def convert_to_eur(self, amount: float) -> float:
        return amount / self.exchange_rate
