from typing import List

from dataclass_csv import DataclassReader

from ynab_import.common.providers import CSVProvider
from ynab_import.swedbank.models import SwedbankTransaction


class SwedbankCSVProvider(CSVProvider):
    CLIENT_ACCOUNT = "Client account"
    DATE = "Date"
    PAYEE = "Beneficiary/Payer"
    MEMO = "Details"
    AMOUNT = "Amount"
    DEBIT_CREDIT = "Debit/Credit"

    def read_csv(self, input_file: str) -> List[SwedbankTransaction]:
        with open(input_file, "r", encoding="utf8") as f:
            reader = DataclassReader(
                f, SwedbankTransaction, delimiter=";", quotechar='"'
            )
            reader.map(self.CLIENT_ACCOUNT).to("client_account")
            reader.map(self.DATE).to("date")
            reader.map(self.PAYEE).to("payee")
            reader.map(self.MEMO).to("memo")
            reader.map(self.AMOUNT).to("amount")
            reader.map(self.DEBIT_CREDIT).to("debit_credit")
            return list(reader)
