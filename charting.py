import pandas as pd
import plotly.graph_objects as go
import alpaca_trade_api as tradeapi
from datetime import datetime
from config import *

'''
NOTES:
- Find way to make the x axis on the chart be time values --> pd.timestamps ?
'''

api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY, ALP_ENDPOINT)

# setting options on pd df's to allow me to view all of the data with no "..."
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


time_frame = pd.date_range('2020-03-30T09:30:00.000Z', '2020-03-30T16:00:00.000Z', freq='M')


# pulling in the data from .txts
openings = open('C:/Users/mille/PycharmProjects/Trading/Paper/openings.txt').read().splitlines()
closings = open('C:/Users/mille/PycharmProjects/Trading/Paper/closings.txt').read().splitlines()
highs = open('C:/Users/mille/PycharmProjects/Trading/Paper/highs.txt').read().splitlines()
lows = open('C:/Users/mille/PycharmProjects/Trading/Paper/lows.txt').read().splitlines()
time = open('C:/Users/mille/PycharmProjects/Trading/Paper/time.txt').read().splitlines()
time_2 = open('C:/Users/mille/PycharmProjects/Trading/Paper/time_2.txt').read().splitlines()

# converting all lists of data to floats
openings = [float(i) for i in openings]
closings = [float(i) for i in closings]
highs = [float(i) for i in highs]
lows = [float(i) for i in lows]
time = [int(i) for i in time]

# you shouldn't even need to convert to a dataframe... you should be able to just call the lists and get the same results
# takings data and making them tuples to then be created to df
data_tuples = list(zip(openings, closings, highs, lows))
# df = pd.DataFrame(data_tuples, columns=['openings', 'closings', 'highs', 'lows'], index=['time'])
df = pd.DataFrame()
df['openings'] = openings
df['closings'] = closings
df['highs'] = highs
df['lows'] = lows

print(df)

data = api.get_barset('WBA', '1Min', limit=316, start='2020-01-03 16:00:00-0500').df

# fig = go.Figure(data=[go.Candlestick(x=data['time'], open=data['open'], close=data['close'], high=data['high'], low=data['low'])])
fig = go.Figure(data=[go.Candlestick(x=time_2, open=df['openings'], close=df['closings'], high=df['highs'], low=df['lows'])])
fig_2 = go.Figure(data=[go.Candlestick(x=time, open=df['openings'], close=df['closings'], high=df['highs'], low=df['lows'])])

fig_2.show()
