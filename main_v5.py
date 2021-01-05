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
- Create graph of data
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
    all_stock_data['min_' + str(y)] = {'high': '', 'low': '', 'dif.': '', 'price': '', 'percent': '', 'avg.': '', 'percent_price': '', 'stop_loss': '', 'entry_price':  ''}
    y += 1

# go_time = 9:30am in seconds | tz_ny = setting the timezone to New York | choice_of_stock = 'choice of stock'
go_time = 34200
tz_ny = pytz.timezone('America/New_York')
choice_of_stock = 'WBA'

# setting up alpaca api and StreamConn
api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY, ALP_ENDPOINT)
api_paper = tradeapi.REST(ALP_PAPER_KEY, ALP_PAPER_SECRET_KEY, ALP_PAPER_ENDPOINT)
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
schedule.every().day.at("08:30").do(start_program)


def last_5_minute_average():
    global stage

    # dividing by 5
    sum_of_5_avg = (all_stock_data['min_' + str(minute_ticker - 5)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 4)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 3)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 2)]['dif.'] + all_stock_data['min_' + str(minute_ticker - 1)]['dif.']) / 5
    sum_of_5_rounded_avg = round(sum_of_5_avg, 2)
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = sum_of_5_rounded_avg
    print('sum of 5 avg', sum_of_5_avg)
    print('sum of 5 rounded avg ', sum_of_5_rounded_avg)
    print('test sum of 5 rounded avg * 2 ', sum_of_5_rounded_avg * 2)
    print('sum of 5 rounded avg * 2 ', str(all_stock_data['min_' + str(minute_ticker)]['avg.']) * 2)


def minute_6_calculations():
    global stage

    # last_5_minute_average being calculated during the 6th minute
    last_5_minute_average()

    # the *2 isn't being calculated in anymore...
    if float(all_stock_data['min_' + str(minute_ticker)]['dif.']) >= float(all_stock_data['min_' + str(minute_ticker)]['avg.']) * 2:
        print('minute 6 difference = ', float(all_stock_data['min_' + str(minute_ticker)]['dif.']))
        print('last 5 minute average doubled = ', float(all_stock_data['min_' + str(minute_ticker)]['avg.']) * 2)
        print('minute_6_dif >= minute_5_average_doubled --> moving to minute_7_calculations')
        stage += 1

        # storing the percent and percent_price
        # to find percent --> taking the difference of high and low and dividing by 2 --> need to multiply by 1/2 for syntax purposes
        all_stock_data['min_' + str(minute_ticker)]['percent'] = all_stock_data['min_' + str(minute_ticker)]['dif.'] * float(.5)
        # to calculate the percent_price are you using the percent of minute_6 and adding it to the dif. of minute_6
        all_stock_data['min_' + str(minute_ticker)]['percent_price'] = all_stock_data['min_' + str(minute_ticker)]['low'] + all_stock_data['min_' + str(minute_ticker)]['percent']
        # printing dictionary values
        print('min_' + str(minute_ticker) + ' all_stock_data --- ' + str(all_stock_data))
        print('min_' + str(minute_ticker) + ' data --- ' + str(all_stock_data['min_' + str(minute_ticker)]))
    else:
        print('minute_6_dif !>= minute_5_average_doubled --> reset_stage()')
        reset_stage()


def minute_7_calculations():
    global stage

    # setting the data that doesn't change to be carried over into the next minute
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = all_stock_data['min_' + str(minute_ticker - 1)]['avg.']
    all_stock_data['min_' + str(minute_ticker)]['percent'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent']
    all_stock_data['min_' + str(minute_ticker)]['percent_price'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent_price']

    if float(all_stock_data['min_' + str(minute_ticker)]['low']) >= float(all_stock_data['min_' + str(minute_ticker - 1)]['percent_price']):
        print('minute_7_low >= minute_6_50_percent_price')

        # shouldn't the comparison be if minute_7 high is greater than minute_6 percent_price + .05 or less than minute_6 percent_price - .05
        # had to convert the .05 to strings??? --> is it just for the if statement
        print(all_stock_data['min_' + str(minute_ticker - 1)]['high'])
        print(all_stock_data['min_' + str(minute_ticker - 1)]['high'] + .05)
        print(all_stock_data['min_' + str(minute_ticker)]['high'])
        print(all_stock_data['min_' + str(minute_ticker - 1)]['high'])
        print(all_stock_data['min_' + str(minute_ticker - 1)]['high'] + -.05)

        if all_stock_data['min_' + str(minute_ticker - 1)]['high'] + .05 >= all_stock_data['min_' + str(minute_ticker)]['high'] >= all_stock_data['min_' + str(minute_ticker - 1)]['high'] + -.05:
            print('minute_6_high + (.05) >= minute_7_high >= minute_6_high - (.05) --> going to minute_8')
            minute_8_buy_stock()

        else:
            print('minute_6_high + .05 !>= minute_7_high !>= minute_6_high - .05 --> reset stage')
            reset_stage()

    else:
        print('minute_7_low !>= minute_6_50_percent_price --> reset stage')
        reset_stage()


def minute_8_buy_stock():
    global choice_of_stock
    global stage

    print('started minute 8 function --- buying process')

    # setting the data that doesn't change to be carried over into the next minute
    all_stock_data['min_' + str(minute_ticker)]['avg.'] = all_stock_data['min_' + str(minute_ticker - 1)]['avg.']
    all_stock_data['min_' + str(minute_ticker)]['percent'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent']
    all_stock_data['min_' + str(minute_ticker)]['percent_price'] = all_stock_data['min_' + str(minute_ticker - 1)]['percent_price']

    account_info = api_paper.get_account()
    # setting stop_loss at the low of bar 7 and appending it to all_stock_data['min_8']['stop_loss']
    stop_loss = all_stock_data['min_' + str(minute_ticker - 1)]['low']
    all_stock_data['min_' + str(minute_ticker - 1)]['stop_loss'] = stop_loss
    # setting entry_price at the high of bar 7 and appending it to all_stock_data['min_8']['entry_price']
    entry_price = all_stock_data['min_' + str(minute_ticker - 1)]['high']
    all_stock_data['min_' + str(minute_ticker - 1)]['entry_price'] = entry_price
    # setting variables that will be the parameters for submitting an order
    dif_entry_price_stop_loss = float(entry_price) - float(stop_loss)
    dif_test_2 = all_stock_data['min_' + str(minute_ticker - 1)]['entry_price'] - all_stock_data['min_' + str(minute_ticker - 1)]['stop_loss']
    dif_test_3 = float(entry_price) - float(stop_loss)
    round_dif_2 = round(dif_test_2, 2)
    target_change = round_dif_2 * 2
    target_price = entry_price + target_change
    target_price_rounded = round(target_price, 2)
    print('target_price = ', target_price)
    print('target_price_rounded = ', target_price_rounded)
    equity = account_info.equity
    buying_power = account_info.buying_power
    print('buying_power = ', buying_power)
    risk = float(equity) * .01

    # if the program already has a position in the market to not buy more stock... wait till the last one has sold out
    if len(api_paper.list_positions()) == 0:

        # calculating number of shares to buy
        total_shares = float(buying_power) / float(entry_price)

        print('total_shares = ' + str(total_shares))
        print('buying power = ' + str(buying_power))
        print('entry price = ' + str(entry_price))
        print('stop loss = ' + str(stop_loss))
        print('dif_entry_price_stop_loss = ' + str(dif_entry_price_stop_loss))
        print('dif_test_2 = ' + str(dif_test_2))
        print('dif_test_2 rounded = ' + str(round_dif_2))
        print('dif_test_3 = ' + str(dif_test_3))

        buying_over_entry = float(buying_power) / float(entry_price)
        buying_over_entry_rounded = round(buying_over_entry, 2)

        print('buying over entry = ' + str(buying_over_entry))
        print('buying over entry rounded = ' + str(buying_over_entry_rounded))

        theoretical_money_lost = buying_over_entry_rounded * round_dif_2
        theoretical_money_lost_rounded = round(theoretical_money_lost, 2)

        print('risk = ' + str(risk))
        print('theoretical money lost = ' + str(theoretical_money_lost))
        print('theoretical money lost rounded = ', theoretical_money_lost_rounded)

        if theoretical_money_lost_rounded > risk:
            money_over = theoretical_money_lost - risk
            number_of_shares_over = money_over / round_dif_2
            shares_to_buy = total_shares - number_of_shares_over
            # shares should be an int... no rounding
            shares_to_buy_int = int(shares_to_buy)
            shares = shares_to_buy_int

            print('attempting to submit order')

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
                    limit_price=target_price_rounded,
                ),
                stop_loss=dict(
                    stop_price=stop_loss,
                )
            )

            print('submitted order successfully')

        else:
            print('minute 8 failed second if statement')
            reset_stage()
    else:
        print('minute 8 failed first if statement')
        reset_stage()


def decide_three_bar():
    if stage == 1:
        minute_6_calculations()

    elif stage == 2:
        minute_7_calculations()


def reset_stage():
    global stage
    stage = 1


# StreamConn being used to collect data on per minute basis --> defined using the channel argument --> runs until an error occurs...
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

        print('minute ' + str(minute_ticker))

        # if last_trade is taking too long to retrieve data put it into a new thread
        last_trade = api.polygon.last_trade(choice_of_stock)
        last_trade_price = round(last_trade.price, 2)
        # storing data in dictionary of dictionaries
        all_stock_data['min_' + str(minute_ticker)]['high'] = round(data.high, 2)
        all_stock_data['min_' + str(minute_ticker)]['low'] = round(data.low, 2)
        # rounding the difference to the nearest cent
        dif_high_and_low = data.high - data.low
        round_dif_high_and_low = round(dif_high_and_low, 2)
        all_stock_data['min_' + str(minute_ticker)]['dif.'] = round_dif_high_and_low
        all_stock_data['min_' + str(minute_ticker)]['price'] = last_trade_price

        if response_ticker == 6:
            print('response_ticker = ' + str(response_ticker))
            stage += 1
            print('stage = ' + str(stage))

        # deciding which stage of the play the program is on and running the appropriate function
        print('on stage ' + str(stage))
        decide_three_bar()

    else:
        # converting all_stock_data and stock_data into dataframe
        df_all_stock_data = pd.DataFrame(all_stock_data).swapaxes('index', 'columns')
        df_stock_data_lst = pd.DataFrame(all_stock_data_lst)
        # edit directory depending on which computer you are running the program on
        df_all_stock_data.to_csv(r'C:\Users\mille\PycharmProjects\Trading\Paper\all_stock_data_dataframe.csv')
        df_stock_data_lst.to_csv(r'C:\Users\mille\PycharmProjects\Trading\Paper\all_stock_data_lst.csv')
        # sys.exit is killing the program
        sys.exit('ending program --> market closes in 30 minutes')


while True:
    schedule.run_pending()


# if __name__ == '__main__':
#   start_program()
