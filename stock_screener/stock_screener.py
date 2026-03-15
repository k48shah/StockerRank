import logging
import json
from pprint import pformat

from .providers.base import DataProvider
from .providers.yahooquery_provider import YahooQueryProvider
from .stock import Stock
from .metrics import METRICS
from .config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class StockScreener:
    def __init__(self, stock_list: list[str], filter_list: list[str], provider: DataProvider) -> None:
        self.stock_list = stock_list
        self.filter_list = filter_list
        self.provider = provider
        self.batch_data = {}
        self.stocks = []
        self.ranks = {
            filter_name: [] for filter_name in filter_list
        }
        self.cum_rank = {}

    def fetch_batch_data(self):
        self.batch_data = self.provider.fetch(self.stock_list)

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
    config = load_config()
    prov_config = config["provider"]

    stock_list = get_stock_list_from_csv(config["watchlist"])

    all_metrics = list(METRICS.keys())

    print(f"Available metrics: {', '.join(all_metrics)}")
    filter_input = input("Enter filters to rank by (comma-separated): ")
    filter_list = [f.strip() for f in filter_input.split(',') if f.strip() in all_metrics]

    if not filter_list:
        logging.error("No valid filters entered. Exiting.")
        return

    provider = YahooQueryProvider(
        batch_size=prov_config["batch_size"],
        max_retries=prov_config["max_retries"],
        sleep_min=prov_config["sleep_min"],
        sleep_max=prov_config["sleep_max"],
        backoff_min=prov_config["backoff_min"],
        backoff_max=prov_config["backoff_max"],
    )
    screener = StockScreener(stock_list, filter_list, provider)

    screener.fetch_batch_data()
    screener.create_stocks()

    screener.calculate_ranks()
    screener.calculate_cumulative_ranks()
    screener.sort_by_cumulative_rank()
    screener.export_cum_ranks_to_json(config["output_file"])
    screener.get_failed_tickers()

if __name__ == "__main__":
    main()