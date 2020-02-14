# testing list of lists and pd dataframes

"""
Using pandas dataframe to reorganize the data collected throughout the day
"""
import pandas as pd

# each new list will have 3 values --> [0] = high , [1] = low , [2] = price
test = [[] for i in range(361)]
test[1].append(3)
test[1].append(4)
test[1].append(5)

print(test)

df_test = pd.DataFrame(test, columns=['high', 'low', 'price'])

print(df_test)