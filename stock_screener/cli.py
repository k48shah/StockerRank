import argparse
import logging

from .config import load_config
from .metrics import METRICS
from .providers.yahooquery_provider import YahooQueryProvider
from .stock_screener import StockScreener, get_stock_list_from_csv


def main():
    parser = argparse.ArgumentParser(
        prog="stock-screener",
        description="Rank stocks by one or more financial metrics."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config YAML file (default: config.yaml)"
    )
    parser.add_argument(
        "--watchlist",
        help="Path to watchlist CSV (overrides config)"
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=list(METRICS.keys()),
        metavar="METRIC",
        help=f"Metrics to rank by. Choices: {', '.join(METRICS.keys())}"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path (overrides config)"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    prov_config = config["provider"]

    watchlist = args.watchlist or config["watchlist"]
    output_file = args.output or config["output_file"]

    stock_list = get_stock_list_from_csv(watchlist)
    if not stock_list:
        logging.error(f"No stocks loaded from {watchlist}. Exiting.")
        return

    all_metrics = list(METRICS.keys())

    if args.metrics:
        filter_list = args.metrics
    else:
        print(f"Available metrics: {', '.join(all_metrics)}")
        filter_input = input("Enter metrics to rank by (comma-separated): ")
        filter_list = [f.strip() for f in filter_input.split(',') if f.strip() in all_metrics]

    if not filter_list:
        logging.error("No valid metrics entered. Exiting.")
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
    screener.export_cum_ranks_to_json(output_file)
    screener.get_failed_tickers()


if __name__ == "__main__":
    main()
