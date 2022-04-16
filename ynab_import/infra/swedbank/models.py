from dataclasses import dataclass
from datetime import datetime

from dataclass_csv import accept_whitespaces, dateformat


@accept_whitespaces
@dataclass
@dateformat("%d.%m.%Y")
class SwedbankTransaction:
    client_account: str
    date: datetime
    memo: str
    amount: str
    debit_credit: str
    payee: str = ""
