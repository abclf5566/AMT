import logging
import pandas as pd

from datetime import datetime, timedelta
from binance.client import Client
from binance.enums import *

class BinanceStrategy:
    def __init__(self, api_key, api_secret, symbol):
        self.client = Client(api_key, api_secret)
        self.symbol = symbol
        
        # 設定logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(handler)

        # 設定交易品種的最小下單數量、價格精度
        self.symbol_info = self.client.get_symbol_info(self.symbol)
        self.min_notional = float(self.symbol_info['filters'][2]['minNotional'])
        self.qty_precision = int(self.symbol_info['quantityPrecision'])
        self.price_precision = int(self.symbol_info['pricePrecision'])
        
        self.balance = 0.0
        self.asset_balance = 0.0
        self.usdt_balance = 0.0
        self.btc_balance = 0.0
        self.btc_price = 0.0
        
    def get_asset_balance(self):
        """取得交易品種和USDT的餘額"""
        account_info = self.client.get_account()
        balances = account_info['balances']
        
        for balance in balances:
            if balance['asset'] == self.symbol[:-4]:
                self.asset_balance = float(balance['free']) + float(balance['locked'])
            elif balance['asset'] == 'USDT':
                self.usdt_balance = float(balance['free']) + float(balance['locked'])
                
        self.logger.info(f"{self.symbol[:-4]}: {self.asset_balance}")
        self.logger.info(f"USDT: {self.usdt_balance}")
        
    def get_btc_balance(self):
        """取得BTC的餘額"""
        ticker = self.client.get_ticker(symbol='BTCUSDT')
        self.btc_price = float(ticker['lastPrice'])
        self.btc_balance = self.usdt_balance / self.btc_price
        
        self.logger.info(f"BTC: {self.btc_balance:.8f}")
        
    def start_trading(self, quantity=0.01, leverage=1, stop_loss_pct=0.05, take_profit_pct=0.1):
        """啟動交易機器人"""
        self.logger.info(f"開始交易: {self.symbol}, 數量: {quantity}")
        
        while True:
            # 取得當前價格
            ticker = self.client.get_ticker(symbol=self.symbol)
            price = float(ticker['lastPrice'])

            # 計算下單數量
            if self.asset_balance * price >= self.min_notional:
                order_quantity = round(quantity / price, self.qty_precision)
            else:
                order_quantity = 0.0
            
            # 設定交易參數
            if order_quantity > 0:
                self.client.futures_change_leverage(symbol=self.symbol, leverage=leverage)
                order_type = ORDER_TYPE_MARKET
                side = SIDE_BUY
                stop_loss_price = round(price * (1 - stop_loss_pct), self.price_precision)
                take_profit_price = round(price * (1 + take_profit_pct), self.price_precision)
                
                # 下單
                try:
                    order = self.client.futures_create_order(
                        symbol=self.symbol,
                        side=side,
                        type=order_type,
                        quantity=order_quantity,
                        reduceOnly=False,
                        price=None,
                        newClientOrderId=None,
                        stopPrice=stop_loss_price,
                        workingType=None,
                        activationPrice=None,
                        callbackRate=None,
                        closePosition=False,
                        priceProtect=False
                    )

                    self.logger.info(f"下單成功: {order}")
                    self.balance = self.asset_balance * price
                except Exception as e:
                    self.logger.error(f"下單失敗: {e}")
                    self.balance = 0.0

            # 更新餘額
            self.get_asset_balance()
            self.get_btc_balance()

            # 計算報酬率
            pnl = self.balance - (self.asset_balance * price)
            returns = pnl / self.balance if self.balance > 0 else 0.0
            self.logger.info(f"報酬率: {returns:.2%}")

            # 判斷是否觸發止損或止盈
            if price <= stop_loss_price:
                self.logger.info("止損觸發")
                break
            elif price >= take_profit_price:
                self.logger.info("止盈觸發")
                break

            # 等待1秒
            self.logger.info("等待1秒")
            time.sleep(1)