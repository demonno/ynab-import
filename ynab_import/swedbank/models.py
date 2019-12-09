from dataclasses import dataclass
from datetime import datetime

from dataclass_csv import accept_whitespaces, dateformat

from ynab_import.common.models import Transaction


@accept_whitespaces
@dataclass
@dateformat("%d.%m.%Y")
class SwedbankTransaction(Transaction):
    client_account: str
    date: datetime
    memo: str
    amount: str
    debit_credit: str
    payee: str = ""
