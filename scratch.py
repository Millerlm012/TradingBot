import alpaca_trade_api as tradeapi
from config import *
import pandas as pd

api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY, ALP_ENDPOINT)

# get daily price data for APPL for the last 5 days
# barset = api.get_barset('APPL', 'day', limit=5)
# appl_bars = barset('APPL')

bars = api.get_barset(['AAPL'], '1D', limit=100, start=pd.Timestamp('2019-12-18', tz='America/New_York').isoformat())
print(bars.df)