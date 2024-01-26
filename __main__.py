import StockScreener as StockScreener
import Analyst as Analyst

CHOICES = ['screener', 'analyst', 'both']

def main():
    choice = ""
    while choice not in CHOICES:
        choice = input("run screener, analyst, or both? (lowercase): \n")

    if choice == "screener" or choice == "both":
        stockList = StockScreener.getStocksFromCSV()
        priority = [1, 1]

        valueList = ["forwardPE", "returnOnAssets"]
        StockScreener.screen(stockList, valueList, priority)
        priority = [1, 1]
        valueList = ["forwardPE", "CPS"]
        StockScreener.screen(stockList, valueList, priority)
        valueList = ["forwardPE", "returnOnEquity"]
        StockScreener.screen(stockList, valueList, priority)

        priority = [1, 1, 1]
        valueList = ["earningsYield", "returnOnAssets", "CPS"]
        StockScreener.screen(stockList, valueList, priority)

    if choice == "analyst" or choice == "both":
        Analyst.analyze()

if __name__== "__main__":
    main()
