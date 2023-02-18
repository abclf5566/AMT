import backtrader as bt
import datetime
import pandas as pd
import os
import config
from api_client import BinanceApiClient


class Strategy(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        pass


class BinanceData(bt.feeds.PandasData):
    lines = ('open', 'high', 'low', 'close', 'volume', 'quote_volume')
    params = (
        ('nocase', True),
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('quote_volume', 'quote_volume'),
    )


class BinanceBacktest:
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.api_client = BinanceApiClient(config.API_KEY, config.API_SECRET)

    def run(self):
        # 獲取歷史K線數據
        klines = self.api_client.get_historical_klines(self.symbol, Client.KLINE_INTERVAL_4HOUR, self.start_date, self.end_date)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')

        # 轉換為Backtrader的Data Feed
        data = BinanceData(dataname=df)
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.addstrategy(Strategy)

        # 回測
        cerebro.run()

        # 獲取回測結果
        return cerebro.broker.get_value()

if __name__ == '__main__':
    backtest = BinanceBacktest(config.SYMBOL, datetime.datetime(2022, 1, 1), datetime.datetime(2022, 2, 1))
    result = backtest.run()
    print(result)
