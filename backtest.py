import pandas as pd
import matplotlib.pyplot as plt
import config
from binance.client import Client

# 使用Binance API獲取最近4小時的K線數據
client = Client(config.API_KEY, config.API_SECRET)
klines = client.futures_historical_klines(config.SYMBOL, Client.KLINE_INTERVAL_1HOUR, '4 hours ago UTC')
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df = df.astype(float)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df = df.set_index('timestamp')

# 定義交易策略和資金管理
def strategy(df):
    df['signal'] = (df['close'] > df['close'].shift(1)).astype(int)
    df['position'] = df['signal'].diff()
    df['position'].fillna(method='ffill', inplace=True)
    df['position'].fillna(0, inplace=True)
    df['returns'] = df['close'].pct_change() * df['position'].shift(1)
    df['cumulative_returns'] = (1 + df['returns']).cumprod()
    df['drawdown'] = df['cumulative_returns'].cummax() - df['cumulative_returns']
    df['max_drawdown'] = df['drawdown'].cummax()

strategy(df)

# 繪製資金變化圖表
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(15, 8))
ax[0].plot(df.index, df['cumulative_returns'])
ax[0].set_ylabel('Cumulative Returns')
ax[1].plot(df.index, df['max_drawdown'])
ax[1].set_ylabel('Max Drawdown')
ax[1].set_xlabel('Date')
plt.show()

# 計算回測結果
start_value = 10000
end_value = start_value * df['cumulative_returns'][-1]
total_return = end_value / start_value - 1
max_drawdown = df['max_drawdown'].max()

print(f"Start value: {start_value:.2f}")
print(f"End value: {end_value:.2f}")
print(f"Total return: {total_return:.2%}")
print(f"Max drawdown: {max_drawdown:.2%}")
