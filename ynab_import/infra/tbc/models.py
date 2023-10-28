from dataclasses import dataclass
from datetime import datetime


@dataclass
class TBCTransaction:
    date: datetime
    description: str
    paid_out: str
    paid_in: str
    partners_name: str
