import xlrd
import xlwt
from yahooquery import Ticker
import os

def getStocksFromCSV():
    raw_ticker = xlrd.open_workbook("StockScreener.xlsx")
    sheet = raw_ticker.sheet_by_index(0)
    dataFrame = list()
    for x in range(sheet.nrows):
        dataFrame.append(sheet.cell_value(x, 0))
    return dataFrame

def exportToCSV(valueList, fileName):
    book = xlwt.Workbook()
    sheet = book.add_sheet("STONKS")
    for i, x in enumerate(valueList):
        for j, y in enumerate(x):
            sheet.write(i, j, x[j])
    book.save(fileName + ".xls")


def tickerEarningsYield(stockList):
    earningsYield = list()
    for stock in stockList:
        print(stock)
        stockInfo = Ticker(stock)
        try:
            if(int(str(stockInfo.price).split('\'regularMarketTime\': \'')[1].split('-')[0]) >= 2020):
                #latestEarnings = str(stockInfo.balance_sheet(frequency="q").get("RetainedEarnings")).split(" ")[-4].split("N")[0]
                #sharePrice = str(stockInfo.price).split('\'regularMarketPrice\': ')[1].split(',')[0]
                #eps = float(latestEarnings)/float(sharePrice)
                #NEW CALC: EBIT/(Enterprise Value)
                print(1/float(str(stockInfo.summary_detail).split('\'forwardPE\': ')[1].split(',')[0]) * 100)
                earningsYield.append(1/float(str(stockInfo.summary_detail).split('\'forwardPE\': ')[1].split(',')[0]) * 100)
        #     print(EarningsYield[index])
            else:
                earningsYield.append(-100000000)
        except:
            earningsYield.append(-100000000)
    return earningsYield

# def tickerComp(stockList):
#     returnOnAssets = list()
#     for stock in stockList:
#         print(stock)
#         stockInfo = Ticker(stock)
#         try:
#             returnOnAssets.append(float(str(stockInfo.financial_data).split('\'returnOnAssets\': ')[1].split(',')[0]))
#             print(float(str(stockInfo.financial_data).split('\'returnOnAssets\': ')[1].split(',')[0]))
#         except:
#             returnOnAssets.append(-100000)
#             print("stonk not real2: " + str(stock))
#     return returnOnAssets

def tickerComp(stockList, financialStr):
    ComparisonVal = list()
    for stock in stockList:
        print(stock)
        stockInfo = Ticker(stock)
        try:
            #NEW CALC: Add specific function to calculate ROC rather than ROA and ROE
            # NEW CALC: EBIT/(Net Working capital + Net Fixed Assets)
            if(int(str(stockInfo.price).split('\'regularMarketTime\': \'')[1].split('-')[0]) >= 2020):
                ComparisonVal.append(float(str(stockInfo.financial_data).split('\'' + financialStr + '\': ')[1].split(',')[0]))
                print(float(str(stockInfo.financial_data).split('\'' + financialStr + '\': ')[1].split(',')[0]))
            else:
                ComparisonVal.append(-10000000)
        except:
            ComparisonVal.append(-10000000)
    return ComparisonVal

# def tickerROE(stockList):
#     returnOnEquity = list()
#     for stock in stockList:
#         print(stock)
#         stockInfo = Ticker(stock)
#         try:
#             returnOnEquity.append(float(str(stockInfo.financial_data).split('\'returnOnEquity\': ')[1].split(',')[0]))
#             print(float(str(stockInfo.financial_data).split('\'returnOnEquity\': ')[1].split(',')[0]))
#         except:
#             returnOnEquity.append(-100000)
#             print("stonk not real2: " + str(stock))
#     return returnOnEquity

def rankVal(rankList):
    sortedList = sorted(rankList, reverse=True)
    ranks = list()
    for i, x in enumerate(rankList):
        ranks.append(sortedList.index(x))
    return ranks

def sumRanks(list1, list2):
    sumList = list()
    for i in range(len(list1)):
        sumList.append(list1[i] + list2[i])
    return sumList

def findBest(rankList, stockList):
    storeStock = stockList[rankList.index(min(rankList))]
    storeRank = min(rankList)
    #stockList.remove(stockList[rankList.index(min(rankList))])
    #rankList.remove(min(rankList))
    rankList[rankList.index(min(rankList))] = 10000000
    return [storeStock, storeRank]

#TODO
def removeDepStocks():
    return


stockListing = getStocksFromCSV()
constStockListing = stockListing
eYield = tickerEarningsYield(stockListing)
earningsRank = rankVal(eYield)

# roa = tickerROA(stockListing)
# roaRank = rankVal(roa)

# roe = tickerROE(stockListing)
# roeRank = rankVal(roe)

secondComp = tickerComp(stockListing, 'returnOnAssets')
secondRank = rankVal(secondComp)

cumRanks = sumRanks(earningsRank, secondRank)
print(cumRanks)
pickList = list()
for x in range(len(stockListing)):
    bestVal = findBest(cumRanks, stockListing)
    originalIndex = stockListing.index(bestVal[0])
    pickList.append([bestVal[0], bestVal[1], eYield[originalIndex], earningsRank[originalIndex], secondComp[originalIndex], secondRank[originalIndex]])
    print(pickList[x])
sortedList = sorted(pickList, key=lambda x: x[1])
exportToCSV(sortedList, "stonks")
# Only do once to prevent extreme stock removals
# removeDepStocks(stockListing)
