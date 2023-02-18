import pandas as pd
import matplotlib.pyplot as plt
import config
from binance.client import Client

# 引入 position.py 文件
from position import PositionManager


# 使用Binance API獲取最近4小時的K線數據
client = Client(config.API_KEY, config.API_SECRET)
klines = client.futures_historical_klines(config.SYMBOL, Client.KLINE_INTERVAL_1HOUR, '4 hours ago UTC')
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df = df.astype(float)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df = df.set_index('timestamp')

# 定義交易策略和資金管理
def strategy(df, short_period=10, long_period=20):
    # 計算短期和長期移動平均線
    df['ma_short'] = df['close'].rolling(short_period).mean()
    df['ma_long'] = df['close'].rolling(long_period).mean()

    # 生成交易信號
    df['signal'] = 0
    df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1
    df.loc[df['ma_short'] < df['ma_long'], 'signal'] = -1

    # 計算持倉
    df['position'] = df['signal'].diff()
    df['position'].fillna(method='ffill', inplace=True)
    df['position'].fillna(0, inplace=True)

    # 計算收益和累計收益
    df['returns'] = df['close'].pct_change() * df['position'].shift(1)
    df['cumulative_returns'] = (1 + df['returns']).cumprod()

    # 計算最大回撤
    df['drawdown'] = df['cumulative_returns'].cummax() - df['cumulative_returns']
    df['max_drawdown'] = df['drawdown'].cummax()

strategy(df)

# 初始化持倉
position_manager = PositionManager()

# 記錄賬戶價值變化
values = []

# 回測每個時間點的收益
for i, row in df.iterrows():
    # 更新資金和倉位信息
    position_manager.update_position()
    position_manager.current_price = row['close']
    
    # 如果當前有持倉，則根據持倉方向計算收益
    if position_manager.position != 0:
        if position_manager.position == 1:
            profit = (row['close'] - position_manager.entry_price) / position_manager.entry_price
        elif position_manager.position == -1:
            profit = (position_manager.entry_price - row['close']) / position_manager.entry_price

        # 如果出現止損或止盈，則平倉
        if position_manager.check_stop_loss(row['close']) or position_manager.check_take_profit(row['close']):
            position_manager.close_position(side=position_manager.current_side, price=row['close'])
            print(f"Close position at {row.name}, price {row['close']}, profit {profit:.2%}")
        else:
            position_manager.update_stop_loss(row['low'])

    # 如果當前沒有持倉，則考慮是否進行開倉
    else:
        if row['position'] == 1:
            position_manager.open_position(side='BUY', price=row['close'], quantity=config.ORDER_QUANTITY)
            print(f"Open long position at {row.name}, price {row['close']}")
        elif row['position'] == -1:
            position_manager.open_position(side='SELL', price=row['close'], quantity=config.ORDER_QUANTITY)
            print(f"Open short position at {row.name}, price {row['close']}")

    # 記錄賬戶價值
    account_info = position_manager.account_info
    equity = float(account_info['totalWalletBalance'])
    margin = float(account_info['totalMaintMargin'])
    values.append(equity - margin)

# 繪製資金變化圖表
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(15, 8))
ax[0].plot(df.index, values)
ax[0].set_ylabel('Portfolio Value')
ax[1].plot(df.index, df['max_drawdown'])
ax[1].set_ylabel('Max Drawdown')
ax[1].set_xlabel('Date')
plt.show()

# 計算回測結果
start_value = 10000
end_value = values[-1]
total_return = end_value / start_value - 1
max_drawdown = df['max_drawdown'].max()

print(f"Start value: {start_value:.2f}")
print(f"End value: {end_value:.2f}")
print(f"Total return: {total_return:.2%}")
print(f"Max drawdown: {max_drawdown:.2%}")
