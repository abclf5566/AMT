from binance.client import Client
from binance.enums import *
import config


class BinanceApiClient:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
    
    def get_orderbook_ticker(self, symbol):
        res = self.client.get_orderbook_ticker(symbol=symbol)
        return res

    def get_account_info(self):
        res = self.client.get_account()
        return res

    def get_klines(self, symbol, interval, limit):
        res = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return res

    def create_order(self, symbol, side, quantity, order_type, price=None, stop_price=None):
        params = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'type': order_type
        }
        if price is not None:
            params['price'] = price
        if stop_price is not None:
            params['stopPrice'] = stop_price

        res = self.client.create_order(**params)
        return res

    def cancel_order(self, symbol, order_id):
        res = self.client.cancel_order(symbol=symbol, orderId=order_id)
        return res

    def get_open_orders(self, symbol):
        res = self.client.get_open_orders(symbol=symbol)
        return res

    def get_all_orders(self, symbol):
        res = self.client.get_all_orders(symbol=symbol)
        return res

    def get_order_status(self, symbol, order_id):
        res = self.client.get_order(symbol=symbol, orderId=order_id)
        return res

    def get_order_trades(self, symbol, order_id):
        res = self.client.get_my_trades(symbol=symbol, orderId=order_id)
        return res

    def get_deposit_history(self, coin):
        res = self.client.get_deposit_history(coin=coin)
        return res

    def get_withdraw_history(self, coin):
        res = self.client.get_withdraw_history(coin=coin)
        return res
"""
__init__方法：初始化BinanceApiClient對象，使用Binance API密鑰進行身份驗證，並初始化Binance API客戶端；
get_orderbook_ticker方法：獲取指定交易對的市場深度和最新價格等信息；
get_account_info方法：獲取帳戶信息，包括可用資金、持倉、凍結資金等；
get_klines方法：獲取指定交易對的K線數據，包括開高低收價、成交量等；
create_order方法：創建新訂單，包括市價單、限價單、止損單等。
"""