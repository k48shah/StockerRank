# Stock Screener & Ranking Tool

A Python-based stock screener and ranking tool inspired by Joel Greenblatt's "The Little Book That Still Beats the Market." Ranks stocks based on fundamental metrics and supports backtesting a strategy against historical data.

---

## Setup

**Install**

```
git clone https://github.com/k48shah/StockerRank.git
cd StockerRank
pip install -e .
```

**Configure**

Edit `config.yaml` to set your watchlist path, output file, and provider settings (batch size, retry limits, sleep intervals).

**Prepare your watchlist**

Add stock tickers (one per line) to a CSV file and point `config.yaml` at it.

---

## Usage

**Screen stocks using live data:**

```
stock-screener screen --metrics roe cps forwardPE
stock-screener screen --watchlist watchlists/my_list.csv --output results.json
```

**Backtest a strategy from a past date to today:**

```
stock-screener backtest --date 2024-01-01 --top-n 30 --metrics roe cps
```

If `--metrics` is omitted, the tool will prompt interactively.

---

## Available Metrics

| Key | Description |
|---|---|
| `forwardPE` | Forward P/E expressed as earnings yield (1/PE * 100) |
| `cps` | Cash per share |
| `roe` | Return on equity |

New metrics can be added by adding an entry to `stock_screener/metrics.py`.

---

## How It Works

1. Fetches financial data from Yahoo Finance via `yahooquery` in batches with retry and backoff logic.
2. For each stock, computes the selected metrics and ranks stocks per metric.
3. Assigns a cumulative rank (sum of individual metric ranks) and sorts by it.
4. Exports ranked results to JSON.

For backtesting, historical balance sheet and income statement data is used to derive metrics at the specified date. `forwardPE` is replaced with trailing PE (price / EPS) since forward estimates are not available historically.

---

## Roadmap

- Caching layer to avoid re-fetching data on repeat runs
- Async batch fetching for faster runs over large watchlists
- Two-pass pre-filtering to reduce API calls
- Additional data providers (Finnhub, Financial Modeling Prep)
- Neural network / statistical model to identify most impactful metrics

---

## Disclaimer

This tool is for educational and research purposes only. The developers are not responsible for any financial decisions, investments, or losses incurred as a result of using this software.

---

## Dependencies

- [yahooquery](https://yahooquery.dpguthrie.com/guide/ticker/intro/)
- [pyyaml](https://pyyaml.org/)
