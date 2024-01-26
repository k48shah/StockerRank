import os
import json
import glob
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import re
import PyPDF2

def getStocks(sizePerJson=30):
    os.chdir("./")
    checkList = dict()
    for file in glob.glob("*.json"):
        with open("./" + file) as f:
            stocksInFile = json.load(f).keys()
        for count in range(0, sizePerJson - 1):
            try:
                key = list(stocksInFile)[count]
                checkList.setdefault(key, [])
                checkList[list(stocksInFile)[count]].append(file)
            except:
                print("less than " + str(sizePerJson) + " stocks selected")
    return checkList

def driverOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('–-disable-notifications')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("prefs", {\
        "profile.default_content_setting_values.notifications":2,
        "download.default_directory": "../docs/", #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        })
    return options


def automationBMO(stocks):
    bmoList = list()
    options = driverOptions()
    loginURL = 'https://www.secure.bmoinvestorline.com/ILClientWeb/login/DisplayLogin.jsp?refresh=true&lang=E'
    driver = webdriver.Chrome(chrome_options=options, executable_path='./driver/chromedriver')
    driver.get(loginURL)
    print("Currently unable to bypass dist bot protection, login will be manual")
    time.sleep(60)
    inputElem = driver.find_element_by_id("nav_quotes_link")
    inputElem.click()
    inputElem = driver.find_element_by_id("M3_1")
    inputElem.click()
    for stock in stocks:
        symbol = stock
        country = "US"
        if ".TO" in str(stock):
            symbol = str(stock).replace(".TO", "")
            country = "Canada"
        if "-" in stock:
            symbol = str(stock).replace("-", ".")
        inputElem = driver.find_element_by_id("quoteSymbol")
        inputElem.send_keys(stock)
        inputElem = Select(driver.find_element_by_id("quoteExchange"))
        inputElem.select_by_visible_text(country)
        driver.execute_script("submitForm('quote')")
        for elem in driver.find_elements_by_class_name("pdficon"):
            elem.click()
            driver.switch_to.window(driver.window_handles[1])
            pdfFileObj = open(driver.current_url, 'rb')
            print(driver.current_url)
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            print(pdfReader.getPage(0).extractText())
        while(1):
            pass
    # inputElem = driver.find_element_by_id("pwd")
    # inputElem.send_keys(passW)
    # inputElem = driver.find_element_by_id("sasi_btn")
    # inputElem.click()
    if driver.current_url() == loginURL:
        driver.quit()

def automationTipRanks(stocks):
    options = driverOptions()
    driver = webdriver.Chrome('./driver/chromedriver')
    tipList = list()
    for stock in stocks:
        try:
            if ".TO" in str(stock):
                rename = "tse:" + stock.replace(".TO", "")
                driver.get('https://www.tipranks.com/stocks/' + str(rename))
            else:
                driver.get('https://www.tipranks.com/stocks/' + str(stock))
            if "No recent analyst ratings found for" in driver.page_source or "Page Not Found" in driver.page_source:
                tipList.append([0, 0, 0])
            else:
                time.sleep(2)
                buys = driver.find_elements_by_class_name("mr2")[4].get_attribute("innerHTML")
                holds = driver.find_elements_by_class_name("mr2")[6].get_attribute("innerHTML")
                sells = driver.find_elements_by_class_name("mr2")[8].get_attribute("innerHTML")
                tipList.append([int(buys), int(holds), int(sells)])
        except:
            tipList.append([0, 0, 0])
    tipList = rankTipRanks(tipList)
    return tipList

def rankTipRanks(tiprankList):
    print(tiprankList)
    for stock in tiprankList:
        rank = stock[0] - stock[1] - 2*stock[2]
        stock.append(rank)
    print(tiprankList)
    return tiprankList

def automationMarketBeat(stocks):
    driver = webdriver.Chrome(chrome_options=driverOptions(), executable_path='./driver/chromedriver')
    mbList = list()
    for stock in stocks:
        stockOrigin = "NASDAQ"
        restock = stock
        if ".TO" in str(stock):
            stockOrigin = "TSE"
            restock = stock.replace(".TO", "")
        driver.get('https://www.marketbeat.com/stocks/' + stockOrigin + '/' + str(restock) + '/price-target/')
        time.sleep(1)
        if not driver.current_url == 'https://www.marketbeat.com/stocks/' + stockOrigin + '/' + str(stock) + '/price-target/':
            driver.get(str(driver.current_url) + '/price-target')
        try:
            driver.execute_script("closeIframeModal()")
        except:
            print("no IframeModal", stock)
        if "Stock Forecast, Price" in driver.page_source:
            mbList.append([0, 0, 0, 0])
        else:
            tagName = driver.find_elements_by_tag_name("td")[11].get_attribute("innerHTML")
            sell = str(tagName).split(" Sell Rating")[0]
            hold = str(tagName).split(" Sell Rating(s)<br>")[1].split(" Hold Rating")[0]
            buy = str(tagName).split(" Hold Rating(s)<br>")[1].split(" Buy Rating")[0]
            strongBuy = str(tagName).split(" Buy Rating(s)<br>")[1].split(" Strong Buy Rating")[0]
            mbList.append([int(sell), int(hold), int(buy), int(strongBuy)])
    mbList = rankMarketBeat(mbList)
    return mbList

def rankMarketBeat(mbrankList):
    for stock in mbrankList:
        rank = stock[3]*2 + stock[2] - stock[1] - stock[0]*2
        stock.append(rank)
    return mbrankList






def analyze():
    stockDict = getStocks(30)
    automationBMO(stockDict)
    # try:
    #     automationBMO(stockDict)
    # except:
    #     print("Log into BMO Investorline to access BMO results")
    # automationTipRanks(stockDict)
    # automationMarketBeat(stockDict)