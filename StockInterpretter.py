"""
THIS FILE IS USED TO DETERMINE THE GROWTH OF STOCKS THAT WERE HIGHLY RANKED DURING THEIR EARNINGS PERIOD
Currently this file is used to analyze stocks based on the priority system and which previous monthly stocks had the highest returns
"""

import xlrd
from yahooquery import Ticker
import json
import time

def getStocksFromCSV():
    raw_ticker = xlrd.open_workbook("StockScreener.xlsx")
    sheet = raw_ticker.sheet_by_index(0)
    dataFrame = list()
    for x in range(sheet.nrows):
        dataFrame.append(sheet.cell_value(x, 0))
    return dataFrame

def exportToJSON(valueList, fileName, rankingMetrics):
    outputData = {}
    for i, x in enumerate(valueList):
        outputData[x[0]] = {
            "Cumulative Rank": x[1],
            "Percent Gain Since Earnings": x[-1]
        }
        for j, y in enumerate(rankingMetrics):
            outputData[x[0]][y] = x[j*2 + 2]
            outputData[x[0]][y + ' Rank'] = x[j*2+3]
    with open(fileName + '.json', 'w') as outFile:
        json.dump(outputData, outFile, indent=4)


def tickerInfo(stockList, finList):
    assetList = [[] for _ in finList]
    percentGain = list()
    for stock in stockList:
        print(stock, stockList.index(stock))
        stockInfo = Ticker(stock)
        try:
            time.sleep(1)
            if(int(str(stockInfo.price).split('\'regularMarketTime\': \'')[1].split('-')[0]) >= 2020):
                #eps = float(latestEarnings)/float(sharePrice)
                finData = stockInfo.all_financial_data('q')
                for index, string in enumerate(finList):
                    infoBool = 0
                    if (string == "forwardPE" and ("ForwardPeRatio" in finData)):
                        assetList[index].append(1/finData.get("ForwardPeRatio")[-1] * 100)
                        infoBool += 1
                    elif (string == "returnOnAssets" and ("NetIncome" in finData) and ("TotalAssets" in finData)):
                        assetList[index].append(finData.get("NetIncome")[-1]/finData.get("TotalAssets")[-1])
                        infoBool += 1
                    elif (string == "returnOnEquity" and ("NetIncome" in finData) and ("StockholdersEquity" in finData)):
                        assetList[index].append(finData.get("NetIncome")[-1]/finData.get("StockholdersEquity")[-1])
                        infoBool += 1
                    elif (string == "earningsYield" and ("EnterprisesValueEBITDARatio" in finData)):
                        assetList[index].append(1/finData.get("EnterprisesValueEBITDARatio"))
                        infoBool += 1
                    elif (string == "prevEarningsYield" and ("PeRatio" in finData)):
                        try:
                            assetList[index].append(1/finData.get("PeRatio")[-1] * 100)
                        except:
                            print("Appending -10000000")
                            assetList[index].append(-100000000)
                        infoBool += 1
                    #TODO Find historical values for company for data interpretation
                    # elif (string == "CPS" and ("totalCashPerShare" in finData)):
                    #     assetList[index].append(finData["totalCashPerShare"])
                    # elif (string == "bookToPrice" and ("priceToBook" in keyStats)):
                    #     assetList[index].append(1/keyStats["priceToBook"])
                    # elif (string == "pegRatio" and ("pegRatio" in keyStats)):
                    #     assetList[index].append(1/keyStats["pegRatio"])
                    elif (infoBool == 0):
                        print("Appending -10000000")
                        assetList[index].append(-100000000)
                try:
                    priceIndex = stockInfo.history(start=str(finData.get("asOfDate")[-1]).split(" ")[0])
                    percentGain.append((priceIndex.get("close")[-1] - priceIndex.get("close")[0]) / priceIndex.get("close")[0] * 100)
                except:
                    percentGain.append(-100000000)
                    print("Stock does not have historical data")
                    print(stockInfo.history(start=str(finData.get("asOfDate")[-1]).split(" ")[0]))
                    print(stockInfo.history(period='1y'))
            else:
                print("Appending -10000000")
                for index, string in enumerate(assetList):
                    string.append(-100000000)
                percentGain.append(-100000000)
        except:
            print("No such stock")
            for index, string in enumerate(assetList):
                string.append(-100000000)
            percentGain.append(-100000000)
    return assetList, percentGain


def rankVal(rankList, mult):
    ranks = [[] for _ in rankList]
    for index, val in enumerate(rankList):
        sortedList = sorted(val, reverse=True)
        print(val)
        for i, x in enumerate(val):
            if x == -100000000 or str(x) == "Nan" or str(x) == "nan":
                ranks[index].append(len(val))
            else:
                ranks[index].append(int(sortedList.index(x)/mult[index]))
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
    print(stockList[rankList.index(min(rankList))], rankList.index(min(rankList)), len(stockList))
    storeRank = min(rankList)
    rankList[rankList.index(min(rankList))] = 10000000
    return [storeStock, storeRank]

#TODO
def removeDepStocks():
    return

def fileNameChange(filter, priority):
    fileName = ""
    for i in range(len(filter)):
        filePriority = str(priority[i]).replace('.', '_')
        fileName = fileName + filter[i] + filePriority
        print(fileName, filePriority)
    return fileName

def main(stockListing, strList, multiplier):
    if not (len(strList) == len(multiplier)):
        print("Check argument lengths!")
    else:
        for i, x in enumerate(multiplier):
            if x == 0:
                strList.pop(i)
                multiplier.pop(i)
        filterList, gainList = tickerInfo(stockListing, strList)
        rankList = rankVal(filterList, multiplier)

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
            temp.append(gainList[originalIndex])
            pickList.append(temp)
            print(pickList[x])
        sortedList = sorted(pickList, key=lambda x: x[1])
        fileString = fileNameChange(strList, multiplier)
        exportToJSON(sortedList, fileString, strList)


#Try to keep max priorities to 1, set all to 1 to have equal priorities!
# 0 is lowest priority, 1 is highest priority (exceeding 1 is equivalent to reducing priority on the opposing filter
priority = [1, 0]
stockList = getStocksFromCSV()
valueList = ["prevEarningsYield", "returnOnAssets"]
main(stockList, valueList, priority)
