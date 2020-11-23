A Stock screener/ranker that is developed by small group of Waterloo students by using the fundamental principles borrowed from "The Little Book that Still Beats the Market" by Joel Greenblatt

How it Works:
1. Import required python libraries
2. Add a list of stocks in Column A of StockScreeneer.xlsx
3. Run StockScreener.py
4. Once data is collected the data will be exported to a file called 'stonks.xls'
5. Sort data in column B by lowest to greatest to see the top pick (best ranked) stocks

The current 30 top pick stocks (as of 21/11/2020) have beaten the S&P500 by a margin of 4x in percent change for the past year.

The graph below represents the percent change in the top 30 stocks vs the bottom 30 stocks chosen by the program. It also uses the S&P500 as a control.
![alt text](https://imgur.com/QqMRw4X.png)


TO-DO LIST:
- Populate Yahoo finance portfolios using selenium and set # of cash
- Take top 30 stocks taken from algorithm, find their percentage gain averages over different time frames and compare to s&p 500 during same frames
- Introduce technical analysis by using OpenCL
- Asynchronous searching of stocks to reduce wait time for data
- Create GUI to choose action from the stock screener
- Append % changes to the end of stonks.xls
- Rename stonks.xls according to initial file given and date
- Comment code functions for readability
- make a main python file which everything is called from rather than a single file which houses all code
- Integrate a front end web server to display and work through the stock picks
- Auto-sort data before dumping into stonks.xls
- Add ability for user to choose their second comparison tool
- Remove stocks that do not have one or two of the required entries
- Recalculate Earnings Yield and ROC using EBIT
This is an educational project and none of the developers are responsible for any trades or decisions made from the tool