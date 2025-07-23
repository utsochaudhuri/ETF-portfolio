from fredapi import Fred
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

start_date = datetime.strptime("2002-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2025-07-01", "%Y-%m-%d")
end_date_tt = start_date + relativedelta(months=3)

fred = Fred(api_key="df4e88e416cc272952e53b8c6f4b2055")
FRED_api_key = "b689f2184e49964c003ed40eb2809cf3"
risk_free_rate_series = fred.get_series("DTB4WK", 
                        observation_start=start_date, 
                        observation_end=end_date)
risk_free_rate_series = risk_free_rate_series.dropna()

tickers = [
    "^GSPC", # S&P 500
    "IWM",   # iShares Russell 2000 ETF (Small-Cap)
    "SPY",   # SPDR S&P 500 ETF Trust (Large-Cap)
    "IVE",   # iShares S&P 500 Value ETF
    "IVW"   # iShares S&P 500 Growth ETF
]

ETF_dict = {"IYW":0, # iShares US Technology ETF
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

ETF_tickers = list(ETF_dict.keys())
tickers = ETF_tickers + tickers

data = yf.download(
    tickers=tickers,
    start=start_date,
    end=end_date,
    group_by="ticker",
    auto_adjust=False,
)

reg_data = {
    "x1=Rm-Rf": [None]*36,
    "x2=SMB": [None]*36,
    "x3=HML": [None]*36,
    "IYW: y=Ri-Rf": [None]*36,
    "IYF: y=Ri-Rf": [None]*36,
    "IYJ: y=Ri-Rf": [None]*36,
    "IYH: y=Ri-Rf": [None]*36,
    "IYK: y=Ri-Rf": [None]*36,
    "IDU: y=Ri-Rf": [None]*36,
    "IYR: y=Ri-Rf": [None]*36,
    "IYM: y=Ri-Rf": [None]*36,
    "IYC: y=Ri-Rf": [None]*36,
    "IYE: y=Ri-Rf": [None]*36,
}
reg_data = pd.DataFrame(reg_data)

def closest_date(date):
    target_date = pd.to_datetime(date)
    available_dates = data["IWM"].index
    closest_date = min(available_dates, key=lambda d: abs(d - target_date))
    return closest_date

def rf_closest_date(date):
    target_date = pd.to_datetime(date)
    available_dates = risk_free_rate_series.index
    closest_date = min(available_dates, key=lambda d: abs(d - target_date))
    return closest_date

def market_prem_calc(count, start_date):
    start_month = start_date+relativedelta(months=count)
    end_month = start_date+relativedelta(months=count+1)
    risk_free_rate = risk_free_rate_series[rf_closest_date(start_month)]
    SnP_start_price = data["^GSPC"].loc[closest_date(start_month), "Adj Close"]
    SnP_end_price = data["^GSPC"].loc[closest_date(end_month), "Adj Close"]
    SnP_month_return = (SnP_end_price-SnP_start_price)/SnP_start_price*100
    market_prem = SnP_month_return - risk_free_rate
    return market_prem

def SMB_calc(count, start_date):
    start_month = start_date+relativedelta(months=count)
    end_month = start_date+relativedelta(months=count+1)
    IWM_start_price = data["IWM"].loc[closest_date(start_month), "Adj Close"]
    IWM_end_price = data["IWM"].loc[closest_date(end_month), "Adj Close"]
    IWM_month_return = (IWM_end_price-IWM_start_price)/IWM_start_price*100
    SPY_start_price = data["SPY"].loc[closest_date(start_month), "Adj Close"]
    SPY_end_price = data["SPY"].loc[closest_date(end_month), "Adj Close"]
    SPY_month_return = (SPY_end_price-SPY_start_price)/SPY_end_price*100
    SMB = IWM_month_return - SPY_month_return
    return SMB

def HML_calc(count, start_date):
    start_month = start_date+relativedelta(months=count)
    end_month = start_date+relativedelta(months=count+1)
    IVE_start_price = data["IVE"].loc[closest_date(start_month), "Adj Close"]
    IVE_end_price = data["IVE"].loc[closest_date(end_month), "Adj Close"]
    IVE_month_return = (IVE_end_price-IVE_start_price)/IVE_start_price*100
    IVW_start_price = data["IVW"].loc[closest_date(start_month), "Adj Close"]
    IVW_end_price = data["IVW"].loc[closest_date(end_month), "Adj Close"]
    IVW_month_return = (IVW_end_price-IVW_start_price)/IVW_end_price*100
    HML = IVE_month_return - IVW_month_return
    return HML

def ETF_return(count, start_date, ticker):
    start_month = start_date+relativedelta(months=count)
    end_month = start_date+relativedelta(months=count+1)
    ticker_start_price = data[ticker].loc[closest_date(start_month), "Adj Close"]
    ticker_end_price = data[ticker].loc[closest_date(end_month), "Adj Close"]
    ticker_month_return = (ticker_end_price-ticker_start_price)/ticker_start_price*100
    return ticker_month_return

def port_invest(count, start_date, alpha_pos, alpha_neg, port_value):
    investment_count = count - 36
    start_month = start_date + relativedelta(months=36) + relativedelta(months=investment_count)
    end_month = start_date + relativedelta(months=36) + relativedelta(months=investment_count + 1)
    ETF_ratios = []
    for ticker in alpha_pos:
        ticker_start_price = data[ticker].loc[closest_date(start_month), "Adj Close"]
        ticker_end_price = data[ticker].loc[closest_date(end_month), "Adj Close"]
        ETF_ratios.append(ticker_end_price/ticker_start_price)
    if len(alpha_neg)>0:
        for ticker in alpha_neg:
            ticker_start_price = data[ticker].loc[closest_date(start_month), "Adj Close"]
            ticker_end_price = data[ticker].loc[closest_date(end_month), "Adj Close"]
            # Alternative ratio as short rewards ETF loss - monthly borrowing fees
            ETF_ratios.append((ticker_start_price/ticker_end_price)-(0.01/12))
    port_value = port_value/(len(alpha_pos)+len(alpha_neg))*(sum(ETF_ratios))
    return port_value

port_value = 100000
SP_value = 100000
port_values_ot = []
SP_value_ot = []
for i in range(246):
    if i<36:
        reg_data.loc[i, "x1=Rm-Rf"] = market_prem_calc(i, start_date)
        reg_data.loc[i, "x2=SMB"] = SMB_calc(i, start_date)
        reg_data.loc[i, "x3=HML"] = HML_calc(i, start_date)
        for ticker in ETF_tickers:
            reg_data.loc[i, f"{ticker}: y=Ri-Rf"] = ETF_return(i, start_date, ticker)
    # Last row accounting
    elif i == 245:
        # Regressing data and calculating alpha
        for ticker in ETF_tickers:
            X = reg_data[["x1=Rm-Rf", "x2=SMB", "x3=HML"]]
            y = reg_data[f"{ticker}: y=Ri-Rf"]
            model = LinearRegression().fit(X, y)
            ETF_dict[ticker] = model.intercept_

        # Investing portfolio
        positive_alpha_ETFs = [k for k, v in ETF_dict.items() if v > 0]
        negative_alpha_ETFs = [k for k, v in ETF_dict.items() if v < 0]
        port_value = port_invest(i, start_date, [], negative_alpha_ETFs, port_value)
        port_values_ot.append(port_value)
        SP_value = port_invest(i, start_date, ["^GSPC"], [], SP_value)
        SP_value_ot.append(SP_value)
    else:
        # Regressing data and calculating alpha
        for ticker in ETF_tickers:
            X = reg_data[["x1=Rm-Rf", "x2=SMB", "x3=HML"]]
            y = reg_data[f"{ticker}: y=Ri-Rf"]
            model = LinearRegression().fit(X, y)
            ETF_dict[ticker] = model.intercept_

        # Investing portfolio
        positive_alpha_ETFs = [k for k, v in ETF_dict.items() if v > 0]
        negative_alpha_ETFs = [k for k, v in ETF_dict.items() if v < 0]
        port_value = port_invest(i, start_date, positive_alpha_ETFs, negative_alpha_ETFs, port_value)
        port_values_ot.append(port_value)
        SP_value = port_invest(i, start_date, ["^GSPC"], [], SP_value)
        SP_value_ot.append(SP_value)

        # Row change for rolling linear regression
        reg_data = reg_data.iloc[1:].reset_index(drop=True)
        new_row = {}
        new_row["x1=Rm-Rf"] = market_prem_calc(i, start_date)
        new_row["x2=SMB"] = SMB_calc(i, start_date)
        new_row["x3=HML"] = HML_calc(i, start_date)
        for ticker in ETF_tickers:
            new_row[f"{ticker}: y=Ri-Rf"] = ETF_return(i, start_date, ticker)
        reg_data.loc[len(reg_data)] = new_row

port_values_ot = port_values_ot[:-1]

# Create time indices for both arrays
# Since they have different lengths, we'll use the minimum length for comparison
min_length = min(len(SP_value_ot), len(port_values_ot))

# Create time axis - you can adjust this based on your actual time period
# Here I'm using sequential time points (could be days, weeks, months, etc.)
time_points = list(range(min_length))

# For demonstration, let's create actual dates
start_date = datetime(2002, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(min_length)]

# Create the plot
plt.figure(figsize=(14, 8))

# Plot both lines (using only the overlapping length)
plt.plot(dates, SP_value_ot[:min_length], label='S&P500', linewidth=2, marker='o', markersize=3, alpha=0.8)
plt.plot(dates, port_values_ot[:min_length], label='Portfolio', linewidth=2, marker='s', markersize=3, alpha=0.8)

# Customize the plot
plt.title('Active vs Passive investing', fontsize=16, fontweight='bold')
plt.xlabel('Time', fontsize=12)
plt.ylabel('Value', fontsize=12)

# Format the x-axis to show dates nicely
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(15))  # Limit number of x-axis labels

# Add grid for better readability
plt.grid(True, alpha=0.3)

# Add legend
plt.legend(loc='upper left', fontsize=12)

# Format y-axis to show values in thousands
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Add some statistics
print(f"\nDataset 1 - Min: {min(SP_value_ot):,.0f}, Max: {max(SP_value_ot):,.0f}")
print(f"Dataset 2 - Min: {min(port_values_ot):,.0f}, Max: {max(port_values_ot):,.0f}")

# Display the plot
plt.show()