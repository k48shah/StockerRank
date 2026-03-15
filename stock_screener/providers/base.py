from abc import ABC, abstractmethod

class DataProvider(ABC):
    @abstractmethod
    def fetch(self, tickers: list[str]) -> dict[str, dict]:
        pass