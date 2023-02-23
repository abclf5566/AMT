import pandas as pd
import talib
import numpy as np


# 读取历史K线数据
df = pd.read_csv('ETHUSDT_1h_365d_klines.csv', index_col=0, parse_dates=True)

def normalized_macd(close):
    macd, signal, hist = talib.MACD(close, fastperiod=13, slowperiod=26, signalperiod=9)
    normalized_macd = (macd - np.mean(macd)) / np.std(macd)
    return normalized_macd

def five_in_one(close, rsi_period=21, sma_period=55):
    rsi = talib.RSI(close, rsi_period)
    sma = talib.SMA(close, sma_period)
    max_high = talib.MAX(df['high'], rsi_period)
    min_low = talib.MIN(df['low'], rsi_period)
    stoch = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    five_in_one = (rsi / 100.0) * (sma / df['close']) * (max_high / df['close']) * (df['close'] / min_low) * (stoch[0] / 100.0)
    return five_in_one

def ma(close, period=13):
    ma = talib.SMA(close, timeperiod=period)
    return ma

def atr_stop_loss(high, low, close, period=14, multiplier=2):
    atr = talib.ATR(high, low, close, timeperiod=period)
    atr_stop_loss = close - atr * multiplier
    return atr_stop_loss

#  # 计算Normalized MACD指标
# df['normalized_macd'] = normalized_macd(df['close'])

# # 计算5 IN 1指标
# df['five_in_one'] = five_in_one(df['close'])

# # 计算移动平均线MA
# df['ma'] = ma(df['close'])