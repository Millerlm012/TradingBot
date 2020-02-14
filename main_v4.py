from datetime import datetime
from config import *
import pytz
import alpaca_trade_api as tradeapi
import threading
import simplejson
from alpaca_trade_api.stream2 import StreamConn
from pprint import pprint
import sys
import schedule
import pandas as pd
import numpy as np

'''main_v4 will be using pandas dataframe to organize data --> will also be running checking for plays throughout the day - not 5 minute chunks'''

'''
NOTES:
- reorganize code / clean

BUGS:
- line 186 -> if day_ticker < ending_time_minutes --> if program is started mid day the logic won't work
'''


# all lists used for storing stock data
all_stock_data = [0]


# go_time --> 34199 is the time the market opens in sec --> (9 * 3600) + (30 * 60) - 1
go_time = 34200
tz_ny = pytz.timezone('America/New_York')
choice_of_stock = 'AAPL'

# setting up alpaca api and StreamConn
api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY, ALP_ENDPOINT)
api_paper = tradeapi.REST(ALP_PAPER_KEY, ALP_PAPER_SECRET_KEY, ALP_PAPER_ENDPOINT)
conn = StreamConn(ALP_KEY, ALP_SECRET_KEY)

# tickers are aggregator's used to keep track of the program throughout the day
day_ticker = 0
response_ticker = 0
ending_time_minutes = 360

'''
def is_market_open():
    current_time = datetime.now(tz_ny)
    opening_time = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    closing_time = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
    if closing_time >= current_time >= opening_time:
        print('the market is open... ' + str(current_time) + ' starting program')
        conn.run(['trade_updates', 'AM.' + choice_of_stock])
    else:
        time_schedule()
def time_schedule():
    current_time = datetime.now(tz_ny)
    print(str(current_time) + ' --- program will start at 09:30')
    schedule.every().day.at('09:30').do(start_program())
'''


def start_program():
    current_time = datetime.now(tz_ny)
    print('main program starting at -- ' + str(current_time))
    conn.run(['trade_updates', 'AM.' + choice_of_stock])


# functions used for calculations and threading tasks
def calculate_5_minute_averages():
    average = (minute_1_dif[0] + minute_2_dif[0] + minute_3_dif[0] + minute_4_dif[0] + minute_5_dif[0]) / 5
    average_doubled = average * 2
    minute_5_average.append(average)
    minute_5_average_doubled.append(average_doubled)


def minute_6_calculations():
    if minute_6_dif[0] >= minute_5_average_doubled[0]:
        print('minute_6_dif >= minute_5_average_doubled --> carrying out calculations for bar 1')
        minute_6_50_percent.append(minute_6_dif[0] / 2)
        minute_6_50_percent_price.append(minute_6_50_percent[0] + minute_6_high_low[1])
        stop_loss.append(minute_6_high_low[0] - round(minute_6_50_percent[0], 2))
    else:
        reset_ticker_and_variables()
        print('minute_6_dif !>= minute_5_average_doubled --> reset ticker and variables')


def minute_7_calculations():
    if minute_7_high_low[1] >= minute_6_50_percent_price[0]:
        print('minute_7_high_low[1] >= minute_6_50_percent_price[0]')
        if minute_6_high_low[0] + .05 >= minute_7_high_low[0] >= minute_6_high_low[0] - .05:
            print('minute_7_high_low[1] >= minute_6_50_percent_price[0] --> waiting for minute 8 to decide 3 bar play')
        else:
            reset_ticker_and_variables()
            print('minute_6_high_low[0] + .05 !>= minute_7_high_low[0] !>= minute_6_high_low[0] - .05 --> reset ticker and variables')
    else:
        reset_ticker_and_variables()
        print('minute_7_high_low[1] !>= minute_6_50_percent_price[0] --> reset ticker and variables')


def minute_8_buy_stock():
    global choice_of_stock

    account_info = api_paper.get_account()
    equity = account_info.equity
    risk = int(equity) * .01
    dif_entry_price_stop_loss.append(entry_price[0] - stop_loss[0])
    shares_decimal = risk / dif_entry_price_stop_loss[0] * .25
    shares = round(shares_decimal[0])
    net_profit = dif_entry_price_stop_loss[0] * 2
    target = entry_price + net_profit

    api_paper.submit_order(symbol=choice_of_stock, qty=shares, side='buy', type='stop_limit', time_in_force='day', limit_price=target, stop_price=stop_loss)

    reset_ticker_and_variables()


def reset_ticker_and_variables():
    global response_ticker
    response_ticker = 0
    del minute_1_high_low[:]
    del minute_1_dif[:]
    del minute_2_high_low[:]
    del minute_2_dif[:]
    del minute_3_high_low[:]
    del minute_3_dif[:]
    del minute_4_high_low[:]
    del minute_4_dif[:]
    del minute_5_high_low[:]
    del minute_5_dif[:]
    del minute_6_high_low[:]
    del minute_6_dif[:]
    del minute_7_high_low[:]
    del minute_7_dif[:]
    del minute_8_high_low[:]
    del minute_8_dif[:]
    del entry_price[:]
    del stop_loss[:]
    del dif_entry_price_stop_loss[:]
    del last_trade_lst[:]


# StreamConn being used to collect data on per minute basis --> defined using the channel argument --> runs until an error occurs... how to kill it
@conn.on(r'^AM$')
async def on_data(conn, channel, data):
    global response_ticker
    global day_ticker
    global ending_time_minutes
    global last_trade_lst
    timenow = datetime.now(tz_ny)
    print(channel)
    pprint(str(timenow) + ' ' + str(data))
    # add time stamps to the stock data in list
    all_stock_data.append(data)

    if day_ticker < ending_time_minutes:

        response_ticker += 1
        day_ticker += 1
        last_trade = api.polygon.last_trade(choice_of_stock)
        last_trade_lst.append(last_trade.price)
        last_trade_lst = list(np.around(np.array(last_trade_lst), 2))

        if response_ticker == 1:
            minute_1_high_low.append(data.high)
            minute_1_high_low.append(data.low)
            minute_1_dif.append(minute_1_high_low[0] - minute_1_high_low[1])

        elif response_ticker == 2:
            minute_2_high_low.append(data.high)
            minute_2_high_low.append(data.low)
            minute_2_dif.append(minute_2_high_low[0] - minute_2_high_low[1])

        elif response_ticker == 3:
            minute_3_high_low.append(data.high)
            minute_3_high_low.append(data.low)
            minute_3_dif.append(minute_3_high_low[0] - minute_3_high_low[1])

        elif response_ticker == 4:
            minute_4_high_low.append(data.high)
            minute_4_high_low.append(data.low)
            minute_4_dif.append(minute_4_high_low[0] - minute_4_high_low[1])

        elif response_ticker == 5:
            minute_5_high_low.append(data.high)
            minute_5_high_low.append(data.low)
            minute_5_dif.append(minute_5_high_low[0] - minute_5_high_low[1])
            minute_5_average_thread = threading.Thread(name='calculate average of 5 minutes', target=calculate_5_minute_averages())
            minute_5_average_thread.start()

        elif response_ticker == 6:
            minute_6_high_low.append(data.high)
            minute_6_high_low.append(data.low)
            minute_6_dif.append(minute_6_high_low[0] - minute_6_high_low[1])
            minute_6_calculations_thread = threading.Thread(name='perform minute 6 calculations', target=minute_6_calculations())
            minute_6_calculations_thread.start()

        elif response_ticker == 7:
            minute_7_high_low.append(data.high)
            minute_7_high_low.append(data.low)
            minute_7_dif.append(minute_7_high_low[0] - minute_7_high_low[1])
            minute_7_calculations_thread = threading.Thread(name='perform minute 7 calculations', target=minute_7_calculations())
            minute_7_calculations_thread.start()

        elif response_ticker == 8:
            minute_8_high_low.append(data.high)
            minute_8_high_low.append(data.low)
            minute_8_dif.append(minute_8_high_low[0] - minute_8_high_low[1])

            if last_trade_lst[0] >= minute_7_high_low[0]:
                entry_price.append(last_trade_lst[0])
                print('buying stock at ' + str(entry_price[0]))
                minute_8_thread = threading.Thread(name='complete minute 8 task', target=minute_8_buy_stock())
                minute_8_thread.start()
            else:
                print('minute_8[59] !>= minute_7_high_low[0] --> resetting ticker and variables')
                reset_ticker_and_variables()

        else:
            # killing program at designated time
            file = open('all_stock_data', 'w')
            simplejson.dump(all_stock_data, file)
            file.close()
            sys.exit('ending program --> market closes in 30 minutes')


if __name__ == '__main__':
    start_program()