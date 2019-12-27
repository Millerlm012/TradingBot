import alpaca_trade_api as tradeapi
from datetime import datetime
import time
from config import *

# need to specify if you want this to be paper... Does the

# starting time to find delay
start_time = time.time()

# setting api keys
api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY)

# setting date/time
start = datetime(2019, 12, 18)
end = datetime(2019, 12, 19)

# pulling historical data from whatever stock listed - using alpaca/polygon
# data = api.polygon.historic_agg('minute', 'APPL', limit=1000).df

# !!!!these two return url/internal errors!!!!!
# data = api.polygon.historic_agg_v2('APPL', 2019-12-18, timespan=None, _from=None, to=None).df
# quotes = api.polygon.historic_quotes('APPL', 2019-12-18, limit=None)

# ending time to find delay
end_time = time.time()
stopWatch = (end_time - start_time)

print()
print('time taken to communicate with polygon = ' + str(stopWatch) + ' secs')

