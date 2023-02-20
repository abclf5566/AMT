import pandas as pd
import talib
import matplotlib.pyplot as plt

# 设置交易对和参数
symbol = 'BTC/USDT'
sma_period = 20
lma_period = 50
oversold_level = 30
overbought_level = 70
balance = 10000
position = 0
last_signal = None
leverage = 3
stop_loss = 0.03
trailing_stop_loss = 0.02
rsi_period = 21
momentum_period = 10
stop_profit = 0.05
trailing_stop_loss_factor = 0.02


# 读取历史K线数据
df = pd.read_csv('AVAXUSDT_1h_klines_365d.csv', index_col=0, parse_dates=True)

# 计算移动平均线和Smart Money Concepts指标
df['sma'] = talib.SMA(df['close'], sma_period)
df['lma'] = talib.SMA(df['close'], lma_period)
df['lux'] = talib.EMA(df['volume'] * (df['close'] - df['low'] - df['high'] + df['open']) / (df['high'] - df['low']), timeperiod=14)

# 计算指标
df['ma'] = talib.SMA(df['close'], 13)
df['normalized_macd'] = talib.MACD(df['close'], fastperiod=13)[0] / df['close']
df['5_in_1'] = talib.RSI(df['close'], timeperiod=rsi_period) / talib.SMA(df['close'], timeperiod=55)

# 迭代历史K线数据，模拟交易
last_price = None
stop_price = None

for i in range(max(sma_period, lma_period, rsi_period) + 1, len(df)):
    # 获取当前的移动平均线、Smart Money Concepts指标值、RSI和Momentum指标值
    sma = df['sma'].iloc[i]
    lma = df['lma'].iloc[i]
    lux = df['lux'].iloc[i]
    rsi = df['5_in_1'].iloc[i]
    close = df['close'].iloc[i]
    ma = df['ma'].iloc[i]
    macd = df['normalized_macd'].iloc[i]
    macd_prev = df['normalized_macd'].iloc[i-1]

    # 生成交易信号
    if macd > 0 and macd_prev <= 0 and rsi > 1 and close > ma and close > sma and close > lma:
        signal = 'buy'
        price = df['close'].iloc[i]
        last_buy_price = price
    elif macd < 0 and macd_prev >= 0 and rsi < 1 and close < ma and close < sma and close < lma:
        signal = 'sell'
    else:
        signal = None

    # 执行交易操作

    if signal == 'buy':
        if last_signal != 'buy':
            price = df['close'].iloc[i]
            amount = (balance * leverage) / price
            stop_price = price * (1 - trailing_stop_loss)
            position += amount
            balance -= amount * price
            last_signal = 'buy'
            print('Buy at', price, 'Amount:', amount, 'Balance:', balance, 'Position:', position, 'Stop price:', stop_price)
        else:
            # 如果上一次交易信号也是买入，就增加仓位
            price = df['close'].iloc[i]
            last_price = df['close'].iloc[i - 1]
            current_profit = (price - last_price) / last_price
            add_amount = (balance * leverage * current_profit * 0.5) / price
            position += add_amount
            balance -= add_amount * price
            print('Increase position at', price, 'Amount:', add_amount, 'Balance:', balance, 'Position:', position)

            # 检查是否需要触发止损单
            stop_price = price * (1 - stop_loss)
            if df['low'].iloc[i] <= stop_price:
                amount = position
                balance += amount * stop_price
                position = 0
                last_signal = 'sell'
                print('Sell at stop loss', stop_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)
        #计算动态止损价
        trailing_stop_loss_price = max(last_price * (1 - trailing_stop_loss_factor), stop_price)
        if df['low'].iloc[i] <= trailing_stop_loss_price:
            amount = position
            balance += amount * trailing_stop_loss_price
            position = 0
            last_signal = 'sell'
            print('Sell at trailing stop loss', trailing_stop_loss_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)
            # 重置止损价
            stop_price = None





    elif signal == 'sell':
        if last_signal != 'sell':
            price = df['close'].iloc[i]
            amount = (balance * leverage) / price
            stop_price = price * (1 + trailing_stop_loss)
            position -= amount
            balance -= amount * price
            last_signal = 'sell'
            print('Sell at', price, 'Amount:', amount, 'Balance:', balance, 'Position:', position, 'Stop price:', stop_price)
        else:
            # 如果上一次交易信号也是卖出，就增加仓位
            price = df['close'].iloc[i]
            # 计算当前已有仓位的价值
            position_value = abs(position) * price
            # 计算可用余额，即未被用于维持保证金的资金
            available_balance = balance + position_value
            # 计算应该增加的合约数量，这里简单地将已有合约数量翻倍
            amount = abs(position) * 2
            # 检查可用余额是否足够
            if amount * price > available_balance:
                # 如果可用余额不足，就减少增仓量
                amount = available_balance // price
            # 更新仓位和余额
            position -= amount
            balance -= amount * price
            print('Increase position at', price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)
        #计算动态止损价
        trailing_stop_loss_price = max(last_price * (1 - trailing_stop_loss_factor), stop_price)
        if df['low'].iloc[i] <= trailing_stop_loss_price:
            amount = position
            balance += amount * trailing_stop_loss_price
            position = 0
            last_signal = 'sell'
            print('Sell at trailing stop loss', trailing_stop_loss_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)
            # 重置止损价
            stop_price = None

    # 更新最新价和最新信号
    last_price = df['close'].iloc[i]
    last_signal = signal




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
