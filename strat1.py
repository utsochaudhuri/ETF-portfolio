import pandas as pd
import yfinance as yf

tickers = [
    # Cyclical ETFs
    "IYW",  # iShares US Technology ETF
    "IYF",  # iShares US Financials ETF
    "IYJ",  # iShares US Industrials ETF
    "IYT",  # iShares US Transportation ETF
    # Defensive ETFs
    "IYH",  # iShares US Healthcare ETF
    "IHE",  # iShares US Pharmaceuticals ETF
    "IYK",  # iShares US Consumer Staples ETF
    "IDU"   # iShares US Utilities ETF
]

data = yf.download(
    tickers=tickers,
    start="2007-01-01",
    end="2025-06-01",
    group_by="ticker",
    auto_adjust=False,
)

def closest_date(date):
    target_date = pd.to_datetime(date)
    available_dates = data["IYF"].index
    closest_date = min(available_dates, key=lambda d: abs(d - target_date))
    return closest_date

df = pd.read_csv("FEDFUNDS.csv")
df["observation_date"] = pd.to_datetime(df["observation_date"])
df["observation_date"] = df["observation_date"].dt.strftime("%Y-%m-%d")

if df.iloc[1,1]>=df.iloc[0,1]:
    cond = "+"
else:
    cond = "-"

fed_cond = []
fed_cond.append(cond)
for i in range(1,220):
    if df.iloc[i+1,1] > df.iloc[i,1]:
        cond="+"
        fed_cond.append(cond)
    elif df.iloc[i+1,1] == df.iloc[i,1]:
        fed_cond.append(cond)
    else:
        cond="-"
        fed_cond.append(cond)

port_value = 100000
cond = None
for i in range(1,220):
    apt_date = closest_date(df.iloc[i,0])
    if cond == None:
        cond = fed_cond[0]
        if cond == "+":
            iyw_prev = data["IYW"].loc[apt_date, "Adj Close"]
            iyf_prev = data["IYF"].loc[apt_date, "Adj Close"]
            iyj_prev = data["IYJ"].loc[apt_date, "Adj Close"]
            iyt_prev = data["IYT"].loc[apt_date, "Adj Close"]
        else:
            iyh_prev = data["IYH"].loc[apt_date, "Adj Close"]
            ihe_prev = data["IHE"].loc[apt_date, "Adj Close"]
            iyk_prev = data["IYK"].loc[apt_date, "Adj Close"]
            idu_prev = data["IDU"].loc[apt_date, "Adj Close"]
    elif cond != fed_cond[i]:
        if cond == "+":
            iyw_now = data["IYW"].loc[apt_date, "Adj Close"]
            iyf_now = data["IYF"].loc[apt_date, "Adj Close"]
            iyj_now = data["IYJ"].loc[apt_date, "Adj Close"]
            iyt_now = data["IYT"].loc[apt_date, "Adj Close"]
            port_value = port_value/4*(iyw_now/iyw_prev+iyf_now/iyf_prev+iyj_now/iyj_prev+iyt_now/iyt_prev)
            iyh_prev = data["IYH"].loc[apt_date, "Adj Close"]
            ihe_prev = data["IHE"].loc[apt_date, "Adj Close"]
            iyk_prev = data["IYK"].loc[apt_date, "Adj Close"]
            idu_prev = data["IDU"].loc[apt_date, "Adj Close"]
            cond = "-"
        else:
            iyh_now = data["IYH"].loc[apt_date, "Adj Close"]
            ihe_now = data["IHE"].loc[apt_date, "Adj Close"]
            iyk_now = data["IYK"].loc[apt_date, "Adj Close"]
            idu_now = data["IDU"].loc[apt_date, "Adj Close"]
            port_value = port_value/4*(iyh_now/iyh_prev+ihe_now/ihe_prev+iyk_now/iyk_prev+idu_now/idu_prev)
            iyw_prev = data["IYW"].loc[apt_date, "Adj Close"]
            iyf_prev = data["IYF"].loc[apt_date, "Adj Close"]
            iyj_prev = data["IYJ"].loc[apt_date, "Adj Close"]
            iyt_prev = data["IYT"].loc[apt_date, "Adj Close"]
            cond = "+"
    if i == len(fed_cond)-1:
        if cond == "+":
            iyw_now = data["IYW"].loc[apt_date, "Adj Close"]
            iyf_now = data["IYF"].loc[apt_date, "Adj Close"]
            iyj_now = data["IYJ"].loc[apt_date, "Adj Close"]
            iyt_now = data["IYT"].loc[apt_date, "Adj Close"]
            port_value = port_value/4*(iyw_now/iyw_prev+iyf_now/iyf_prev+iyj_now/iyj_prev+iyt_now/iyt_prev)
        else:
            iyh_now = data["IYH"].loc[apt_date, "Adj Close"]
            ihe_now = data["IHE"].loc[apt_date, "Adj Close"]
            iyk_now = data["IYK"].loc[apt_date, "Adj Close"]
            idu_now = data["IDU"].loc[apt_date, "Adj Close"]
            port_value = port_value/4*(iyh_now/iyh_prev+ihe_now/ihe_prev+iyk_now/iyk_prev+idu_now/idu_prev)

print(port_value)