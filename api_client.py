import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode

import requests

from config import API_KEY, SECRET_KEY

API_URL = 'https://api.binance.com'


class APIClient:
    def __init__(self):
        self.api_key = API_KEY
        self.secret_key = SECRET_KEY

    def _generate_signature(self, data):
        query_string = urlencode(data)
        signature = hmac.new(self.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def request(self, method, path, params=None):
        headers = {'X-MBX-APIKEY': self.api_key}
        query_params = {'timestamp': int(time.time() * 1000)}
        if params:
            query_params.update(params)
        query_params_string = urlencode(query_params)
        signature = self._generate_signature(query_params_string)
        query_params['signature'] = signature
        url = f'{API_URL}{path}?{urlencode(query_params)}'
        response = requests.request(method, url, headers=headers)
        response.raise_for_status()
        return json.loads(response.text)

    def get_historical_candles(self, symbol, interval, limit):
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = self.request('GET', '/api/v3/klines', params)
        return response

    def get_trade_fee(self, symbol):
        response = self.request('GET', '/sapi/v1/asset/tradeFee', params={'symbol': symbol})
        trade_fee = next(filter(lambda x: x['symbol'] == symbol, response['tradeFee']), None)
        return trade_fee

    def get_account_info(self):
        response = self.request('GET', '/api/v3/account')
        return response
