import numpy as np
import talib
import math
import time
import logging
from api_client import BinanceApiClient
import config

class QuantStrategy:
    def __init__(self, api_client, symbol):
        self.api_client = api_client
        self.symbol = symbol
        self.min_order_value = config.MIN_ORDER_VALUE
        self.order_quantity = config.ORDER_QUANTITY
        self.risk_limit = config.RISK_LIMIT
        self.leverage_limit = config.LEVERAGE_LIMIT
        self.trading_limit = config.TRADING_LIMIT
        self.trade_type = config.TRADE_TYPE

    def run(self):
        order_book_ticker = self.api_client.get_orderbook_ticker(self.symbol)
        klines = self.api_client.get_klines(self.symbol, '5m', 100)

        # 解析市場信息
        bids = float(order_book_ticker['bidPrice'])
        asks = float(order_book_ticker['askPrice'])
        price = (bids + asks) / 2.0

        # 使用Art技術指標預測市場走勢
        trend = self.art_indicator(klines)
        
        # 選擇交易策略
        if trend == 'up':
            self.aggressive_strategy(price)
        elif trend == 'down':
            self.conservative_strategy(price)
        else:
            logging.warning('無法識別市場趨勢')

    def aggressive_strategy(self, price):
        # 計算槓桿倍率
        leverage = self.calculate_leverage()

        # 計算下單數量
        order_quantity = self.calculate_order_quantity(price, leverage)

        # 計算實際手續費
        fee_rate = self.api_client.get_trade_fee(self.symbol, self.trade_type)['maker']
        fee = self.calculate_fee(price, order_quantity, fee_rate)

        # 計算止損和止盈阈值
        stop_loss, take_profit = self.calculate_stop_loss_take_profit(price, fee)

        # 下單
        self.create_order(price, order_quantity, stop_loss, take_profit)

    def conservative_strategy(self, price):
        # 計算下單數量
        order_quantity = self.calculate_order_quantity(price)

        # 計算實際手續費
        fee_rate = self.api_client.get_trade_fee(self.symbol, self.trade_type)['maker']
        fee = self.calculate_fee(price, order_quantity, fee_rate)

        # 計算止損和止盈阈值
        stop_loss, take_profit = self.calculate_stop_loss_take_profit(price, fee)

        # 下單
        self.create_order(price, order_quantity, stop_loss, take_profit)

    def calculate_leverage(self):
        # 計算槓桿倍率
        margin_info = self.api_client.get_margin_info()
        net_asset_value = float(margin_info['netAsset'])
        borrow_value = float(margin_info['totalAssetOfBtc'])
        equity = net_asset_value + borrow_value
        leverage = equity / net_asset_value
        leverage = min(leverage, self.leverage_limit)
        return leverage
