from typing import List

from dataclass_csv import DataclassReader

from ynab_import.common.providers import CSVReader
from ynab_import.core.interactions import Transaction
from ynab_import.revolut.models import RevolutTransaction


class RevolutCSVReader(CSVReader):
    COMPLETED_DATE = "Completed Date "
    DESCRIPTION = " Description "
    PAID_OUT_EUR = " Paid Out (EUR) "
    PAID_IN_EUR = " Paid In (EUR) "
    EXCHANGE_OUT = " Exchange Out"
    EXCHANGE_IN = " Exchange In"
    BALANCE_EUR = " Balance (EUR)"
    CATEGORY = " Category"
    NOTES = " Notes"

    SKIP_KEYWORDS = ["Metal Cashback"]

    def read_transactions(self, input_file: str) -> List[Transaction]:
        with open(input_file, "r", encoding="utf8") as f:
            reader = DataclassReader(
                f, RevolutTransaction, delimiter=",", quotechar='"'
            )
            reader.map(self.COMPLETED_DATE).to("completed_date")
            reader.map(self.DESCRIPTION).to("description")
            reader.map(self.PAID_OUT_EUR).to("paid_out_eur")
            reader.map(self.PAID_IN_EUR).to("paid_in_eur")
            reader.map(self.EXCHANGE_OUT).to("exchange_out")
            reader.map(self.EXCHANGE_IN).to("exchange_in")
            reader.map(self.BALANCE_EUR).to("balance_eur")
            reader.map(self.CATEGORY).to("category")
            reader.map(self.NOTES).to("notes")
            transactions = list(reader)

        return [
            self._make(tr) for tr in transactions if tr.memo not in self.SKIP_KEYWORDS
        ]

    def _make(self, transaction: RevolutTransaction) -> Transaction:
        amount = self.to_amount(transaction.amount)
        if transaction.debit_credit == "D":
            amount = amount * -1

        return Transaction(
            date=transaction.date,
            amount=amount,
            payee_name=transaction.payee,
            description=transaction.notes,
        )
