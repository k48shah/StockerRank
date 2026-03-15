import argparse
import logging
from datetime import date, datetime

from .config import load_config
from .metrics import METRICS
from .providers.yahooquery_provider import YahooQueryProvider
from .stock_screener import StockScreener, get_stock_list_from_csv
from .backtest.runner import BacktestRunner


def main():
    parser = argparse.ArgumentParser(
        prog="stock-screener",
        description="Rank stocks by one or more financial metrics."
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML (default: config.yaml)")

    subparsers = parser.add_subparsers(dest="command")

    # SCREENER
    screen_parser = subparsers.add_parser("screen", help="Screen and rank stocks using live data.")
    screen_parser.add_argument("--watchlist", help="Path to watchlist CSV (overrides config)")
    screen_parser.add_argument(
        "--metrics", nargs="+", choices=list(METRICS.keys()), metavar="METRIC",
        help=f"Metrics to rank by. Choices: {', '.join(METRICS.keys())}"
    )
    screen_parser.add_argument("--output", help="Output JSON file (overrides config)")

    # BACKTEST
    backtest_parser = subparsers.add_parser("backtest", help="Backtest a strategy from a past date to today.")
    backtest_parser.add_argument("--date", required=True, help="Backtest start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--top-n", type=int, default=30, help="Number of top-ranked stocks to hold (default: 10)")
    backtest_parser.add_argument("--watchlist", help="Path to watchlist CSV (overrides config)")
    backtest_parser.add_argument(
        "--metrics", nargs="+", choices=list(METRICS.keys()), metavar="METRIC",
        help=f"Metrics to rank by. Choices: {', '.join(METRICS.keys())}"
    )
    backtest_parser.add_argument("--output", default="backtest_results.json", help="Output JSON file (default: backtest_results.json)")

    args = parser.parse_args()

    # Default to 'screen'
    if args.command is None:
        args.command = "screen"

    config = load_config(args.config)

    if args.command == "screen":
        _run_screen(args, config)
    elif args.command == "backtest":
        _run_backtest(args, config)


def _run_screen(args, config):
    prov_config = config["provider"]
    watchlist = getattr(args, "watchlist", None) or config["watchlist"]
    output_file = getattr(args, "output", None) or config["output_file"]

    stock_list = get_stock_list_from_csv(watchlist)
    if not stock_list:
        logging.error(f"No stocks loaded from {watchlist}. Exiting.")
        return

    filter_list = _resolve_metrics(args)
    if not filter_list:
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


def _run_backtest(args, config):

    try:
        backtest_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        logging.error(f"Invalid date format '{args.date}'. Use YYYY-MM-DD.")
        return

    if backtest_date >= date.today():
        logging.error("Backtest date must be in the past.")
        return

    watchlist = getattr(args, "watchlist", None) or config["watchlist"]
    stock_list = get_stock_list_from_csv(watchlist)
    if not stock_list:
        logging.error(f"No stocks loaded from {watchlist}. Exiting.")
        return

    filter_list = _resolve_metrics(args)
    if not filter_list:
        return

    prov_config = config["provider"]
    runner = BacktestRunner(
        stock_list=stock_list,
        filter_list=filter_list,
        backtest_date=backtest_date,
        top_n=args.top_n,
        batch_size=prov_config["batch_size"],
        max_retries=prov_config["max_retries"],
        sleep_min=prov_config["sleep_min"],
        sleep_max=prov_config["sleep_max"],
        backoff_min=prov_config["backoff_min"],
        backoff_max=prov_config["backoff_max"],
    )
    performance = runner.run()
    runner.export_to_json(performance, args.output)

    print(f"\nBacktest complete: {backtest_date} -> today")
    print(f"Portfolio ({len(performance.stocks)} stocks):")
    for s in performance.stocks:
        print(f"  #{s.rank} {s.ticker:8s}  {s.pct_return:+.2f}%")
    print(f"Avg return: {performance.avg_return:+.2f}%  |  Up: {performance.stocks_up}  Down: {performance.stocks_down}")
    print(f"Results saved to {args.output}")


def _resolve_metrics(args) -> list[str]:
    all_metrics = list(METRICS.keys())
    if getattr(args, "metrics", None):
        return args.metrics
    print(f"Available metrics: {', '.join(all_metrics)}")
    filter_input = input("Enter metrics to rank by (comma-separated): ")
    filter_list = [f.strip() for f in filter_input.split(',') if f.strip() in all_metrics]
    if not filter_list:
        logging.error("No valid metrics entered. Exiting.")
    return filter_list


if __name__ == "__main__":
    main()
