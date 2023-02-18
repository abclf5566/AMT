import os
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import config
import requests
import hmac
import hashlib
import time
import json
import config


#get_klines：用於獲取歷史K線數據；
#get_account_info：用於獲取帳戶信息；
#place_order：用於下單。
#get_fee_rate：用於獲取用戶的交易手續費率；
#get_trade_fee：用於獲取交易手續費；
#get_order_cost：用於計算實際手續費。

class BinanceApiClient:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        self.bm = BinanceSocketManager(self.client)

    def get_klines(self, symbol, interval, start_time, end_time):
        klines = self.client.futures_klines(
            symbol=symbol,
            interval=interval,
            startTime=start_time,
            endTime=end_time
        )
        return klines

    def get_account_info(self):
        account_info = self.client.futures_account()
        return account_info

    def place_order(self, symbol, trade_type, order_type, quantity, price=None, params=None):
        if trade_type == 'SPOT':
            order_func = self.client.create_order
            order_params = {
                'symbol': symbol,
                'side': params['side'],
                'type': params['type'],
                'quantity': quantity
            }
            if 'price' in params:
                order_params['price'] = params['price']
            if 'stopPrice' in params:
                order_params['stopPrice'] = params['stopPrice']
            if 'timeInForce' in params:
                order_params['timeInForce'] = params['timeInForce']
        elif trade_type == 'MARGIN_LONG' or trade_type == 'MARGIN_SHORT':
            order_func = self.client.create_margin_order
            order_params = {
                'symbol': symbol,
                'side': params['side'],
                'type': params['type'],
                'quantity': quantity,
                'isIsolated': True
            }
            if 'price' in params:
                order_params['price'] = params['price']
            if 'stopPrice' in params:
                order_params['stopPrice'] = params['stopPrice']
            if 'timeInForce' in params:
                order_params['timeInForce'] = params['timeInForce']
            if trade_type == 'MARGIN_LONG':
                order_params['isBuyer'] = True
            else:
                order_params['isBuyer'] = False
        else:
            raise ValueError('Invalid trade type')

        order_result = order_func(**order_params)

        return order_result
def request(method, path, params=None, data=None, headers=None):
    url = config.API_URL + path
    ts = int(time.time() * 1000)
    headers = headers or {}
    headers['X-MBX-APIKEY'] = config.API_KEY
    if params is not None:
        params['timestamp'] = ts
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = hmac.new(config.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        query_string += f'&signature={signature}'
        url += '?' + query_string
    if data is not None:
        data = json.dumps(data)
    response = requests.request(method, url, headers=headers, params=params, data=data)
    return response


def get_fee_rate(symbol):
    params = {
        'symbol': symbol,
        'timestamp': int(time.time() * 1000),
    }
    response = request('GET', '/sapi/v1/asset/tradeFee', params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    if data is None:
        return None
    trade_fee = data.get('tradeFee', [])
    maker_fee = None
    taker_fee = None
    for fee in trade_fee:
        if fee['symbol'] == symbol:
            maker_fee = float(fee['maker'])
            taker_fee = float(fee['taker'])
            break
    if maker_fee is None or taker_fee is None:
        return None
    return maker_fee, taker_fee


def get_trade_fee(symbol, is_maker):
    fee_rate = get_fee_rate(symbol)
    if fee_rate is None:
        return None
    maker_fee_rate, taker_fee_rate = fee_rate
    if is_maker:
        fee_rate = maker_fee_rate
    else:
        fee_rate = taker_fee_rate
    return fee_rate


def get_order_cost(symbol, quantity, price, is_maker=False):
    fee_rate = get_trade_fee(symbol, is_maker)
    if fee_rate is None:
        return None
    cost = quantity * price
    fee = cost * fee_rate
    return fee