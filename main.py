from datetime import datetime, timedelta
from timeloop import Timeloop
from yahoo_fin import stock_info as si
from config import *
import pytz
import time
import alpaca_trade_api as tradeapi
import threading
import simplejson
import numpy as np

'''
Thread 1 will pull a stock's price and store the price for every second the market is open --> 234000 seconds

It will send responses to thread x every 60 sec for 4 minutes - then once for the 5th, 6th, 7th, and 8th min
(repeating when told from thread x)
'''

'''
NOTES:
WATCH minute_8_calculation --> using try except startment to determine if that will run properly 

REWRITE minute_x_calculations --> repetitive code can be transferred into functions to be called later

!! REORGANIZE code into multiple files later !! 
'''

# all lists used for storing stock data
stock_every_second = []

minute_1 = []
minute_1_high_low = []
minute_1_dif = []

minute_2 = []
minute_2_high_low = []
minute_2_dif = []

minute_3 = []
minute_3_high_low = []
minute_3_dif = []

minute_4 = []
minute_4_high_low = []
minute_4_dif = []

minute_5 = []
minute_5_high_low = []
minute_5_dif = []
minute_5_average = []
minute_5_average_doubled = []

minute_6 = []
minute_6_high_low = []
minute_6_dif = []
minute_6_50_percent = []
minute_6_50_percent_price = []

minute_7 = []
minute_7_high_low = []
minute_7_dif = []
stop_loss = []

minute_8 = []
minute_8_high_low = []
minute_8_dif = []
entry_price = []
dif_entry_price_stop_loss = []

# go_time --> 34199 is the time the market opens in sec --> (9 * 3600) + (30 * 60) - 1
go_time = 34199
tz_ny = pytz.timezone('America/New_York')
choice_of_stock = 'FCEL'
get_stock_price_now = si.get_live_price(choice_of_stock)

# setting up alpaca api --> in paper
api = tradeapi.REST(ALP_PAPER_KEY, ALP_PAPER_SECRET_KEY, ALP_PAPER_ENDPOINT)

# timeloop used for get_stock_price_all_day | tickers used for keeping track of the time in seconds from the start of the day | time_to_run determines how long to run the program until 15:30
tl = Timeloop()
day_ticker = 0
response_ticker = 0
time_to_run = 0
ending_time = 55800


# use functions to stock price to proper list
def add_stock_to_stock_every_second():
    stock_every_second.append(get_stock_price_now)


def add_stock_to_min_1():
    minute_1.append(get_stock_price_now)


def add_stock_to_minute_2():
    minute_2.append(get_stock_price_now)


def add_stock_to_minute_3():
    minute_3.append(get_stock_price_now)


def add_stock_to_minute_4():
    minute_4.append(get_stock_price_now)


def add_stock_to_minute_5():
    minute_5.append(get_stock_price_now)


def add_stock_to_minute_6():
    minute_6.append(get_stock_price_now)


def add_stock_to_minute_7():
    minute_7.append(get_stock_price_now)


def add_stock_to_minute_8():
    minute_8.append(get_stock_price_now)


def is_market_open():
    global time_to_run
    global ending_time

    current_time = datetime.now(tz_ny)
    opening_time = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    current_time_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
    if current_time >= opening_time:
        time_to_run = ending_time - current_time_seconds
        print('the market is open... ' + str(current_time) + ' starting time loop next second')
        tl.start(block=True)
    else:
        sleep_until_market_opens()


# tells program to wait until market opens before proceeding
def sleep_until_market_opens():
    global time_to_run

    first_time_ny = datetime.now(tz_ny)

    # current time in new york ---> converted to seconds
    current_new_york_time = first_time_ny.hour * 3600 + first_time_ny.minute * 60 + first_time_ny.second

    wait_time_secs = go_time - current_new_york_time
    time_to_run = ending_time - current_new_york_time
    wait_time_min = wait_time_secs / 60

    print('program will wait for ' + str(wait_time_min) + ' mins')

    time.sleep(wait_time_secs)

    tl.start(block=True)


# starting process 1 --> get stock price every second and store data properly
@tl.job(interval=timedelta(seconds=1))
def get_stock_price_all_day():
    global day_ticker
    global response_ticker
    global stock_every_second
    global minute_8

    time_now = datetime.now(tz_ny)
    print('main program loop running ' + str(time_now))

    # runs the program until 15:30
    if day_ticker < time_to_run:

        day_ticker += 1
        response_ticker += 1

        add_stock_to_stock_every_second()

        if response_ticker <= 60:
            add_stock_to_min_1()
            if response_ticker == 60:
                minute_1_thread = threading.Thread(name='complete minute 1 task', target=minute_1_high_low_calculation())
                minute_1_thread.start()

        elif response_ticker <= 120:
            add_stock_to_minute_2()
            if response_ticker == 120:
                minute_2_thread = threading.Thread(name='complete minute 2 task', target=minute_2_high_low_calculation())
                minute_2_thread.start()

        elif response_ticker <= 180:
            add_stock_to_minute_3()
            if response_ticker == 180:
                minute_3_thread = threading.Thread(name='complete minute 3 task', target=minute_3_high_low_calculation())
                minute_3_thread.start()

        elif response_ticker <= 240:
            add_stock_to_minute_4()
            if response_ticker == 240:
                minute_4_thread = threading.Thread(name='complete minute 4 task', target=minute_4_high_low_calculation())
                minute_4_thread.start()

        elif response_ticker <= 300:
            add_stock_to_minute_5()
            if response_ticker == 300:
                minute_5_thread = threading.Thread(name='complete minute 5 task', target=minute_5_calculation())
                minute_5_thread.start()

        elif response_ticker <= 360:
            add_stock_to_minute_6()
            if response_ticker == 360:
                minute_6_thread = threading.Thread(name='complete minute 6 task', target=minute_6_calculation())
                minute_6_thread.start()

        elif response_ticker <= 420:
            add_stock_to_minute_7()
            if response_ticker == 420:
                minute_7_thread = threading.Thread(name='complete minute 7 task', target=minute_7_calculation())
                minute_7_thread.start()

        elif response_ticker <= 480:
            add_stock_to_minute_8()
            for i in minute_8:
                if i >= minute_7_high_low[0]:
                    entry_price.append(i)
                    print('i >= minute_7_high_low[0] --> buying stock at ' + str(i))
                    minute_8_thread = threading.Thread(name='complete minute 8 task', target=minute_8_buy_stock())
                    minute_8_thread.start()

                try:
                    if minute_8[59] >= minute_7_high_low[0]:
                        entry_price.append(minute_8[59])
                        print('minute_8[59] >= minute_7_high_low[0] --> buying stock at ' + str(minute_8[59]))
                        minute_8_thread = threading.Thread(name='complete minute 8 task', target=minute_8_buy_stock())
                        minute_8_thread.start()
                    else:
                        print('minute_8[59] !>= minute_7_high_low[0] --> resetting ticker and variables')
                        minute_8_thread = threading.Thread(name='complete minute 8 task', target=reset_ticker_and_variables())
                        minute_8_thread.start()

                except IndexError:
                    print('minute 8 has not reached the 60th second')

    else:
        # stops program at 15:30 --> by using when the day_ticker reaches the correct number of seconds --> saves ticker
        print('stopping the program at ' + str(time_now))
        stock_every_second = list(np.around(np.array(stock_every_second), 2))
        file = open('stock_every_second_save.txt', 'w')
        simplejson.dump(stock_every_second, file)
        file.close()
        tl.stop()


def minute_1_high_low_calculation():
    global minute_1

    minute_1 = list(np.around(np.array(minute_1), 2))
    minute_1_high_low.append(max(minute_1))
    minute_1_high_low.append(min(minute_1))
    minute_1_dif.append(minute_1[0] - minute_1[1])


def minute_2_high_low_calculation():
    global minute_2

    minute_2 = list(np.around(np.array(minute_2), 2))
    minute_2_high_low.append(max(minute_2))
    minute_2_high_low.append(min(minute_2))
    minute_2_dif.append(minute_2[0] - minute_2[1])


def minute_3_high_low_calculation():
    global minute_3

    minute_3 = list(np.around(np.array(minute_3), 2))
    minute_3_high_low.append(max(minute_3))
    minute_3_high_low.append(min(minute_3))
    minute_3_dif.append(minute_3[0] - minute_3[1])


def minute_4_high_low_calculation():
    global minute_4

    minute_4 = list(np.around(np.array(minute_4), 2))
    minute_4_high_low.append(max(minute_4))
    minute_4_high_low.append(min(minute_4))
    minute_4_dif.append(minute_4[0] - minute_4[1])


def minute_5_calculation():
    global minute_5

    minute_5 = list(np.around(np.array(minute_5), 2))
    minute_5_high_low.append(max(minute_5))
    minute_5_high_low.append(min(minute_5))
    minute_5_dif.append(minute_5[0] - minute_5[1])
    minute_5_average.append((minute_1_dif[0] + minute_2_dif[0] + minute_3_dif[0] + minute_4_dif[0] + minute_5_dif[0]) / 5)
    minute_5_average_doubled.append(minute_5_average[0] * 2)


def minute_6_calculation():
    global minute_6

    minute_6 = list(np.around(np.array(minute_6), 2))
    minute_6_high_low.append(max(minute_6))
    minute_6_high_low.append(min(minute_6))
    minute_6_dif.append(minute_6[0] - minute_6[1])
    if minute_6_dif[0] >= minute_5_average_doubled[0]:
        print('minute_6_dif >= minute_5_average_doubled --> carrying out calculations for bar 1')
        minute_6_50_percent.append(minute_6_dif[0] / 2)
        minute_6_50_percent_price.append(minute_6_50_percent[0] + minute_6_high_low[1])
        stop_loss.append(minute_6_high_low[0] - round(minute_6_50_percent[0], 2))
    else:
        reset_ticker_and_variables()
        print('minute_6_dif !>= minute_5_average_doubled --> reset ticker and variables')


def minute_7_calculation():
    global minute_7

    minute_7 = list(np.around(np.array(minute_7), 2))
    minute_7_high_low.append(max(minute_7))
    minute_7_high_low.append(min(minute_7))
    minute_7_dif.append(minute_7[0] - minute_7[1])
    if minute_7_high_low[1] >= minute_6_50_percent_price[0]:
        print('minute_7_high_low[1] >= minute_6_50_percent_price[0]')
        if minute_6_high_low[0] + .05 >= minute_7_high_low[0] >= minute_6_high_low[0] - .05:
            print('minute_7_high_low[1] >= minute_6_50_percent_price[0] --> waiting for minute 8 to decide 3 bar play')
        else:
            reset_ticker_and_variables()
            print('minute_6_high_low[0] + .05 >= minute_7_high_low[0] >= minute_6_high_low[0] - .05 --> reset ticker and variables')
    else:
        reset_ticker_and_variables()
        print('minute_7_high_low[1] >= minute_6_50_percent_price[0] --> reset ticker and variables')


def minute_8_buy_stock():
    reset_ticker_and_variables_minute_8_1()
    global choice_of_stock

    account_info = api.get_account()
    equity = account_info.equity
    risk = int(equity) * .01
    dif_entry_price_stop_loss.append(entry_price[0] - stop_loss[0])
    shares_decimal = risk / dif_entry_price_stop_loss[0] * .25
    shares = round(shares_decimal[0])
    net_profit = dif_entry_price_stop_loss[0] * 2
    target = entry_price + net_profit

    api.submit_order(symbol=choice_of_stock, qty=shares, side='buy', type='stop_limit', time_in_force='day', limit_price=target, stop_price=stop_loss)

    reset_variables_minute_8_2()


def reset_ticker_and_variables():
    global response_ticker
    response_ticker = 0
    del minute_1[:]
    del minute_1_high_low[:]
    del minute_1_dif[:]
    del minute_2[:]
    del minute_2_high_low[:]
    del minute_2_dif[:]
    del minute_3[:]
    del minute_3_high_low[:]
    del minute_3_dif[:]
    del minute_4[:]
    del minute_4_high_low[:]
    del minute_4_dif[:]
    del minute_5[:]
    del minute_5_high_low[:]
    del minute_5_dif[:]
    del minute_6[:]
    del minute_6_high_low[:]
    del minute_6_dif[:]
    del minute_7[:]
    del minute_7_high_low[:]
    del minute_7_dif[:]
    del minute_8[:]
    del minute_8_high_low[:]
    del minute_8_dif[:]
    del entry_price[:]
    del stop_loss[:]
    del dif_entry_price_stop_loss[:]


def reset_ticker_and_variables_minute_8_1():
    global response_ticker
    response_ticker = 0
    del minute_1[:]
    del minute_1_high_low[:]
    del minute_1_dif[:]
    del minute_2[:]
    del minute_2_high_low[:]
    del minute_2_dif[:]
    del minute_3[:]
    del minute_3_high_low[:]
    del minute_3_dif[:]
    del minute_4[:]
    del minute_4_high_low[:]
    del minute_4_dif[:]
    del minute_5[:]
    del minute_5_high_low[:]
    del minute_5_dif[:]
    del minute_6[:]
    del minute_6_high_low[:]
    del minute_6_dif[:]


def reset_variables_minute_8_2():
    del minute_7[:]
    del minute_7_high_low[:]
    del minute_7_dif[:]
    del minute_8[:]
    del minute_8_high_low[:]
    del minute_8_dif[:]
    del entry_price[:]
    del stop_loss[:]
    del dif_entry_price_stop_loss[:]


if __name__ == '__main__':
    is_market_open()
