import talib
import pandas as pd

# 讀取歷史K線
df = pd.read_csv('btc_usdt_hourly_data.csv', index_col=0, parse_dates=True)

# 計算Normalized MACD指標
normalized_macd = talib.MACD(df['close'], fastperiod=13, signalperiod=26, slowperiod=50)[2] / talib.MACD(df['close'], fastperiod=13, signalperiod=26, slowperiod=50)[1]

# 計算5 IN 1指標
rsi_period = 21
sma_period = 55
rsi = talib.RSI(df['close'], rsi_period)
sma = talib.SMA(df['close'], sma_period)
max_high = talib.MAX(df['high'], rsi_period)
min_low = talib.MIN(df['low'], rsi_period)
stoch = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
five_in_one = (rsi / 100.0) * (sma / df['close']) * (max_high / df['close']) * (df['close'] / min_low) * (stoch[0] / 100.0)

# 計算移動平均線MA
ma = talib.SMA(df['close'], timeperiod=13)

# 計算多單信號
if normalized_macd.iloc[-1] > normalized_macd.iloc[-2] and five_in_one.iloc[-1] > five_in_one.iloc[-2] and df.iloc[-1]['close'] > ma.iloc[-1]:
    print('多單信號')

# 計算空單信號
if normalized_macd.iloc[-1] < normalized_macd.iloc[-2] and five_in_one.iloc[-1] > five_in_one.iloc[-2] and df.iloc[-1]['close'] < ma.iloc[-1]:
    print('空單信號')
