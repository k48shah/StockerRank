from time import sleep
import random
import logging
from yahooquery import Ticker
from .base import DataProvider

class YahooQueryProvider(DataProvider):
    def __init__(self, batch_size=10, max_retries=3, sleep_min=3, sleep_max=7, backoff_min=5, backoff_max=10):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.sleep_min = sleep_min
        self.sleep_max = sleep_max
        self.backoff_min = backoff_min
        self.backoff_max = backoff_max

    def fetch(self, tickers: list[str]) -> dict[str, dict]:
        result = {}
        for i in range(0, len(tickers), self.batch_size):
            batch = tickers[i:i+self.batch_size]
            batch_data = self._fetch_batch_data(batch)
            result.update(batch_data)
        return result
    
    def _fetch_batch_data(self, batch: list[str]) -> dict[str, dict]:
        for retry in range(self.max_retries):
            try:
                ticker_batch = Ticker(batch)
                logging.info(f"Fetched data for batch: {batch}")
                sleep(random.uniform(self.sleep_min, self.sleep_max))
                summary = ticker_batch.summary_detail
                financial = ticker_batch.financial_data
                price = ticker_batch.price
                return {
                    ticker: {
                        "summary_detail": summary.get(ticker, {}) if isinstance(summary, dict) else {},
                        "financial_data": financial.get(ticker, {}) if isinstance(financial, dict) else {},
                        "price": price.get(ticker, {}) if isinstance(price, dict) else {},
                    } for ticker in batch
                }
            except Exception as e:
                logging.error(f"Attempt {retry + 1} failed for batch {batch}: {e}")
                if retry < self.max_retries - 1:
                    backoff_time = (2 ** retry) * random.uniform(self.backoff_min, self.backoff_max)
                    logging.info(f"Waiting {backoff_time:.2f} seconds before retry...")
                    sleep(backoff_time)
