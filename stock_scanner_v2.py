import requests
from config import *
from iex import Stock

url = IEX_ENDPOINT

def get_company():
    tsla = Stock('TSLA')
    print(tsla.book())


