from dataclasses import dataclass, field


@dataclass
class StockPerformance:
    ticker: str
    rank: int
    metric_values: dict
    individual_ranks: dict
    price_at_start: float
    price_now: float
    pct_return: float


@dataclass
class PortfolioPerformance:
    start_date: str
    top_n: int
    metrics_used: list[str]
    stocks: list[StockPerformance] = field(default_factory=list)

    @property
    def avg_return(self) -> float:
        if not self.stocks:
            return 0.0
        return sum(s.pct_return for s in self.stocks) / len(self.stocks)

    @property
    def stocks_up(self) -> int:
        return sum(1 for s in self.stocks if s.pct_return > 0)

    @property
    def stocks_down(self) -> int:
        return sum(1 for s in self.stocks if s.pct_return <= 0)

    def to_dict(self) -> dict:
        return {
            "start_date": self.start_date,
            "top_n": self.top_n,
            "metrics_used": self.metrics_used,
            "avg_return_pct": round(self.avg_return, 4),
            "stocks_up": self.stocks_up,
            "stocks_down": self.stocks_down,
            "stocks": [
                {
                    "ticker": s.ticker,
                    "rank": s.rank,
                    "metric_values": s.metric_values,
                    "individual_ranks": s.individual_ranks,
                    "price_at_start": s.price_at_start,
                    "price_now": s.price_now,
                    "pct_return": round(s.pct_return, 4),
                }
                for s in self.stocks
            ],
        }
