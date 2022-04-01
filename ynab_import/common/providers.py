from abc import ABC, abstractmethod


class CSVReader(ABC):  # pragma: no cover
    @abstractmethod
    def read_transactions(self):
        pass

    @staticmethod
    def _to_milliunit(amount: float) -> int:
        return int(amount * 1000)

    @staticmethod
    def _to_float(amount: str) -> float:
        return float(amount.replace(",", "."))

    def to_amount(self, amount: str) -> int:
        if not amount.strip():
            return 0
        return self._to_milliunit(self._to_float(amount))
