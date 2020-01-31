import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream2 import StreamConn
from config import *
from timeloop import Timeloop
import time
import os
from pprint import pprint

conn = StreamConn(ALP_KEY, ALP_SECRET_KEY)

# need to set up alpaca_api_key as enviromental variable OR make the key be an argument for StreamConn?
@conn.on(r'.*')
async def on_data(conn, channel, data):
    print(channel)
    pprint(data)

# A.'symbol' --> specifies what stock you want to monitor --> currently I don't know what it's working for time and such
conn.run(['trade_updates', 'A.FCEL'])