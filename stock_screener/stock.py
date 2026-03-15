import logging
from pprint import pformat
from typing import Optional
from metrics import METRICS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Stock:
    def __init__(self, ticker, data=None):
        self.ticker = ticker
        self.data = data
        # TODO: Make rate data computation dynamic based on user input of metrics to compute
        # TODO: Add caching of computed metrics up to a date to avoid redundant calculations
        self.rate_data = {
            "forwardPE": self.compute_metric(METRICS["forwardPE"]),
            "cps": self.compute_metric(METRICS["cps"]),
            "roc": self.compute_metric(METRICS["roc"])
        }
        logging.info(pformat(self.rate_data))

    def compute_metric(self, metric_config: dict) -> float | None:
        source = self.data.get(metric_config["source"], {})
        raw = source.get(metric_config["field"])
        if raw is None:
            return None
        return metric_config["transform"](raw)

    def get_one_year_ago_price(self) -> Optional[float]:
        try:
            if self.data and 'history' in self.data:
                hist_data = self.data['history']
                if isinstance(hist_data, dict):
                    hist_df = hist_data
                    if not hist_df.empty:
                        one_year_ago_price = hist_df['close'].iloc[0]
                        logging.info(f"One year ago price for {self.ticker}: {one_year_ago_price}")
                        return one_year_ago_price
            logging.warning(f"One year ago price not found for {self.ticker}")
            return None
        except Exception as e:
            logging.error(f"Error getting one year ago price for {self.ticker}: {e}")
            return None

    def get_current_price(self) -> Optional[float]:
        try:
            if self.data and 'price' in self.data:
                price_data = self.data['price']
                if isinstance(price_data, dict):
                    current_price = price_data.get('regularMarketPrice')
                    if current_price is not None:
                        logging.info(f"Current price for {self.ticker}: {current_price}")
                        return current_price
            logging.warning(f"Current price not found for {self.ticker}")
            return None
        except Exception as e:
            logging.error(f"Error getting current price for {self.ticker}: {e}")
            return None