import talib
import pandas as pd
import matplotlib.pyplot as plt

# 讀取歷史K線
df = pd.read_csv('btc_usdt_hourly_data.csv', index_col=0, parse_dates=True)

# 計算Normalized MACD指標
fast_ma = 13
macd, signal, hist = talib.MACD(df['close'], fastperiod=fast_ma, signalperiod=26, slowperiod=50)
normalized_macd = (macd - signal) / signal

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
ma_period = 13
ma = talib.SMA(df['close'], ma_period)

# 繪製Normalized MACD指標
plt.subplot(3, 1, 1)
plt.plot(df.index, normalized_macd, label='Normalized MACD')
plt.legend()

# 繪製5 IN 1指標
plt.subplot(3, 1, 2)
plt.plot(df.index, five_in_one, label='5 IN 1')
plt.legend()

# 繪製移動平均線MA
plt.subplot(3, 1, 3)
plt.plot(df.index, df['close'], label='Price')
plt.plot(df.index, ma, label='MA')
plt.legend()

plt.show()
