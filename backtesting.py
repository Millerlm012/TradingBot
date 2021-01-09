import itertools
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime
from config import *
import yfinance as yf

'''
NOTES:
    - double check bar 2 calculations
'''

# setting options on pd df's to allow me to view all of the data with no "..."
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# what does the below line of code do?
# pd.set_option('display.max_colwidth', -1)
# pd.set_option('display.max_colwidth', None) --> is the proper way to write the code now

api = tradeapi.REST(ALP_KEY, ALP_SECRET_KEY, ALP_ENDPOINT)
api_paper = tradeapi.REST(ALP_PAPER_KEY, ALP_PAPER_SECRET_KEY, ALP_PAPER_ENDPOINT)

data = yf.download('WBA', start='2020-04-03', end='2020-04-04', interval='1m')
# data.to_csv(r'C:\Users\mille\PycharmProjects\TradingBot\Paper\yfinance_data.csv')

highs = data.iloc[:,1]
highs_rounded = round(highs, 2)
lows = data.iloc[:,2]
lows_rounded = round(lows, 2)
dif = []


def calculate_differences():
    z = 0
    for i in range(390):
        # dif = differences of high and lows each minute
        dif.append([highs[z] - lows[z]])
        z += 1


def last_5_minute_average():

    x = 5
    averages = []
    for i in range(385):
        sum = (dif_rounded[x - 5] + dif_rounded[x - 4] + dif_rounded[x - 3] + dif_rounded[x - 2] + dif_rounded[x - 1]) / 5
        x += 1
        averages.append(sum)
    averages_rounded = [round(i, 2) for i in averages]
    print('averages rounded -', averages_rounded)
    averages_doubled = [i * 2 for i in averages]
    averages_doubled_rounded = [round(i, 2) for i in averages_doubled]
    print('averages doubled rounded -', averages_doubled_rounded)
    return averages_doubled_rounded


def three_bar_play(averages_doubled_rounded):

    x = 5
    # dif_without_5 is dif_roudned without first 5 elements --> same with lows and highs
    dif_without_5 = dif_rounded[x:]
    highs_without_5 = highs_rounded[x:]
    lows_without_5 = lows_rounded[x:]
    print('dif without 5 =', dif_without_5)
    print('length of dif rounded =', len(dif_rounded))
    print('length of dif without 5 =', len(dif_without_5))
    print('length of averages doubled rounded =', len(averages_doubled_rounded))

    bar_1 = []
    half_of_bar_1 = []
    y = 0
    z = 0
    q = 0
    for i in dif_without_5:
        # bar 1 calculation
        if dif_without_5[y] >= averages_doubled_rounded[y]:
            z += 1
            bar_1.append(dif_without_5[y])
            half_of_bar_1.append((dif_without_5[y] * .5) + lows_without_5[y])
            print(dif_without_5[y], '>=', averages_doubled_rounded[y], '--> Success --> Total bar ones =', z)

            # bar 2 calculation
            if lows_without_5[y + 1] >= half_of_bar_1[q]:
                print('PASSED step one of bar 2 -', lows_without_5[y + 1], '>=', half_of_bar_1[q])
                q += 1

                # part 2 of bar 2 calculation
                if highs_without_5[y] + .05 >= highs_without_5[y + 1] >= highs_without_5[y] - .05:
                    print('PASSED step two of bar 2 -', highs_without_5[y] + .05, '>=', highs_without_5[y + 1], '>=', highs_without_5[y] - .05)
                    print('acceptable play - would let alpaca do the rest of the work at', y, 'minute')
                else:
                    print('did NOT pass step two of bar 2 -', highs_without_5[y] + .05, '!>=', highs_without_5[y + 1], '!>=', highs_without_5[y] - .05)
            else:
                print('did NOT pass step one of bar 2 -', lows_without_5[y + 1], '!>=', half_of_bar_1[q])
                q += 1
            y += 1
        else:
            print(dif_without_5[y], '!>=', averages_doubled_rounded[y])
            y += 1
    print('completed the function')


calculate_differences()
# flattening the list of lists
chain_object = itertools.chain.from_iterable(dif)
flattened_dif = list(chain_object)
dif_rounded = [round(i, 2) for i in flattened_dif]
print('dif rounded -', dif_rounded)
last_5_minute_average()
three_bar_play(averages_doubled_rounded=last_5_minute_average())
