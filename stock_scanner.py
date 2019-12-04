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

# got tired of writing out the entire statement
Token = token = IEX_API_KEY

# setting iex api version to test [sandbox] - use sandbox api keys
os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
os.environ['IEX_TOKEN'] = IEX_API_KEY


'''NOTE: i don't think i need the two parts in the function

def getCompanyHistory():
    amzn_hist = amazon.get_historical_data('AMZN', Token)
    return(amzn_hist)
    
that should be plenty

'''


# attempting to get previous data
def getCompanyHistory():
    amazon = Stock('AMZN', Token)
    amzn_hist = amazon.get_historical_data('AMZN', Token)
    return(amzn_hist)

# attempting to retrieve (CURRENT?) stock info and format it to a pandas dataframe
def getCompanyInfo():
    amzn = Stock('AMZN', Token)
    amzn_info = amzn.get_company()
    return(amzn_info)

amzn_info_to_df = []
