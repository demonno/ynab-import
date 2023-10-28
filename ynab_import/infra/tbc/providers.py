import csv
from dataclasses import dataclass
from datetime import datetime
from typing import List

from ynab_import.core.interactions import Transaction
from ynab_import.core.providers import CSVReader
from ynab_import.infra.tbc.models import TBCTransaction


@dataclass
class TBCCSVReader(CSVReader):
    index_mapping = {
        "Date"
    }
    SKIP_KEYWORDS = ["closing balance", "Turnover", "Opening balance"]

    source_file_path: str

    def read_transactions(self) -> List[Transaction]:
        with open(self.source_file_path, "r", encoding="utf8") as f:
            data = csv.DictReader(f, delimiter=";")
            transactions: list[TBCTransaction] = []
            _ = next(data)
            for row in data:
                tr = TBCTransaction(
                    date=datetime.strptime(row['Date'], "%d/%m/%Y"),
                    description=row['Description'],
                    paid_in=row['Paid In'],
                    paid_out=row['Paid Out'],
                    partners_name=row['Partner\'s Name'],
                )
                transactions.append(tr)
        return [
            self._make(tr)
            for tr in transactions
            if tr.description not in self.SKIP_KEYWORDS
        ]

    def _make(self, transaction: TBCTransaction) -> Transaction:

        if transaction.paid_in:
            amount = self.to_amount(transaction.paid_in)
        if transaction.paid_out:
            amount = self.to_amount(transaction.paid_out) * -1

        return Transaction(
            date=transaction.date,
            amount=amount,
            payee_name=transaction.partners_name,
            description=transaction.description,
        )
