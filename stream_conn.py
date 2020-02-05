from alpaca_trade_api.stream2 import StreamConn
from config import *
from timeloop import Timeloop
from datetime import datetime
import pytz
from pprint import pprint

conn = StreamConn(ALP_KEY, ALP_SECRET_KEY)
tz_ny = pytz.timezone('America/New_York')

stock_data = []
choice_of_stock = 'AAPL'

tl = Timeloop()


# StreamConn being used to collect data
@conn.on(r'^AM$')
async def on_data(conn, channel, data):
    timenow = datetime.now(tz_ny)
    print(channel)
    pprint(str(timenow) + ' ' + str(data))
    stock_data.append(data)


conn.run(['trade_updates', 'AM.' + choice_of_stock])
