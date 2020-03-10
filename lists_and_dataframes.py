import pandas as pd

# testing list of lists and pd dataframes

"""
Using pandas dataframe to reorganize the data collected throughout the day
"""

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
    all_stock_data['min_' + str(y)] = {'high': '', 'low': '', 'dif.': '', 'price': '', 'percent': '', 'avg.': '', 'percent_price': '', 'stop_loss': '', 'entry_price': ''}
    y += 1

minute_ticker = 5
all_stock_data['min_' + str(minute_ticker)]['dif.'] = str(.06)
all_stock_data['min_' + str(minute_ticker - 4)]['dif.'] = str(.05)
all_stock_data['min_' + str(minute_ticker - 3)]['dif.'] = str(.04)
all_stock_data['min_' + str(minute_ticker - 2)]['dif.'] = str(.03)
all_stock_data['min_' + str(minute_ticker - 1)]['dif.'] = str(.02)

minute_5 = all_stock_data['min_' + str(minute_ticker)]['dif.'] = str(.06)
minute_4 = all_stock_data['min_' + str(minute_ticker - 4)]['dif.'] = str(.05)
minute_3 = all_stock_data['min_' + str(minute_ticker - 3)]['dif.'] = str(.04)
minute_2 = all_stock_data['min_' + str(minute_ticker - 2)]['dif.'] = str(.03)
minute_1 = all_stock_data['min_' + str(minute_ticker - 1)]['dif.'] = str(.02)


sum_of_5 = minute_5 + minute_4 + minute_3 + minute_2 + minute_1
average = sum_of_5 * int(.2)
print(average)
print(sum_of_5)


all_stock_data['min_3']['avg.'] = str(average)


print(all_stock_data)

all_stock_data['min_' + str(minute_ticker)]['high'] = 25
all_stock_data['min_' + str(minute_ticker + 1)]['high'] = 36
all_stock_data['min_1']['price'] = 26.90
all_stock_data['min_4']['low'] = .05

print(all_stock_data)


df = pd.DataFrame(all_stock_data).swapaxes('index', 'columns')

print(df)
