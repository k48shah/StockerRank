# Stock Screener & Ranking Tool

A Python-based stock screener and ranking tool inspired by Joel Greenblatt’s “The Little Book That Still Beats the Market.” Developed by a University of Waterloo graduate, this project applies a proven quantitative strategy to identify high-performing equities using fundamental metrics.

## Overview

This tool automates the process of sourcing and ranking stocks based on a proprietary implementation of the Magic Formula — a simple yet powerful value-investing strategy. With just a list of tickers, the screener fetches key financial metrics and ranks companies accordingly.


The algorithm has historically demonstrated significant outperformance:
📊 The top 30 ranked stocks achieved a greater return over the S&P 500 over a 3 year period.

Stock Portfolio
![Performance Stock Picker](https://imgur.com/a/nOovIhF)

S&P 500
![Performance S&P 500](https://imgur.com/a/0zzxv5H)

## How It Works

1. Import all necessary Python libraries. (Provided in `requirements.txt`)
2. Input your stock tickers into Column A of `StockScreeneer.csv`.
3. Run `StockScreener.py`, choose what you would like to filter by.
4. The program collects and analyzes data, then exports the results to `ranked_stocks.json`.
5. The best ranked stocks are listed from top to bottom

---

## Setup Instructions

1. **Clone the repository**  
   Open your terminal and run:
   ```
   git clone https://github.com/k48shah/StockerRank.git
   cd StockerRank
   ```

2. **Install required Python packages**  
   Run the following command to install dependencies:
   ```
   python3 -m pip install -r requirements.txt
   ```

3. **Prepare your stock list**  
   - Open `StockScreeneer.csv`.
   - Enter your desired stock tickers in Column A. (I have provided a set of large set of stocks)

4. **Run the screener**  
   Execute the main Python file:
   ```
   python StockScreener.py
   ```

5. **View results**  
   - Open `ranked_stocks.json` to see the ranked stocks.

---

## Features


- Pulls real-time financial data from Yahoo Finance via yahooquery
Ranks stocks based on Earnings Yield, Return on Capital (ROC), and Cash per share
Exports clean, sortable results to Excel and JSON
Easily customizable and extendable for different investment strategies

---

## Roadmap/To-Do

- [] Automate Yahoo Finance portfolio creation using Selenium (with cash allocation)

- [] Benchmark top 30 picks vs. S&P 500 over multiple time frames

- [] Integrate OpenCV for visual-based technical analysis

- [] Add asynchronous data fetching to improve performance

- [] Design an interactive GUI for non-technical users

- [] Append percent change data to output files

- [] Enable metric customization (e.g. market cap, sector filters)

- [] Add bottom-fishing logic for price floors

- [] Support multiple output formats (CSV, JSON, XLSX)

- [] (Optional) Automate S&P 500 performance comparisons

---

## Disclaimer

This tool is for educational and research purposes only.
The developers are not responsible for any financial decisions, investments, or losses incurred as a result of using this software.

---

## Dependencies

- [yahooquery](https://yahooquery.dpguthrie.com/guide/ticker/intro/)