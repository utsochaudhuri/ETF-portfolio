import pandas as pd
import time
import yfinance as yf
import statistics
import numpy as np
from fredapi import Fred
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy import stats

df = pd.read_csv("final_data - Copy.csv")
fred = Fred(api_key="df4e88e416cc272952e53b8c6f4b2055")

start_date = datetime.strptime("2025-03-01", "%Y-%m-%d")
end_date = start_date + relativedelta(months=3)
economic_met_start_date = start_date - relativedelta(months=3)


# Economic Metrics
gdp_series = fred.get_series("A191RL1Q225SBEA", 
                      observation_start=economic_met_start_date, 
                      observation_end=end_date)


inflation_series = fred.get_series("CPIAUCSL",
                            observation_start=economic_met_start_date, 
                            observation_end=end_date)


unemployment_series = fred.get_series("UNRATE", 
                               observation_start=economic_met_start_date, 
                               observation_end=end_date)


rates_series = fred.get_series("FEDFUNDS", 
                        observation_start=economic_met_start_date, 
                        observation_end=end_date)


yield_curve_series = fred.get_series("T10Y2Y", 
                              observation_start=economic_met_start_date, 
                              observation_end=end_date)


confidence_series = fred.get_series("UMCSENT", 
                             observation_start=economic_met_start_date, 
                             observation_end=end_date)


gdp_monthly = gdp_series.resample('M').last()
inflation_monthly = inflation_series.resample('M').last()
unemployment_monthly = unemployment_series.resample('M').last()
rates_monthly = rates_series.resample('M').last()
yield_curve_monthly = yield_curve_series.resample('M').last()
confidence_monthly = confidence_series.resample('M').last()

gdp_z = pd.Series(stats.zscore(gdp_monthly.dropna().values, nan_policy="omit"), 
                  index=gdp_monthly.dropna().index, name='gdp_z')
inflation_z = pd.Series(stats.zscore(inflation_monthly.dropna().values, nan_policy="omit"), 
                  index=inflation_monthly.dropna().index, name='inflation_z')
unemployment_z = pd.Series(stats.zscore(unemployment_monthly.dropna().values, nan_policy="omit"), 
                  index=unemployment_monthly.dropna().index, name='unemployment_z')
rates_z = pd.Series(stats.zscore(rates_monthly.dropna().values, nan_policy="omit"), 
                  index=rates_monthly.dropna().index, name='rates_z')
yield_curve_z = pd.Series(stats.zscore(yield_curve_monthly.dropna().values, nan_policy="omit"), 
                  index=yield_curve_monthly.dropna().index, name='yield_curve_z')
confidence_z = pd.Series(stats.zscore(confidence_monthly.dropna().values, nan_policy="omit"), 
                  index=confidence_monthly.dropna().index, name='confidence_z')

composite = pd.concat([gdp_z, inflation_z, unemployment_z, rates_z, yield_curve_z, confidence_z], axis=1)
# Forward-fill GDP data to fill the gaps
composite['gdp_z'] = composite['gdp_z'].fillna(method='ffill')
composite_score = composite.mean(axis=1, skipna=True)
print(composite_score)

# def sharpe_ratio(ticker,start_date,end_date):
#     # Risk Free Return Rate Calculation
#     data = yf.download("SGOV", start=start_date,end=end_date, auto_adjust=False)
#     risk_free_total_return = (data.iloc[-1,0]-data.iloc[0,0])/data.iloc[0,0]
#     risk_free_return_rate = ((1+risk_free_total_return)**(1/len(data)))-1

#     data = yf.download(ticker, start=start_date,end=end_date)

#     # ETF return Calculation
#     return_values = []
#     x = 0
#     while x < len(data)-1:
#         return_values.append((data["Close"].values[x+1][0]-data["Close"].values[x][0])/data["Close"].values[x][0])
#         x+=1
#     avg_daily_return = statistics.mean(return_values)
#     std_dev_daily_return = statistics.stdev(return_values)

#     sharpe_ratio = ((avg_daily_return - risk_free_return_rate)/std_dev_daily_return)


# start_date = "2024-01-01"
# end_date = "2025-04-01"
# non_available = []
# for ticker in df["ETF Ticker"]:
#     try:
#         sharpe_ratio(ticker, start_date, end_date)
#     except:
#         non_available.append(ticker)
# print(non_available)