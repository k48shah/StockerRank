import xlrd
import xlwt
from yahooquery import Ticker

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


def tickerInfo(stockList, finList):
    assetList = [[] for _ in finList]
    for stock in stockList:
        print(stock, stockList.index(stock))
        stockInfo = Ticker(stock)
        try:
            if(int(str(stockInfo.price).split('\'regularMarketTime\': \'')[1].split('-')[0]) >= 2020):
                #eps = float(latestEarnings)/float(sharePrice)
                finData = stockInfo.financial_data[stock]
                keyStats = stockInfo.key_stats[stock]
                for index, string in enumerate(finList):
                    infoBool = 0
                    if (string == "forwardEP" and ("forwardPE" in keyStats)):
                        assetList[index].append(1/keyStats["forwardPE"] * 100)
                        infoBool += 1
                    elif (string == "returnOnAssets" and ("returnOnAssets" in finData)):
                        assetList[index].append(finData["returnOnAssets"])
                        infoBool += 1
                    elif (string == "returnOnEquity" and ("returnOnEquity" in finData)):
                        assetList[index].append(finData["returnOnEquity"])
                        infoBool += 1
                    elif (string == "earningsYield" and ("enterpriseValue" in keyStats) and ("ebitda" in finData)):
                        assetList[index].append(keyStats["enterpriseValue"]/finData["ebitda"])
                        print(keyStats["enterpriseValue"]/finData["ebitda"])
                        infoBool += 1
                    elif (infoBool == 0):
                        assetList[index].append(-100000000)
            else:
                assetList[index].append(-100000000)
        except:
            print("No such stock")
            for index, string in enumerate(finList):
                assetList[index].append(-100000000)
    return assetList


def rankVal(rankList):
    ranks = [[] for _ in rankList]
    for index, val in enumerate(rankList):
        sortedList = sorted(val, reverse=True)
        print(val)
        for i, x in enumerate(val):
            ranks[index].append(sortedList.index(x))
    return ranks

def sumRanks(rankedList):
    sumList = list()
    for value in range(0, len(rankedList[0])):
        temp = 0
        for i in range(0, len(rankedList)):
            temp = temp + rankedList[i][value]
        sumList.append(temp)
    return sumList

def findBest(rankList, stockList):
    storeStock = stockList[rankList.index(min(rankList))]
    storeRank = min(rankList)
    rankList[rankList.index(min(rankList))] = 10000000
    return [storeStock, storeRank]

#TODO
def removeDepStocks():
    return


stockListing = getStocksFromCSV()
strList = ["earningsYield", "returnOnAssets"]
filterList = tickerInfo(stockListing, strList)
rankList = rankVal(filterList)

cumRanks = sumRanks(rankList)
print(cumRanks)
pickList = list()
for x in range(len(stockListing)):
    bestVal = findBest(cumRanks, stockListing)
    originalIndex = stockListing.index(bestVal[0])
    temp = list()
    temp.append(bestVal[0])
    temp.append(bestVal[1])
    for index, filter in enumerate(strList):
        temp.append(filterList[index][originalIndex])
        temp.append(rankList[index][originalIndex])
    pickList.append(temp)
    print(pickList[x])
sortedList = sorted(pickList, key=lambda x: x[1])
exportToCSV(sortedList, "stonks")
# Only do once to prevent extreme stock removals
# removeDepStocks(stockListing)
