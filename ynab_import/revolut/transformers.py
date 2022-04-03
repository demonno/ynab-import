from dataclasses import replace
from typing import List

from ynab_import.common.models import YnabTransaction
from ynab_import.common.transformers import Transformer
from ynab_import.revolut.models import RevolutTransaction


class RevolutTransformer(Transformer):
    """Data transformation From Revolut To Ynab"""

    SKIP_KEYWORDS = ["Metal Cashback"]

    def prepare_data(self, transaction: RevolutTransaction) -> RevolutTransaction:
        paid_out_eur = (
            self.ynab_amount(transaction.paid_out_eur)
            if transaction.paid_out_eur
            else ""
        )
        paid_in_eur = (
            self.ynab_amount(transaction.paid_in_eur) if transaction.paid_in_eur else ""
        )
        description = transaction.description.strip()
        notes = transaction.notes.strip()
        return replace(
            transaction,
            description=description,
            notes=notes,
            paid_out_eur=paid_out_eur,
            paid_in_eur=paid_in_eur,
        )

    def transform(
        self, transactions: List[RevolutTransaction]
    ) -> List[YnabTransaction]:
        res = []
        for tr in transactions:
            if tr.description.strip() in self.SKIP_KEYWORDS:
                continue
            tr = self.prepare_data(tr)
            amount = tr.paid_in_eur or -1 * tr.paid_out_eur
            import_id = self.generate_import_id(
                self.account_id, amount, tr.completed_date.isoformat(),
            )
            res.append(
                YnabTransaction(
                    account_id=self.account_id,
                    date=tr.completed_date.isoformat(),
                    amount=amount,
                    payee_name=tr.description,
                    memo=tr.notes,
                    cleared=None,
                    approved=False,
                    flag_color="green",
                    import_id=import_id,
                )
            )
        return res
