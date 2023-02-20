import pandas as pd
import talib
import matplotlib.pyplot as plt

# 设置交易对和参数
symbol = 'BTC/USDT'
sma_period = 20
lma_period = 50
lux_period = 14
oversold_level = 30
overbought_level = 70
balance = 1000
position = 0
last_signal = None
leverage = 3
stop_loss = 0.03
trailing_stop_loss = 0.02
rsi_period = 14
momentum_period = 10
stop_profit = 0.05
trailing_stop_loss_factor = 0.02


# 读取历史K线数据
df = pd.read_csv('btc_usdt_hourly_data.csv', index_col=0, parse_dates=True)



# 输出最终结果，包括结算后的余额
print('Final balance:', balance + position * df['close'].iloc[-1])
print('Final position:', position)

# 将时间设置为索引
df = pd.read_csv('btc_usdt_hourly_data.csv', parse_dates=['timestamp'])
df.set_index('timestamp', inplace=True)

# 添加资金变化的列
df['position'] = position
df['balance'] = balance

# 计算每个交易日的资产总值
df['total_assets'] = df['position'] * df['close'] + df['balance']

# 绘制资产总值变化折线图
df['total_assets'].plot()

# 显示图表
plt.show()
