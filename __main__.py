import StockScreener as StockScreener


priority = [1, 1]
valueList = ["forwardPE", "returnOnAssets"]
StockScreener.main(stockList, valueList, priority)
# valueList = ["earningsYield", "returnOnAssets"]
# main(stockList, valueList, priority)
valueList = ["forwardPE", "CPS"]
main(stockList, valueList, priority)
valueList = ["forwardPE", "returnOnEquity"]
main(stockList, valueList, priority)

priority = [1, 1, 1]
valueList = ["earningsYield", "returnOnAssets", "CPS"]
main(stockList, valueList, priority)

priority = [1, 1]
valueList = ["pegRatio", "returnOnAssets"]
main(stockList, valueList, priority)
valueList = ["bookToPrice", "returnOnAssets"]
main(stockList, valueList, priority)