from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass
class Transaction(object):
    pass


@dataclass_json
@dataclass
class YnabTransaction(Transaction):
    account_id: str
    date: str
    amount: str
    # payee_id: str #not used
    payee_name: str
    # category_id: str #not used
    memo: str
    import_id: str

    cleared: Optional[str] = None
    approved: bool = False
    flag_color: str = "green"
