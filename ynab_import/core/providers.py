from abc import ABC, abstractmethod


class CSVReader(ABC):  # pragma: no cover
    @abstractmethod
    def read_transactions(self):
        pass

    @staticmethod
    def to_milliunit(amount: float) -> int:
        return int(amount * 1000)

    @staticmethod
    def to_float(amount: str) -> float:
        return float(amount.replace(",", "."))

    def to_amount(self, amount: str) -> int:
        if not amount.strip():
            return 0
        return self.to_milliunit(self.to_float(amount))
