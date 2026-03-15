import logging
import json
from yahooquery import Ticker
from time import sleep
import random
from pprint import pformat
from stock import Stock

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        for i in range(0, len(self.stock_list), batch_size):
            batch = self.stock_list[i:i+batch_size]
            logging.info(f"Fetching batch {i//batch_size + 1}: {batch}")
            
            for attempt in range(max_retries):
                try:
                    ticker_batch = Ticker(batch)
                    
                    sleep_time = random.uniform(3, 7)
                    logging.info(f"Sleeping for {sleep_time:.2f} seconds to avoid rate limiting")
                    sleep(sleep_time)
                    try:
                        summary_detail = ticker_batch.summary_detail
                        if not isinstance(summary_detail, dict) or 'error' in str(summary_detail).lower():
                            logging.warning(f"Invalid summary_detail for batch {batch}")
                            summary_detail = {}
                    except Exception as e:
                        logging.warning(f"Failed to get summary_detail for batch {batch}: {e}")
                        summary_detail = {}
                    
                    sleep(random.uniform(2, 4))
                    
                    try:
                        financial_data = ticker_batch.financial_data
                        if not isinstance(financial_data, dict) or 'error' in str(financial_data).lower():
                            logging.warning(f"Invalid financial_data for batch {batch}")
                            financial_data = {}
                    except Exception as e:
                        logging.warning(f"Failed to get financial_data for batch {batch}: {e}")
                        financial_data = {}
                    
                    sleep(random.uniform(2, 4))
                    
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
                    break
                    
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1} failed for batch {batch}: {e}")
                    if attempt < max_retries - 1:
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
                [s for s in self.stocks if s.rate_data.get(filter_name) is not None],
                key=lambda stock: stock.rate_data[filter_name],
                reverse=True
            )
            logging.info(filter_name)
            for index, rank in enumerate(self.ranks[filter_name]):
                logging.info(f"{pformat(rank.ticker)} {index}")

    def calculate_cumulative_ranks(self):
        for stock in self.stocks:
            self.cum_rank[stock.ticker] = sum(
                self.ranks[filter_name].index(stock)
                for filter_name in self.filter_list
                if stock in self.ranks[filter_name]
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

    def get_failed_tickers(self) -> list[str]:
        """Returns list of tickers that failed to fetch data"""
        successful_tickers = set(self.batch_data.keys())
        failed_tickers = [ticker for ticker in self.stock_list if ticker not in successful_tickers]
        if failed_tickers:
            logging.warning(f"Tickers with no data: {failed_tickers}")
            print(f"\nFailed tickers ({len(failed_tickers)}): {', '.join(failed_tickers)}")
        return failed_tickers


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
    screener.get_failed_tickers()

if __name__ == "__main__":
    main()