import xlrd
from yahooquery import Ticker
import json
import math

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
            "cumRank": x[1]
        }
        for j, y in enumerate(rankingMetrics):
            outputData[x[0]][y] = x[j*2 + 2]
            outputData[x[0]][y + 'Rank'] = x[j*2+3]
    with open(fileName + '.json', 'w') as outFile:
        json.dump(outputData, outFile, indent=4)

def tickerInfo(stockList, finList):
    assetList = [[] for _ in finList]
    for stock in stockList:
        print(stock, stockList.index(stock))
        stockInfo = Ticker(stock)
        # print(list(quartInfo.keys()))
        try:
            if(int(str(stockInfo.price).split('\'regularMarketTime\': \'')[1].split('-')[0]) >= 2020):
                #eps = float(latestEarnings)/float(sharePrice)
                finData = stockInfo.all_financial_data('q')
                keyStats = stockInfo.key_stats[stock]
                for index, string in enumerate(finList):
                    infoBool = 0
                    if (string == "returnOnAssets" and ("NetIncome" in finData) and ("TotalAssets" in finData)):
                        try:
                            assetList[index].append(finData.get("NetIncome")[-1] / finData.get("TotalAssets")[-1])
                        except:
                            assetList[index].append(-100000000)
                        infoBool += 1
                    elif (string == "returnOnEquity" and ("NetIncome" in finData) and ("StockholdersEquity" in finData)):
                        try:
                            assetList[index].append(finData.get("NetIncome")[-1] / finData.get("StockholdersEquity")[-1])
                        except:
                            assetList[index].append(-100000000)
                        infoBool += 1
                    elif (string == "returnOnCapital" and ("NetIncome" in finData) and ("StockholdersEquity" in finData) and ("CurrentLiabilities")):
                        try:
                            assetList[index].append(finData.get("NetIncome")[-1] / (finData.get("StockholdersEquity")[-1] + finData.get("CurrentLiabilities")[-1]))
                        except:
                            assetList[index].append(-100000000)
                        infoBool += 1
                    elif (string == "earningsYield" and ("EnterprisesValueEBITDARatio" in finData)):
                        try:
                            # assetList[index].append(float(finData["ebitda"]/keyStats["enterpriseValue"]))
                            assetList[index].append(1/finData.get("EnterprisesValueEBITDARatio")[-5])
                        except:
                            assetList[index].append(-100000000)
                        infoBool += 1
                    # elif (string == "earningsYield" and ("enterpriseToEbitda" in keyStats)):
                    #     try:
                    #         # assetList[index].append(float(finData["ebitda"]/keyStats["enterpriseValue"]))
                    #         assetList[index].append(int(keyStats["enterpriseToEbitda"]))
                    #     except:
                    #         assetList[index].append(-100000000)
                    #     infoBool += 1
                    elif (infoBool == 0):
                        assetList[index].append(-100000000)
                    if math.isnan(assetList[index][-1]):
                        print("here")
                        assetList[index][-1] = -100000000
                print(len(assetList[0]) - 1, len(assetList[1]) - 1)
            else:
                for index, string in enumerate(assetList):
                    string.append(-100000000)
        except:
            print("No such stock")
            for index, string in enumerate(assetList):
                string.append(-100000000)
            print(assetList)

    return assetList


def rankVal(rankList, mult):
    ranks = [[] for _ in rankList]
    for index, val in enumerate(rankList):
        sortedList = sorted(val, reverse=True)
        for i, x in enumerate(val):
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
    storeRank = min(rankList)
    rankList[rankList.index(min(rankList))] = 10000000
    return [storeStock, storeRank]

#TODO
def removeDepStocks():
    return

def fileNameChange(filter, priority):
    fileName = ""
    for i in range(len(filter)):
        filePriority = str(priority[i])
        if filePriority.find('.'):
            filePriority.replace('.', '_')
        fileName = fileName + filter[i] + filePriority + "rekt"
    return fileName

def screen(stockListing, strList, multiplier):
    if not (len(strList) == len(multiplier)):
        print("Check argument lengths!")
    else:
        for i, x in enumerate(multiplier):
            if x == 0:
                strList.pop(i)
                multiplier.pop(i)
        for i, x in enumerate(multiplier):
            if x == 0:
                strList.pop(i)
                multiplier.pop(i)
        filterList = tickerInfo(stockListing, strList)
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
            pickList.append(temp)
            print(pickList[x])
        sortedList = sorted(pickList, key=lambda x: x[1])
        fileString = fileNameChange(strList, multiplier)
        exportToJSON(sortedList, fileString, strList)


stockList = getStocksFromCSV()
# #Try to keep max priorities to 1, set all to 1 to have equal priorities!
# # 0 is lowest priority, 1 is highest priority (exceeding 1 is equivalent to reducing priority on the opposing filter
#
priority = [1, 1]
valueList = ["earningsYield", "returnOnAssets"]
screen(stockList, valueList, priority)
valueList = ["earningsYield", "returnOnEquity"]
screen(stockList, valueList, priority)
valueList = ["earningsYield", "returnOnCapital"]
screen(stockList, valueList, priority)
# # valueList = ["earningsYield", "returnOnAssets"]
# # main(stockList, valueList, priority)
# valueList = ["forwardPE", "CPS"]
# screen(stockList, valueList, priority)
# valueList = ["forwardPE", "returnOnEquity"]
# screen(stockList, valueList, priority)
#
# priority = [1, 1, 1]
# valueList = ["earningsYield", "returnOnAssets", "CPS"]
# main(stockList, valueList, priority)
#
# priority = [1, 1]
# valueList = ["pegRatio", "returnOnAssets"]
# main(stockList, valueList, priority)
# valueList = ["bookToPrice", "returnOnAssets"]
# main(stockList, valueList, priority)