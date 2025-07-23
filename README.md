# ETF-portfolio
To understand active vs passive portfolio strategies I built 6 differnt ETF sector rotation portfolio (active) strategies to test returns against the benchmark (S&P500 --> buy & hold) for the US market over the course of different time periods. My strategies included:

## Strategy 1 (FED Interest rates)
Depending on whether the FED's interest rates increased or decreased I cycled my portfolio into either cyclical or defensive ETFs

## Strategy 2 (Lookback and investment periods)
For the chosen 10 ETFs I looked back at its performance (J months) and then invested in top 3 performing ETFs for investment period of k months. Adopting different values of j and k to be 1, 3, 6, 12 to obtain 16 different investment styles.

## Strategy 3 (Fama French 3 factor model "long only")
To get better alpha estimates over CAPM I used the 3-factor Fama French model to estimate the alpha for each ETF using a rolling linear regression on the following formuala:

$$
Pi - R_f = \alpha + \beta_1 (R_m - R_f) + \beta_2 SMB + \beta_3 HML + \epsilon
$$

Rf: Risk Free Rate (Estimated through 4-week TY Bill)
Pi-Rf: Portfolio Performance (ETF returns - Risk Free Rate)
Rm: Market Returns (Estimated market returns through returns of S&P500)
Rm-Rf: Market Premium (Market returns estimtated through S&P500 returns - Risk Free Rate)
SMB: Small Minus Big (Reutrn of small cap stocks estimated through IWM ETF - Return of big cap stocks estimated through SPY ETF)
HML: High Minus Low (Return of high book-to-market ration "value stocks" estimated through IVE ETF - Return of low book-to-market ration "growth stocks" estimated through IWM ETF)

## Strategy 4 (Fama French 3 factor model "long and short")
Same strategy as strategy 3 but for I also shorted ETFs with negative alpha

## Strategy 5 (Fama French 5 factor model "long only")
To get even better alpha estimates I used the Fama French 5 factor model which introduces to two more explanatory variables to reduce alpha estimate error using the same method as strategy 3. The model's formula is:

$$
Pi - R_f = \alpha + \beta_1 (R_m - R_f) + \beta_2 SMB + \beta_3 HML + \beta_4 RMW+ \beta_5 CMA+\epsilon
$$

RMW: Robust Minus Weak (Returns of high profit stocks - Returns of low profit stocks)
CMA: Conversative Minus Aggressive (Returns of firms investing conservatively - Returns of investing aggressively)

Since ETF substitutes were unavailable for RMW and CMA, I used the listed stocks from the "archive" file to construct a custom universe. After filtering for data availability, I calculated Return on Equity and Asset Growth to proxy for profitability and investment aggressiveness. I then used the top and bottom 30% of each metric to compute average returns and derive RMW and CMA as the respective differences.

Also to obtain necessary data I have used the refinitiv api (blocked access) ran through the symbols_list file, however the file has also been downloaded in the roe_asset_data.csv

## Strategy 6 (Fama French 5 factor model "long and short")
Same strategy as strategy 5 but for I also shorted ETFs with negative alpha

## Miscellaneous 
To run the strategy and tester files you will need the following libraries:
1. pandas
2. yfinance
3. numpy
4. datetime
5. relativedelta
6. fredapi
7. scikit-learn
8. matplotlib
