from dataclasses import dataclass
from typing import Optional


@dataclass
class YnabTransaction:
    account_id: str
    date: str
    amount: str
    payee_name: str
    memo: str
    import_id: str

    cleared: Optional[str] = None
    approved: bool = False
    flag_color: str = "green"
