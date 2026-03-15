import logging
import random
import pandas as pd
from datetime import date, timedelta
from time import sleep
from typing import Optional
from yahooquery import Ticker

from ..providers.base import DataProvider
from ..metrics import METRICS


class HistoricalProvider(DataProvider):
    def __init__(
        self,
        backtest_date: date,
        batch_size: int = 10,
        max_retries: int = 3,
        sleep_min: float = 3,
        sleep_max: float = 7,
        backoff_min: float = 5,
        backoff_max: float = 10,
    ):
        self.backtest_date = backtest_date
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.sleep_min = sleep_min
        self.sleep_max = sleep_max
        self.backoff_min = backoff_min
        self.backoff_max = backoff_max

    def fetch(self, tickers: list[str]) -> dict[str, dict]:
        result = {}
        for i in range(0, len(tickers), self.batch_size):
            batch = tickers[i:i + self.batch_size]
            result.update(self._fetch_batch(batch))
        return result

    def _fetch_batch(self, batch: list[str]) -> dict[str, dict]:
        for retry in range(self.max_retries):
            try:
                t = Ticker(batch)
                sleep(random.uniform(self.sleep_min, self.sleep_max))

                balance_sheets = self._safe_fetch(t, "balance_sheet", frequency="q")
                income_statements = self._safe_fetch(t, "income_statement", frequency="q")
                price_history = t.history(
                    start=str(self.backtest_date),
                    end=str(self.backtest_date + timedelta(days=7))
                )

                result = {}
                for ticker in batch:
                    try:
                        bs = self._closest_filing(balance_sheets, ticker)
                        inc = self._closest_filing(income_statements, ticker)
                        price = self._price_at_date(price_history, ticker)

                        financial_data, summary_detail = self._derive_all(bs, inc, price)

                        result[ticker] = {
                            "financial_data": financial_data,
                            "summary_detail": summary_detail,
                            "price": {"regularMarketPrice": price},
                        }
                    except Exception as e:
                        logging.warning(f"Skipping {ticker}. Could not build historical data: {e}")

                logging.info(f"Successfully fetched historical data for batch: {batch}")
                return result

            except Exception as e:
                logging.error(f"Attempt {retry + 1} failed for batch {batch}: {e}")
                if retry < self.max_retries - 1:
                    backoff_time = (2 ** retry) * random.uniform(self.backoff_min, self.backoff_max)
                    logging.info(f"Waiting {backoff_time:.2f} seconds before retry...")
                    sleep(backoff_time)
                else:
                    logging.error(f"Max retries exceeded for batch {batch}, skipping.")
                    return {}

    def _safe_fetch(self, ticker_obj: Ticker, method: str, **kwargs) -> pd.DataFrame:
        try:
            data = getattr(ticker_obj, method)(**kwargs)
            if isinstance(data, pd.DataFrame):
                return data
            logging.warning(f"Unexpected type for {method}: {type(data)}")
            return pd.DataFrame()
        except Exception as e:
            logging.warning(f"Failed to fetch {method}: {e}")
            return pd.DataFrame()

    def _closest_filing(self, df: pd.DataFrame, ticker: str) -> dict:
        if df.empty:
            return {}

        if isinstance(df.index, pd.MultiIndex):
            if ticker not in df.index.get_level_values(0):
                return {}
            ticker_df = df.loc[ticker]
        else:
            ticker_df = df[df["symbol"] == ticker] if "symbol" in df.columns else df

        if ticker_df.empty:
            return {}

        date_col = next((c for c in ["asOfDate", "endDate", "date"] if c in ticker_df.columns), None)
        if date_col is None:
            return {}

        ticker_df = ticker_df.copy()
        ticker_df[date_col] = pd.to_datetime(ticker_df[date_col]).dt.date
        valid = ticker_df[ticker_df[date_col] <= self.backtest_date]

        if valid.empty:
            return {}

        max_date = valid[date_col].max()
        row = valid[valid[date_col] == max_date].iloc[0]
        return row.to_dict()

    def _price_at_date(self, history: pd.DataFrame, ticker: str) -> float | None:
        if history is None or history.empty:
            return None
        try:
            if isinstance(history.index, pd.MultiIndex):
                if ticker not in history.index.get_level_values(0):
                    return None
                ticker_history = history.loc[ticker]
            else:
                ticker_history = history[history["symbol"] == ticker]

            if ticker_history.empty:
                return None
            return float(ticker_history["close"].iloc[0])
        except Exception as e:
            logging.warning(f"Could not get price for {ticker}: {e}")
            return None

    def _derive_all(self, bs: dict, inc: dict, price: float | None) -> tuple[dict, dict]:
        financial_data = {}
        summary_detail = {}

        for metric in METRICS.values():
            derive = metric.get("historical_derive")
            if derive is None:
                continue
            value = derive(bs, inc, price)
            if value is None:
                continue
            target = financial_data if metric["source"] == "financial_data" else summary_detail
            target[metric["field"]] = value

        return financial_data, summary_detail
