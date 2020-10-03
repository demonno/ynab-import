from dataclasses import dataclass
from datetime import datetime

from dataclass_csv import accept_whitespaces, dateformat

from ynab_import.common.models import Transaction


@accept_whitespaces
@dataclass
@dateformat("%b %d, %Y ")
class RevolutTransaction(Transaction):
    completed_date: datetime
    description: str
    paid_out_eur: str
    paid_in_eur: str
    exchange_out: str
    exchange_in: str
    balance_eur: str
    category: str
    notes: str = ""
