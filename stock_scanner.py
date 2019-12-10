# GOAL = write algorithm to find stocks following the 3 bar play

# checking out IEX api for gathering stock data
import os

from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from iexfinance.stocks import get_earnings_today
from iexfinance.stocks import get_historical_data
from config import *

# setting iex api version to test [sandbox] - use sandbox api keys
os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
os.environ['IEX_TOKEN'] = IEX_API_KEY

amzn = Stock('AMZN')
amzn_balance = amzn.get_balance_sheet()

print(amzn_balance)
