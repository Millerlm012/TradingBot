# GOAL = write algorithm to find stocks following the 3 bar play

# checking out IEX api for gathering stock data
import os

from iexfinance.stocks import Stock
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from config import *

# setting iex api version to test [sandbox] - use sandbox api keys
os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
os.environ['IEX_TOKEN'] = IEX_API_KEY

# do I need the api key for actual requests?

# Returning amzn balance
amzn = Stock('AMZN')
amzn_balance_lst = []
amzn_balance_lst = amzn.get_balance_sheet()

amzn_balance_df = pd.DataFrame(amzn_balance_lst)
print(amzn_balance_df)

# keep the output separated for now
print(" ")
print("--------------------------------------------------------------------- ")
print(" ")


# get historical prices of stock FOR THE PAST MONTH - assuming use batch to return multiple
# put historical_prices into pandas dataframe
amzn_hist_lst = []
amzn_hist_lst = amzn.get_historical_prices()

# making list into dataframe - (df = dataframe)
amzn_hist_df = pd.DataFrame(amzn_hist_lst)
print(amzn_hist_df)


# returns amzn real time price/quote - for multiple symbols use tuple/batch.get_price()
amzn_price = amzn.get_price()
print(amzn_price)