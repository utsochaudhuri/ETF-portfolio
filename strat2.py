from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

tickers_dict = {"IYW":0, # iShares US Technology ETF
           "IYF":0, # iShares US Financials ETF
           "IYJ":0, # iShares US Industrials ETF
           "IYH":0, # iShares US Healthcare ETF
           "IYK":0, # iShares US Consumer Staples ETF
           "IDU":0, # iShares US Utilities ETF
           "IYR":0, # iShares US Real Estate ETF
           "IYM":0, # iShares US Basic Materials ETF
           "IYC":0, # iShares US Consumer Discretionary ETF
           "IYE":0  # iShares US Energy ETF
           }

months = [datetime.strptime("2007-01-01", "%Y-%m-%d") + relativedelta(months=month) for month in range(211)]

df = pd.DataFrame(
    data=np.nan,  
    index=['k=1', 'k=3', 'k=6', 'k=12'],
    columns=['j=1', 'j=3', 'j=6', 'j=12']
)

tickers = list(tickers_dict.keys())
data = yf.download(
    tickers=tickers,
    start="2006-01-01",
    end="2025-07-01",
    group_by="ticker",
    auto_adjust=False
)

def closest_date(date):
    target_date = pd.to_datetime(date)
    available_dates = data["IYF"].index
    closest_date = min(available_dates, key=lambda d: abs(d - target_date))
    return closest_date

def perf_calc(ticker, apt_date, j):
    date_prev = None
    sum = 0
    for i in range(j,0,-1):
        if date_prev == None:
            date_prev = closest_date(apt_date - relativedelta(months=j))
            date_now = closest_date(date_prev + relativedelta(months=1))
            ticker_prev = data[ticker].loc[date_prev, "Adj Close"]
            ticker_now = data[ticker].loc[date_now, "Adj Close"]
            month_return = (ticker_now-ticker_prev)/ticker_prev
            sum+=month_return
        else:
            date_prev = date_now
            date_now = closest_date(date_prev + relativedelta(months=1))
            ticker_prev = data[ticker].loc[date_prev, "Adj Close"]
            ticker_now = data[ticker].loc[date_now, "Adj Close"]
            month_return = (ticker_now-ticker_prev)/ticker_prev
            sum+=month_return
    avg_month_perf = sum/j
    return avg_month_perf

for j in [1,3,6,12]:
    for k in [1,3,6,12]:
        port_value = 100000
        for apt_date in months[::k]:
            for ticker in tickers:
                tickers_dict[ticker] = perf_calc(ticker, apt_date, j)
            winners_port = sorted(tickers_dict, key=tickers_dict.get, reverse=True)[:3]
            perf_ratio_tot = 0
            for win_ticker in winners_port:
                date_prev = closest_date(apt_date)
                date_now = closest_date(apt_date + relativedelta(months=k))
                win_ticker_price_prev = data[win_ticker].loc[date_prev, "Adj Close"]
                win_ticker_price_now = data[win_ticker].loc[date_now, "Adj Close"]
                perf_ratio_tot+=win_ticker_price_now/win_ticker_price_prev
            port_value = port_value/3*(perf_ratio_tot)
        print(port_value)
        df.loc[f"k={k}",f"j={j}"] = port_value
         
print(df)