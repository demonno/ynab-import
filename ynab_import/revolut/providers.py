from typing import List

from dataclass_csv import DataclassReader

from ynab_import.common.providers import CSVProvider
from ynab_import.revolut.models import RevolutTransaction


class RevolutCSVProvider(CSVProvider):
    COMPLETED_DATE = "Completed Date "
    DESCRIPTION = " Description "
    PAID_OUT_EUR = " Paid Out (EUR) "
    PAID_IN_EUR = " Paid In (EUR) "
    EXCHANGE_OUT = " Exchange Out"
    EXCHANGE_IN = " Exchange In"
    BALANCE_EUR = " Balance (EUR)"
    CATEGORY = " Category"
    NOTES = " Notes"

    def read_csv(self, input_file: str) -> List[RevolutTransaction]:
        with open(input_file, "r", encoding="utf8") as f:
            reader = DataclassReader(
                f, RevolutTransaction, delimiter=";", quotechar='"'
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
            return list(reader)
