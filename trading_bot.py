import logging
import time
import threading
import pandas as pd
from datetime import datetime, timedelta

from config import *
from strategy import BinanceStrategy


class BinanceTradingBot:
    def __init__(self):
        # 設定logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(handler)

        # 創建策略實例
        self.strategy = BinanceStrategy(api_key, api_secret, symbol)

        # 設定持倉狀態
        self.position = 0  # 0表示空倉，1表示多倉

    def check_signal(self):
        """檢查交易訊號"""
        while True:
            try:
                # 取得當前持倉方向
                position_info = self.strategy.client.futures_position_information(symbol=self.strategy.symbol)
                if len(position_info) > 0:
                    if float(position_info[0]['positionAmt']) > 0:
                        self.position = 1
                    else:
                        self.position = 0
                else:
                    self.position = 0

                # 取得K線資料
                end_time = int(time.time() // 60 * 60 * 1000)
                start_time = end_time - interval * 60 * 1000 * window
                klines = self.strategy.client.futures_klines(symbol=self.strategy.symbol, interval=interval,
                                                             startTime=start_time, endTime=end_time)

                # 將K線資料轉換成DataFrame
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                                   'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                                   'taker_buy_quote_asset_volume', 'ignore'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)

                # 計算指標
                df['ma_short'] = df['close'].rolling(window=ma_short).mean()
                df['ma_long'] = df['close'].rolling(window=ma_long).mean()
                df['rsi'] = self.strategy.RSI(df['close'], rsi_window)

                # 檢查交易訊號
                if self.position == 0:
                    if df['ma_short'][-1] > df['ma_long'][-1] and df['rsi'][-1] > rsi_buy_threshold:
                        self.strategy.start_trading(quantity=order_quantity, leverage=leverage,
                                                     stop_loss_pct=stop_loss_pct, take_profit_pct=take_profit_pct)
                        self.logger.info(f"買入 {self.strategy.symbol}")
                elif self.position == 1:
                    if df['ma_short'][-1] < df['ma_long'][-1] and df['rsi'][-1] < rsi_sell_threshold:
                        self.strategy.start_trading(quantity=-order_quantity, leverage=leverage,
                                                     stop_loss_pct=stop_loss_pct, take_profit_pct=take_profit_pct)
                        self.logger.info(f"賣出 {self.strategy.symbol}")

                time.sleep(check_interval)
            except Exception as e:
                self.logger.exception(e)
                time.sleep(check_interval)

    def run(self):
        """啟動交
