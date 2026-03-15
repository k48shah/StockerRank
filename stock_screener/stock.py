import logging
from pprint import pformat
from typing import Optional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Stock:
    def __init__(self, ticker, data=None):
        self.ticker = ticker
        self.data = data
        self.rate_data = {
            "forwardPE": self.get_forward_pe(),
            "cps": self.get_cps(),
            "roc": self.get_roe()
        }
        logging.info(pformat(self.rate_data))

    def get_forward_pe(self) -> Optional[float]:
        try:
            if self.data and 'summary_detail' in self.data:
                summary = self.data['summary_detail']
                if isinstance(summary, dict):
                    forward_pe_raw = summary.get('forwardPE')
                    if forward_pe_raw and forward_pe_raw > 0:
                        forward_pe = 1 / forward_pe_raw * 100
                        logging.info(f"Forward PE for {self.ticker}: {forward_pe}")
                        return forward_pe
            logging.warning(f"Forward PE not found for {self.ticker}")
            return None
        except Exception as e:
            logging.error(f"Error getting Forward PE for {self.ticker}: {e}")
            return None

    def get_cps(self) -> Optional[float]:
        try:
            if self.data and 'financial_data' in self.data:
                financial_data = self.data['financial_data']
                if isinstance(financial_data, dict):
                    cps = financial_data.get('totalCashPerShare')
                    if cps is not None:
                        logging.info(f"CPS for {self.ticker}: {cps}")
                        return cps
            logging.warning(f"CPS not found for {self.ticker}")
            return None
        except Exception as e:
            logging.error(f"Error getting CPS for {self.ticker}: {e}")
            return None

    def get_roe(self) -> Optional[float]:
        try:
            if self.data and 'financial_data' in self.data:
                financial_data = self.data['financial_data']
                if isinstance(financial_data, dict):
                    roe = financial_data.get('returnOnEquity')
                    if roe is not None:
                        logging.info(f"ROE for {self.ticker}: {roe}")
                        return roe
            logging.warning(f"ROE not found for {self.ticker}")
            return None
        except Exception as e:
            logging.error(f"Error getting ROE for {self.ticker}: {e}")
            return None

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