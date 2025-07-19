import logging
import json
from yahooquery import Ticker
from time import sleep
import random
from pprint import pformat

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Stock:
    def __init__(self, ticker, data=None):
        self.ticker = ticker
        self.data = data  # Pre-fetched batch data
        self.rate_data = {
            "forwardPE": self.get_forward_pe(),
            "cps": self.get_cps(),
            "roc": self.get_roe()
        }
        logging.info(pformat(self.rate_data))

    def get_forward_pe(self) -> float:
        try:
            if self.data and 'summary_detail' in self.data:
                summary = self.data['summary_detail']
                if isinstance(summary, dict):
                    forward_pe_raw = summary.get('forwardPE')
                    print(forward_pe_raw)
                    if forward_pe_raw and forward_pe_raw > 0:
                        forward_pe = 1 / forward_pe_raw * 100
                        logging.info(f"Forward PE for {self.ticker}: {forward_pe}")
                        return forward_pe
            logging.error(f"Forward PE not found for {self.ticker}")
            return -100000000
        except Exception as e:
            logging.error(f"Error getting Forward PE for {self.ticker}: {e}")
            return -100000000

    def get_cps(self) -> float:
        try:
            if self.data and 'financial_data' in self.data:
                financial_data = self.data['financial_data']
                if isinstance(financial_data, dict):
                    cps = financial_data.get('totalCashPerShare')
                    if cps is not None:
                        logging.info(f"CPS for {self.ticker}: {cps}")
                        return cps
            logging.error(f"CPS not found for {self.ticker}")
            return -100000000
        except Exception as e:
            logging.error(f"Error getting CPS for {self.ticker}: {e}")
            return -100000000

    def get_roe(self) -> float:
        try:
            if self.data and 'financial_data' in self.data:
                financial_data = self.data['financial_data']
                if isinstance(financial_data, dict):
                    roe = financial_data.get('returnOnEquity')
                    if roe is not None:
                        logging.info(f"ROE for {self.ticker}: {roe}")
                        return roe
            logging.error(f"ROE not found for {self.ticker}")
            return -100000000
        except Exception as e:
            logging.error(f"Error getting ROE for {self.ticker}: {e}")
            return -100000000

    def get_one_year_ago_price(self) -> float:
        try:
            if self.data and 'history' in self.data:
                hist_data = self.data['history']
                if isinstance(hist_data, dict):
                    hist_df = hist_data
                    if not hist_df.empty:
                        one_year_ago_price = hist_df['close'].iloc[0]
                        logging.info(f"One year ago price for {self.ticker}: {one_year_ago_price}")
                        return one_year_ago_price
            logging.error(f"One year ago price not found for {self.ticker}")
            return -100000000
        except Exception as e:
            logging.error(f"Error getting one year ago price for {self.ticker}: {e}")
            return -100000000

    def get_current_price(self) -> float:
        try:
            if self.data and 'price' in self.data:
                price_data = self.data['price']
                if isinstance(price_data, dict):
                    current_price = price_data.get('regularMarketPrice')
                    if current_price is not None:
                        logging.info(f"Current price for {self.ticker}: {current_price}")
                        return current_price
            logging.error(f"Current price not found for {self.ticker}")
            return -100000000
        except Exception as e:
            logging.error(f"Error getting current price for {self.ticker}: {e}")
            return -100000000


class StockScreener:
    def __init__(self, stock_list: list[str], filter_list: list[str]) -> None:
        self.stock_list = stock_list
        self.filter_list = filter_list
        self.batch_data = {}
        self.stocks = []
        self.ranks = {
            filter_name: [] for filter_name in filter_list
        }
        self.cum_rank = {}

    def fetch_batch_data(self, batch_size=10, max_retries=3):
        """Fetch data in batches to reduce API calls"""
        for i in range(0, len(self.stock_list), batch_size):
            batch = self.stock_list[i:i+batch_size]
            logging.info(f"Fetching batch {i//batch_size + 1}: {batch}")
            
            for attempt in range(max_retries):
                try:
                    # Create ticker object for batch
                    ticker_batch = Ticker(batch)
                    
                    # Add random delay between 3-7 seconds
                    sleep_time = random.uniform(3, 7)
                    logging.info(f"Sleeping for {sleep_time:.2f} seconds to avoid rate limiting")
                    sleep(sleep_time)
                    
                    # Fetch different types of data
                    try:
                        summary_detail = ticker_batch.summary_detail
                        if not isinstance(summary_detail, dict) or 'error' in str(summary_detail).lower():
                            logging.warning(f"Invalid summary_detail for batch {batch}")
                            summary_detail = {}
                    except Exception as e:
                        logging.warning(f"Failed to get summary_detail for batch {batch}: {e}")
                        summary_detail = {}
                    
                    sleep(random.uniform(2, 4))  # Additional delay between different data types
                    
                    try:
                        financial_data = ticker_batch.financial_data
                        if not isinstance(financial_data, dict) or 'error' in str(financial_data).lower():
                            logging.warning(f"Invalid financial_data for batch {batch}")
                            financial_data = {}
                    except Exception as e:
                        logging.warning(f"Failed to get financial_data for batch {batch}: {e}")
                        financial_data = {}
                    
                    sleep(random.uniform(2, 4))  # Additional delay
                    
                    try:
                        price_data = ticker_batch.price
                        if not isinstance(price_data, dict) or 'error' in str(price_data).lower():
                            logging.warning(f"Invalid price_data for batch {batch}")
                            price_data = {}
                    except Exception as e:
                        logging.warning(f"Failed to get price_data for batch {batch}: {e}")
                        price_data = {}
                    for stock in batch:
                        try:
                            self.batch_data[stock] = {
                                'summary_detail': summary_detail.get(stock, {}),
                                'financial_data': financial_data.get(stock, {}),
                                'price': price_data.get(stock, {})
                            }
                        except Exception as e:
                            logging.warning(f"Skipping {stock} due to fetch error: {e}")
                    
                    logging.info(f"Successfully fetched data for batch {batch}")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1} failed for batch {batch}: {e}")
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        backoff_time = (2 ** attempt) * random.uniform(5, 10)
                        logging.info(f"Waiting {backoff_time:.2f} seconds before retry...")
                        sleep(backoff_time)
                    else:
                        logging.error(f"Max retries exceeded for batch {batch}")
        missing = [t for t in batch if t not in summary_detail or t not in financial_data or t not in price_data]
        if missing:
            logging.warning(f"Tickers missing data in batch: {missing}")

    def create_stocks(self):
        """Create Stock objects with pre-fetched batch data"""
        for ticker in self.stock_list:
            if ticker in self.batch_data:
                stock = Stock(ticker, self.batch_data[ticker])
                self.stocks.append(stock)
            else:
                logging.warning(f"No data found for {ticker}, skipping.")

    def calculate_ranks(self):
        for filter_name in self.filter_list:
            self.ranks[filter_name] = sorted(
                self.stocks,
                key=lambda stock: stock.rate_data.get(filter_name, float('inf')),
                reverse=True
            )
            logging.info(filter_name)
            for index, rank in enumerate(self.ranks[filter_name]):
                logging.info(f"{pformat(rank.ticker)} {index}")

    def calculate_cumulative_ranks(self):
        for stock in self.stocks:
            self.cum_rank[stock.ticker] = sum(
                self.ranks[filter_name].index(stock) for filter_name in self.filter_list
            )

    def sort_by_cumulative_rank(self):
        return sorted(
            self.cum_rank.items(),
            key=lambda item: item[1]
        )

    def export_cum_ranks_to_json(self, filename: str):
        sorted_stocks = self.sort_by_cumulative_rank()
        result = []

        for ticker, cum_rank in sorted_stocks:
            stock_data = {
                "ticker": ticker,
                "cumulative_rank": cum_rank,
                "rate_data": {},
                "individual_ranks": {}
            }

            # Find the matching Stock object
            stock_obj = next((s for s in self.stocks if s.ticker == ticker), None)
            if stock_obj:
                stock_data["rate_data"] = stock_obj.rate_data

                for filter_name in self.filter_list:
                    try:
                        rank_index = self.ranks[filter_name].index(stock_obj)
                        stock_data["individual_ranks"][filter_name] = rank_index
                    except ValueError:
                        stock_data["individual_ranks"][filter_name] = None

            result.append(stock_data)

        with open(filename, 'w') as file:
            json.dump(result, file, indent=4)

        logging.info(f"Ranked stock data exported to {filename}")

def get_stock_list_from_csv(filename: str) -> list[str]:
    try:
        with open(filename, 'r') as file:
            stock_list = [line.strip() for line in file if line.strip()]
        logging.info(f"Stock list loaded from {filename}")
        return stock_list
    except FileNotFoundError:   
        logging.error(f"File {filename} not found")
        return []

def main():
    stock_list = get_stock_list_from_csv("StockScreener.csv")

    all_metrics = ["forwardPE", "cps", "roc"]

    print("Available metrics: forwardPE, cps, roc")
    filter_input = input("Enter filters to rank by (comma-separated): ")
    filter_list = [f.strip() for f in filter_input.split(',') if f.strip() in all_metrics]

    if not filter_list:
        logging.error("No valid filters entered. Exiting.")
        return

    screener = StockScreener(stock_list, filter_list)

    screener.fetch_batch_data(batch_size=5)
    screener.create_stocks()
    screener.calculate_ranks()
    screener.calculate_cumulative_ranks()
    screener.sort_by_cumulative_rank()
    screener.export_cum_ranks_to_json("ranked_stocks.json")

if __name__ == "__main__":
    main()