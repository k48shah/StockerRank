from abs import ABC, abstractmethod

class DataProvider(ABC):
    @abstractmethod
    def fetch_data(self, ticker: str) -> dict:
        pass