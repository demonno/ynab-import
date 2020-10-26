from dataclasses import replace
from typing import List

from ynab_import.common.models import YnabTransaction
from ynab_import.common.transformers import Transformer
from ynab_import.swedbank.models import SwedbankTransaction


class SwedBankTransformer(Transformer):
    """Data transformation From Swedbank To Ynab"""

    SKIP_KEYWORDS = ["closing balance", "Turnover", "Opening balance"]

    def prepare_data(self, swedbank: SwedbankTransaction) -> SwedbankTransaction:
        ynab_amount = self.ynab_amount(swedbank.amount)
        if swedbank.debit_credit == "D":
            ynab_amount = str(ynab_amount * -1)
        return replace(swedbank, amount=ynab_amount)

    def to_ynab_transactions(
        self, transactions: List[SwedbankTransaction]
    ) -> List[YnabTransaction]:
        res = []
        for tr in transactions:
            if tr.memo in self.SKIP_KEYWORDS:
                continue
            tr = self.prepare_data(tr)
            import_id = self.generate_import_id(
                self.account_id, tr.amount, tr.date.isoformat(),
            )
            res.append(
                YnabTransaction(
                    account_id=self.account_id,
                    date=tr.date.isoformat(),
                    amount=tr.amount,
                    payee_name=tr.payee,
                    memo=tr.memo,
                    cleared="cleared",
                    approved=False,
                    flag_color="red",
                    import_id=import_id,
                )
            )
        return res
