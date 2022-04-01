from dataclasses import dataclass
from datetime import datetime
from typing import List, Protocol


@dataclass
class Transaction:
    date: datetime
    amount: int
    payee_name: str
    description: str


class IWriteRepository(Protocol):
    def create_many(self, transactions: List[Transaction]) -> int:
        ...


class IReadRepository(Protocol):
    def read_transactions(self) -> List[Transaction]:
        ...


def import_transactions(read: IReadRepository, write: IWriteRepository) -> int:
    return write.create_many(read.read_transactions())
