from dataclasses import dataclass
from typing import List

from dataclass_csv import DataclassReader

from ynab_import.common.providers import CSVReader
from ynab_import.core.interactions import Transaction
from ynab_import.swedbank.models import SwedbankTransaction


@dataclass
class SwedbankCSVReader(CSVReader):
    CLIENT_ACCOUNT = "Client account"
    DATE = "Date"
    PAYEE = "Beneficiary/Payer"
    MEMO = "Details"
    AMOUNT = "Amount"
    DEBIT_CREDIT = "Debit/Credit"

    SKIP_KEYWORDS = ["closing balance", "Turnover", "Opening balance"]

    source_file_path: str

    def read_transactions(self) -> List[Transaction]:
        with open(self.source_file_path, "r", encoding="utf8") as f:
            reader = DataclassReader(
                f, SwedbankTransaction, delimiter=";", quotechar='"'
            )
            reader.map(self.CLIENT_ACCOUNT).to("client_account")
            reader.map(self.DATE).to("date")
            reader.map(self.PAYEE).to("payee")
            reader.map(self.MEMO).to("memo")
            reader.map(self.AMOUNT).to("amount")
            reader.map(self.DEBIT_CREDIT).to("debit_credit")
            swedbank_transactions = list(reader)
        return [
            self._make(tr)
            for tr in swedbank_transactions
            if tr.memo not in self.SKIP_KEYWORDS
        ]

    def _make(self, transaction: SwedbankTransaction) -> Transaction:
        amount = self.to_amount(transaction.amount)
        if transaction.debit_credit == "D":
            amount = amount * -1

        return Transaction(
            date=transaction.date,
            amount=amount,
            payee_name=transaction.payee,
            description=transaction.memo,
        )
