from binance.client import Client
from binance.enums import *
import config


class BinanceApiClient:
    def __init__(self):
        self.positions = []

    def __init__(self, api_key, api_secret):
    #   self.client = Client(api_key, api_secret)
        self.client = Client("qv4gLXSIxA6h4bBqGCEHwQl4JddurxuhVy5w7MEP7H2NJgUgN9Apa2ZFc5lLjmBD", "1pInbB0eydGfIEu3otJggKnShibfRtbvclLYphm7jEw7HVtwtps5CojJEyshFfS7")
    
    def get_orderbook_ticker(self, symbol):
        res = self.client.get_orderbook_ticker(symbol=symbol)
        return res

    def get_account_info(self):
        res = self.client.get_account()
        return res

    def get_klines(self, symbol, interval, start_time, end_time):
        klines = self.client.futures_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_time.strftime("%d %b %Y %H:%M:%S"),
            end_str=end_time.strftime("%d %b %Y %H:%M:%S"),
            limit=1000
        )
        return klines

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

    def get_spot_position(self, symbol):
        position = self.client.futures_position_information(symbol=symbol)
        for p in position:
            if p['symbol'] == symbol:
                return p
        return None

    def get_spot_account_info(self):
        return self.client.get_account()

    def open_position(self, timestamp, price, direction):
        self.position = Position()
        self.position.open(timestamp, price, direction)

    def close_position(self, timestamp, price):
        self.position.close(timestamp, price)
        self.position = None

    def update_stop_loss(self, low):
        if self.position is not None:
            self.position.update_stop_loss(low)

    def check_stop_loss(self, price):
        if self.position is not None:
            return self.position.check_stop_loss(price)
        else:
            return False

    def check_take_profit(self, price):
        if self.position is not None:
            return self.position.check_take_profit(price)
        else:
            return False
"""
__init__方法：初始化BinanceApiClient對象，使用Binance API密鑰進行身份驗證，並初始化Binance API客戶端；
get_orderbook_ticker方法：獲取指定交易對的市場深度和最新價格等信息；
get_account_info方法：獲取帳戶信息，包括可用資金、持倉、凍結資金等；
get_klines方法：獲取指定交易對的K線數據，包括開高低收價、成交量等；
create_order方法：創建新訂單，包括市價單、限價單、止損單等。
"""