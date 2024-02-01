import pandas as pd
import numpy as np

import statsmodels.api as sm 
from statsmodels.tsa.stattools import coint
# 24 (how many times it's crossing the 0), 21 (moving average pram)
from constants import MAX_HALF_LIFE, WINDOW 

# https://www.pythonforfinance.net/2016/05/09/python-backtesting-mean-reversion-part-2/ /!\ ANNEX BELOW

# Calculate Half Life

def calculate_half_life(spread):
  df_spread = pd.DataFrame(spread, columns=["spread"])
  spread_lag = df_spread.spread.shift(1)
  spread_lag.iloc[0] = spread_lag.iloc[1]
  spread_ret = df_spread.spread - spread_lag
  spread_ret.iloc[0] = spread_ret.iloc[1]
  spread_lag2 = sm.add_constant(spread_lag)
  model = sm.OLS(spread_ret, spread_lag2)
  res = model.fit()
  halflife = round(-np.log(2) / res.params.iloc[1], 0)
  return halflife

# Calculate the ZScore
def calculate_zscore(spread):
  spread_series = pd.Series(spread)
  mean = spread_series.rolling(center=False, window=WINDOW).mean()
  std = spread_series.rolling(center=False, window=WINDOW).std()
  x = spread_series.rolling(center=False, window=1).mean()
  zscore = (x - mean) / std
  return zscore


# Calculate Cointegration
def calculate_cointegration(series_1, series_2):
  series_1 = np.array(series_1).astype(np.float64)
  series_2 = np.array(series_2).astype(np.float64)
  coint_flag = 0
  coint_res = coint(series_1, series_2)
  coint_t = coint_res[0]
  p_value = coint_res[1]
  critical_value = coint_res[2][1]
  model = sm.OLS(series_1, series_2).fit()
  hedge_ratio = model.params[0]
  spread = series_1 - (hedge_ratio * series_2)
  half_life = calculate_half_life(spread)
  t_check = coint_t < critical_value
  coint_flag = 1 if p_value < 0.05 and t_check else 0
  return coint_flag, hedge_ratio, half_life

# Store Cointegration Results
def store_cointegration_results(df_market_prices):

  # Initialize
  markets = df_market_prices.columns.to_list()
  criteria_met_pairs = []

  # Find cointegrated pairs
  # Start with our base pair
  for index, base_market in enumerate(markets[:-1]):
    series_1 = df_market_prices[base_market].values.astype(float).tolist()

    # Get Quote Pair
    for quote_market in markets[index +1:]:
      series_2 = df_market_prices[quote_market].values.astype(float).tolist()

      # Check cointegration
      coint_flag, hedge_ratio, half_life = calculate_cointegration(series_1, series_2)

      # Log pair
      if coint_flag == 1 and half_life <= MAX_HALF_LIFE and half_life > 0:
        criteria_met_pairs.append({
          "base_market": base_market,
          "quote_market": quote_market,
          "hedge_ratio": hedge_ratio,
          "half_life": half_life,
        })
        # print(
        #   "base_market", base_market,
        #   "quote_market", quote_market,
        #   "hedge_ratio", hedge_ratio,
        #   "half_life", half_life
        # )
        
  # Create and save DataFrame
  df_criteria_met = pd.DataFrame(criteria_met_pairs)
  df_criteria_met.to_csv("cointegrated_pairs.csv")
  del df_criteria_met

  # Return result
  return "saved"

"""
*************** ANNEX ******************
* Mean reversion strategy: A mean reversion strategy is based on the idea that 
the prices of two correlated assets will tend to revert to their historical or equilibrium relationship over time, 
and that deviations from this relationship can be exploited for profit :
* Cointegration: Cointegration is a statistical property that measures if two or more time series move together in the long run, 
even if they are not correlated in the short run. Cointegration can be tested using the Augmented Dickey Fuller test, 
which checks if the spread between the two series is stationary or mean reverting. 
A low p-value and a negative test statistic indicate cointegration.
* Half-life: Half-life is a measure of how long it takes for the spread between two cointegrated series to revert to its mean. 
It can be estimated by running a linear regression between the spread and its lagged version, 
and then using the coefficient to calculate the half-life using the Ornstein-Uhlenbeck process23. 
A shorter half-life means faster mean reversion and more trading opportunities.
* Z-score: Z-score is a normalized value that indicates how many standard deviations the spread is away from its mean4. 
It can be used to generate trading signals based on predefined thresholds. 
For example, a high positive Z-score means the spread is too high and should be sold, 
while a low negative Z-score means the spread is too low and should be bought.

"""
"""
A mean reversion strategy works on the principle that prices or returns eventually move back towards their mean or average. 
Here’s how it works concretely:
1- Identify a pair of assets: The first step is to identify a pair of assets that are cointegrated. 
This means that even though their prices may move independently in the short term, they tend to move together in the long term.
2- Calculate the spread: The spread is the difference between the prices of the two assets. 
If the assets are cointegrated, the spread will be stationary or mean-reverting.
3- Calculate the Z-score: The Z-score is a measure of how far away the current spread is from its mean in terms of standard deviations. 
It’s calculated as:
Z=σX−μ​
where X is the current spread, μ is the mean of the spread, and σ is the standard deviation of the spread.
The standard deviation gives you a measure of how much the spread deviates from its mean on average. 
In the context of a mean reversion strategy, a larger standard deviation would mean that the spread deviates more from the mean, 
potentially providing more trading opportunities. 
However, it also means more risk as the price can deviate further from the mean before reverting back.

4- Generate trading signals: Trading signals are generated based on the Z-score. Here are the general rules:
    * Go long on the spread: If the Z-score is below a certain negative threshold (say -2), 
    this means the spread is too low compared to its mean. The expectation is that the spread will increase, so you should go long on the spread. 
    This involves buying the underperforming asset and selling the outperforming asset.

    * Go short on the spread: If the Z-score is above a certain positive threshold (say +2), 
    this means the spread is too high compared to its mean. 
    The expectation is that the spread will decrease, so you should go short on the spread. 
    This involves selling the underperforming asset and buying the outperforming asset.

Exit the trade: You can exit the trade when the Z-score crosses zero, which means the spread has reverted to its mean.

"""
