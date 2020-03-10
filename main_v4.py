from datetime import datetime
from config import *
import pytz
import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream2 import StreamConn
from pprint import pprint
import sys
import schedule
import pandas as pd

'''main_v4 will be using pandas dataframe to organize data --> will also be running checking for plays throughout the day - not 5 minute chunks'''

'''
NOTES:
- reorganize code / clean
- Figure out how to properly call the dictionary of dictionaries and properly add to them and stuff
- You will be getting the price each minute throughout the day and the highs and lows.... Technically you should be able to graph that at the end of the day
--------------------------------------------------------------------------------------------------------------------------------
Dictionary Diagram:
{'min_x': {'high': '', 'low': '', 'dif.': '', 'price': '', 'percent': '', 'avg.': '', 'percent_price': '', 'stop_loss': '', 'entry_price': ''}
--------------------------------------------------------------------------------------------------------------------------------
DATAFRAME DIAGRAM:
        [0]     [1]     [2]     [3]     [4]       [5]        [6]                [7]         [8]           ----->   elements from dictionary
        high    low     dif.    price   percent   avg.       percent_price     stop_loss   entry_price
0       NaN     NaN     NaN     NaN     NaN       NaN        NaN               NaN         NaN
1       ' ---------------------------------------- Values --------------------------------------------- '
...     ' ---------------------------------------- Values --------------------------------------------- '
360     ' ---------------------------------------- Values --------------------------------------------- '
--------------------------------------------------------------------------------------------------------------------------------
BUGS:
'''

# dictionary of dictionaries used for storing data
all_stock_data_lst = []
all_stock_data = {'min_0': 'N/A'}
stock_data_keys = {
    'high': '',
    'low': '',
    'dif.': '',
    'price': '',
    'percent': '',
    'avg.': '',
    'percent_price': '',
    'stop_loss': '',
    'entry_price': '',
}

# making all of the keys for the all_stock_data dictionary
y = 1
for i in range(361):
    all_stock_data['min_' + str(y)] = stock_data_keys
    y += 1

# go_time = 9:30am in seconds | tz_ny = setting the timezone to New York | choice_of_stock = 'choice of stock'
go_time = 34200
tz_ny = pytz.timezone('America/New_York')
choice_of_stock = 'AAPL'

# setting up alpaca api and StreamConn
api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY, ALP_ENDPOINT, api_version='v2')
api_paper = tradeapi.REST(ALP_PAPER_KEY, ALP_PAPER_SECRET_KEY, ALP_PAPER_ENDPOINT, api_version='v2')
conn = StreamConn(ALP_KEY, ALP_SECRET_KEY)

# tickers are aggregator's used to keep track of the program throughout the day
stage = 0
minute_ticker = 0
response_ticker = 0
ending_time_minutes = 360


# use schedule to 'schedule' the start of the program for opening time of NY stock exchange
def start_program():
    current_time = datetime.now(tz_ny)
    print('main program starting at -- ' + str(current_time))
    conn.run(['trade_updates', 'AM.' + choice_of_stock])


# 08:30 --> central time --> 09:30 eastern time --> deal with time zone later
# schedule.every().day.at("08:30").do(start_program)


def last_5_minute_average():
    global stage

    # had to multiply by .2 --> equal to dividing by 5
    sum_of_5 = all_stock_data['min_' + str(minute_ticker - 5)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 4)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 3)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 2)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 1)]['dif.']
    average = int(sum_of_5) / 5
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = str(average)
    stage += 1


# stock_data[[minute_ticker - 1][3]] * 2 --> retrieves minute 5 avg. and doubles it
def minute_6_calculations():
    global stage

    # setting the data that doesn't change to be carried over into the next minute
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = all_stock_data['min_' + str(minute_ticker - 1)]['avg.']

    if all_stock_data['min_' + str(minute_ticker)]['dif.'] >= all_stock_data['min_' + str(minute_ticker - 1)]['avg.'] * 2:
        print('minute_6_dif >= minute_5_average_doubled')
        stage += 1

        # storing the percent and percent_price
        # to find percent --> taking the difference of high and low and dividing by 2 --> need to multiply by 1/2 for syntax purposes
        all_stock_data['min_' + str(minute_ticker)]['percent'] = all_stock_data['min_' + str(minute_ticker)]['dif.'] * int(.5)
        # to calculate the percent_price are you using the percent of minute_6 and adding it to the dif. of minute_6
        all_stock_data['min_' + str(minute_ticker)]['percent_price'] = all_stock_data['min_' + str(minute_ticker)]['low'] + all_stock_data['min_' + str(minute_ticker)]['percent']
    else:
        # ! rewrite the reset function !
        reset_stage()
        print('minute_6_dif !>= minute_5_average_doubled --> reset_stage()')


def minute_7_calculations():
    global stage

    # setting the data that doesn't change to be carried over into the next minute
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = all_stock_data['min_' + str(minute_ticker - 1)]['avg.']
    all_stock_data['min_' + str(minute_ticker)]['percent'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent']
    all_stock_data['min_' + str(minute_ticker)]['percent_price'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent_price']

    if all_stock_data['min_' + str(minute_ticker)]['low'] >= all_stock_data['min_' + str(minute_ticker - 1)]['percent_price']:
        print('minute_7_low >= minute_6_50_percent_price')

        # shouldn't the comparison be if minute_7 high is greater than minute_6 percent_price + .05 or less than minute_6 percent_price - .05
        # had to convert the .05 to strings??? --> is it just for the if statement
        if all_stock_data['min_' + str(minute_ticker - 1)]['high'] + str(.05) >= all_stock_data['min_' + str(minute_ticker)]['high'] >= all_stock_data['min_' + str(minute_ticker)]['high'] + str(-.05):
            print('minute_6_high + (.05) >= minute_7_high >= minute_6_high - (.05) --> going to minute_8')
            stage += 1
            # decide_three_bar() --> jumps right into minute_8
            decide_three_bar()

        else:
            reset_stage()
            print('minute_6_high + .05 !>= minute_7_high !>= minute_6_high - .05 --> reset stage')
    else:
        reset_stage()
        print('minute_7_low !>= minute_6_50_percent_price --> reset stage')


def minute_8_buy_stock():
    global choice_of_stock
    global stage

    # setting the data that doesn't change to be carried over into the next minute
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = all_stock_data['min_' + str(minute_ticker - 1)]['avg.']
    all_stock_data['min_' + str(minute_ticker)]['percent'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent']
    all_stock_data['min_' + str(minute_ticker)]['percent_price'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent_price']

    account_info = api_paper.get_account()
    # setting stop_loss at the low of bar 7 and appending it to all_stock_data['min_8']['stop_loss']
    stop_loss = all_stock_data['min_' + str(minute_ticker - 1)]['low']
    all_stock_data['min_' + str(minute_ticker)]['stop_loss'] = stop_loss
    # setting entry_price at the high of bar 7 and appending it to all_stock_data['min_8']['entry_price']
    entry_price = all_stock_data['min_' + str(minute_ticker - 1)]['high']
    all_stock_data['min_' + str(minute_ticker)]['entry_price'] = entry_price
    # main algorithm --> need to fix apparently
    dif_entry_price_stop_loss = int(entry_price) - int(stop_loss)
    target_change = dif_entry_price_stop_loss * 2
    target_price = int(entry_price) + int(target_change)
    equity = account_info.equity
    risk = int(equity) * .01
    shares_decimal = risk / dif_entry_price_stop_loss * .25
    shares = round(shares_decimal)

    if equity >= 27000:

        api_paper.submit_order(
            # submit the order as a limit (buys stock once it reaches "correct" price) -> uses bracket to decide when to sell stock (either at limit or stop loss)
            symbol=choice_of_stock,
            qty=shares,
            side='buy',
            type='limit',
            time_in_force='day',
            limit_price=entry_price,
            order_class='bracket',
            take_profit=dict(
                limit_price=target_price,
            ),
            stop_loss=dict(
                stop_price=stop_loss,
            )
        )

        reset_stage()

    else:
        reset_stage()


def decide_three_bar():
    if stage == 1:
        last_5_minute_average()

    elif stage == 2:
        minute_6_calculations()

    elif stage == 3:
        minute_7_calculations()

    elif stage == 4:
        minute_8_buy_stock()


def reset_stage():
    global stage
    stage = 1


# StreamConn being used to collect data on per minute basis --> defined using the channel argument --> runs until an error occurs... how to kill it
@conn.on(r'^AM$')
async def on_data(conn, channel, data):
    global stage
    global response_ticker
    global minute_ticker
    global ending_time_minutes

    timenow = datetime.now(tz_ny)
    print(channel)
    pprint(str(timenow) + ' ' + str(data))

    all_stock_data_lst.append(str(timenow) + '---' + str(data))

    if minute_ticker < ending_time_minutes:

        response_ticker += 1
        minute_ticker += 1

        # if last_trade is taking too long to retrieve data put it into a new thread
        last_trade = api.polygon.last_trade(choice_of_stock)
        last_trade_price = round(last_trade.price, 2)
        # storing data in dictionary of dictionaries
        all_stock_data['min_' + str(minute_ticker)]['high'] = data.high
        all_stock_data['min_' + str(minute_ticker)]['low'] = data.low
        all_stock_data['min_' + str(minute_ticker)]['dif.'] = data.high - data.low
        all_stock_data['min_' + str(minute_ticker)]['price'] = last_trade_price

        if response_ticker == 5:
            stage += 1

        # deciding which stage of the play the program is on and running the appropriate function
        decide_three_bar()

    else:
        # converting all_stock_data and stock_data into dataframe
        df_all_stock_data = pd.DataFrame(all_stock_data).swapaxes('index', 'columns')
        df_stock_data_lst = pd.DataFrame(all_stock_data_lst)
        df_all_stock_data.to_csv(r'C:\Users\mille\PycharmProjects\TradingBot\Paper\all_stock_data_dataframe.csv')
        df_stock_data_lst.to_csv(r'C:\Users\mille\PycharmProjects\TradingBot\Paper\all_stock_data_lst.csv')
        # I think sys.exit is killing the program
        sys.exit('ending program --> market closes in 30 minutes')

# while True:
#    schedule.run_pending()

if __name__ == '__main__':
    start_program()
