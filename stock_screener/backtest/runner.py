import json
import logging
from datetime import date

from yahooquery import Ticker

from ..stock_screener import StockScreener
from .historical_provider import HistoricalProvider
from .performance import PortfolioPerformance, StockPerformance


class BacktestRunner:
    def __init__(
        self,
        stock_list: list[str],
        filter_list: list[str],
        backtest_date: date,
        top_n: int,
        batch_size: int = 10,
        max_retries: int = 3,
        sleep_min: float = 3,
        sleep_max: float = 7,
        backoff_min: float = 5,
        backoff_max: float = 10,
    ):
        self.stock_list = stock_list
        self.filter_list = filter_list
        self.backtest_date = backtest_date
        self.top_n = top_n
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.sleep_min = sleep_min
        self.sleep_max = sleep_max
        self.backoff_min = backoff_min
        self.backoff_max = backoff_max

    def run(self) -> PortfolioPerformance:
        provider = HistoricalProvider(
            self.backtest_date,
            batch_size=self.batch_size,
            max_retries=self.max_retries,
            sleep_min=self.sleep_min,
            sleep_max=self.sleep_max,
            backoff_min=self.backoff_min,
            backoff_max=self.backoff_max,
        )
        screener = StockScreener(self.stock_list, self.filter_list, provider)

        screener.fetch_batch_data()
        screener.create_stocks()
        screener.calculate_ranks()
        screener.calculate_cumulative_ranks()

        all_ranked = screener.sort_by_cumulative_rank()

        candidate_tickers = [ticker for ticker, _ in all_ranked[:self.top_n * 3]]
        current_prices = self._fetch_current_prices(candidate_tickers)

        portfolio = PortfolioPerformance(
            start_date=str(self.backtest_date),
            top_n=self.top_n,
            metrics_used=self.filter_list,
        )

        portfolio_rank = 1
        for ticker, _ in all_ranked:
            if portfolio_rank > self.top_n:
                break

            stock_obj = next((s for s in screener.stocks if s.ticker == ticker), None)
            if stock_obj is None:
                continue

            price_start = screener.batch_data.get(ticker, {}).get("price", {}).get("regularMarketPrice")
            price_now = current_prices.get(ticker)

            if price_start is None or price_now is None:
                logging.warning(f"Missing price data for {ticker}, skipping.")
                continue

            pct_return = (price_now - price_start) / price_start * 100

            individual_ranks = {
                f: screener.ranks[f].index(stock_obj)
                for f in self.filter_list
                if stock_obj in screener.ranks[f]
            }

            portfolio.stocks.append(StockPerformance(
                ticker=ticker,
                rank=portfolio_rank,
                metric_values=stock_obj.rate_data,
                individual_ranks=individual_ranks,
                price_at_start=price_start,
                price_now=price_now,
                pct_return=pct_return,
            ))
            portfolio_rank += 1

        if len(portfolio.stocks) < self.top_n:
            logging.warning(f"Only {len(portfolio.stocks)} of {self.top_n} requested stocks had valid price data.")

        return portfolio

    def _fetch_current_prices(self, tickers: list[str]) -> dict[str, float]:
        try:
            t = Ticker(tickers)
            price_data = t.price
            return {
                ticker: data.get("regularMarketPrice")
                for ticker, data in price_data.items()
                if isinstance(data, dict)
            }
        except Exception as e:
            logging.error(f"Failed to fetch current prices: {e}")
            return {}

    def export_to_json(self, performance: PortfolioPerformance, filename: str):
        with open(filename, "w") as f:
            json.dump(performance.to_dict(), f, indent=4)
        logging.info(f"Backtest results exported to {filename}")
