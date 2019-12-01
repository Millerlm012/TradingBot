# GOAL = bot trades when 3 bar play is found and taking place

import requests, json
import time
from config import *

BASE_URL = ENDPOINT
ACCOUNT_URL = '{}/v2/account'.format(BASE_URL)
ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}


def get_account():
    r = requests.get(ACCOUNT_URL, HEADERS)

    return json.loads(r.content)


# setting response_get_account to equal the function get_account
response_get_account = get_account()
print(response_get_account)


def create_order(symbol, qty, side, type, limit_in_force, limit_price, stop_price, extended_hours, client_orders_id):
    data = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': type,
        'limit_in_force': limit_in_force,
        'limit_price': limit_price,
        'stop_price': stop_price,
        'extended_hours': extended_hours,
        'client_orders_id': client_orders_id
    }

    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)

    return json.loads(r.content)