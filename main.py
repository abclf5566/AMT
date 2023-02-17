import time
import logging

from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

logging.basicConfig(filename='output.log', level=logging.INFO)


class BinanceTrader:
    def __init__(self, api_key: str, secret_key: str, testnet: bool = True):
        self.client = Client(api_key, secret_key)
        self.testnet = testnet
        if testnet:
            self.client.API_URL = 'https://testnet.binance.vision/api'

        self.trading_symbol = 'BTCUSDT'
        self.trade_quantity = 0.001

    def start_trading(self, quantity=0.001, leverage=1, stop_loss_pct=0.05, take_profit_pct=0.1):
        """"
        自動化交易策略的核心功能
        """
        self.trade_quantity = quantity

        # 設定杠桿
        self.set_leverage(leverage)

        # 檢查是否有持倉
        position = self.check_position()
        if position:
            logging.info(f"目前持倉方向為 {position['positionSide']}")
            if position['positionSide'] == 'LONG':
                self.close_long_position(stop_loss_pct, take_profit_pct)
            else:
                self.close_short_position(stop_loss_pct, take_profit_pct)
        else:
            self.open_long_position()

        logging.info('等待5秒鐘')
        time.sleep(5)

        self.check_results()

    def check_position(self):
        """"
        檢查是否有持倉
        """
        try:
            position = self.client.futures_position_information(symbol=self.trading_symbol)
            for p in position:
                if p['symbol'] == self.trading_symbol:
                    return p
        except BinanceAPIException as e:
            logging.error(f"API Error: {e}")
            return None

    def open_long_position(self):
        """"
        開多倉位
        """
        try:
            order = self.client.futures_create_order(symbol=self.trading_symbol,
                                                     side=SIDE_BUY,
                                                     type=ORDER_TYPE_MARKET,
                                                     quantity=self.trade_quantity)
            logging.info(f"下單成功，單號：{order['orderId']}")
        except BinanceAPIException as e:
            logging.error(f"下單失敗: {e}")

    def close_long_position(self, stop_loss_pct, take_profit_pct):
        """"
        平多倉位
        """
        position = self.check_position()

        if position is None or position['positionAmt'] == '0':
            logging.warning('目前無多頭持倉')
            return

        # 計算保證金
        notional = float(position['entryPrice']) * float(position['positionAmt'])
        if notional < 10:
            logging.warning(f'保證金不足，當前為{notional} USDT')
            return

        # 計算止損價格
        stop_loss_price = float(position['entryPrice']) * (1 - stop_loss_pct)
        logging.info(f'設置止
