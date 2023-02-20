import pandas as pd
import talib
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

# 设置交易对和参数
symbol = 'BTC/USDT'
balance = 1000
position = 0
last_signal = None
leverage = 5
stop_loss = 0.03
trailing_stop_loss = 0.02
stop_profit = 0.05
trailing_stop_loss_factor = 0.02
trail_threshold = 0.01  # 移动止盈触发阈值
trail_stop_loss_factor = 0.01  # 移动止盈因子

# 读取历史K线数据
df = pd.read_csv('BTCUSDT_1h_klines_30d.csv', index_col=0, parse_dates=True)

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

# 计算Normalized MACD指标
df['normalized_macd'] = normalized_macd(df['close'])

# 计算5 IN 1指标
df['five_in_one'] = five_in_one(df['close'])

# 计算移动平均线MA
df['ma'] = ma(df['close'])

# 定义和初始化变量
last_sell_price = 0
last_buy_price = 0
stop_profit_price = 0

# 循环遍历历史数据
for i in range(1, len(df)):
    close = df['close'][i]
    macd_prev = df['normalized_macd'][i - 1]
    macd = df['normalized_macd'][i]

    # 生成交易信号
    if macd_prev < macd and df['five_in_one'][i - 1] > df['five_in_one'][i] and close < df['ma'][i]:
        signal = 'sell'
        price = df['close'][i]
        last_sell_price = price
    elif macd_prev > macd and df['five_in_one'][i - 1] < df['five_in_one'][i] and close > df['ma'][i]:
        signal = 'buy'
        price = df['close'][i]
        last_buy_price = price
    else:
        signal = None

    # 执行交易操作
    if signal == 'buy':
        if last_signal != 'buy':
            price = df['close'].iloc[i]
            amount = (balance * leverage) / price
            stop_price = price * (1 - trailing_stop_loss)
            if amount > balance:
                amount = balance
            position += amount
            balance -= amount * price
            last_signal = 'buy'
            print(f'Buy at {price:.4f} Amount: {amount:.4f} Balance: {balance:.4f} Position: {position:.4f} Stop price: {stop_price:.4f}')
        else:
            # 如果上一次交易信号也是买入，就增加仓位
            price = df['close'].iloc[i]
            last_price = df['close'].iloc[i - 1]
            current_profit = (price - last_price) / last_price
            add_amount = (balance * leverage * current_profit * 0.5) / price
            if add_amount > balance:
                add_amount = balance
            position += add_amount
            balance -= add_amount * price
            print(f'Increase position at {price:.4f} Amount: {add_amount:.4f} Balance: {balance:.4f} Position: {position:.4f}')

            # 检查是否需要触发止损单
            stop_price = price * (1 - stop_loss)
            if df['low'].iloc[i] <= stop_price:
                amount = position
                balance += amount * stop_price
                position = 0
                last_signal = 'sell'
                print(f'Sell at stop loss {stop_price:.4f} Amount: {amount:.4f} Balance: {balance:.4f} Position: {position:.4f}')
        # 判断是否需要触发移动止损单
        if last_buy_price > 0:
            trailing_stop_loss_price = max(last_buy_price * (1 - trailing_stop_loss_factor), stop_price)
            if df['low'].iloc[i] <= trailing_stop_loss_price:
                amount = position
                balance += amount * trailing_stop_loss_price
                position = 0
                last_signal = 'sell'
                print(f'Sell at trailing stop loss {trailing_stop_loss_price:.4f} Amount: {amount:.4f} Balance: {balance:.4f} Position: {position:.4f}')
                # 重置止损价
                stop_price = None

    elif signal == 'sell':
        if last_signal != 'sell':
            price = df['close'].iloc[i]
            amount = (balance * leverage) / price
            stop_price = price * (1 + trailing_stop_loss)
            if amount > abs(position):
                amount = abs(position)
            position -= amount
            balance -= amount * price
            last_signal = 'sell'
            print(f'Sell at {price:.4f} Amount: {amount:.4f} Balance: {balance:.4f} Position: {position:.4f} Stop price: {stop_price:.4f}')
        else:
            # 如果上一次交易信号也是卖出，就减少仓位
            price = df['close'].iloc[i]
            last_price = df['close'].iloc[i - 1]
            current_profit = (last_price - price) / last_price
            reduce_amount = (abs(position) * current_profit * 0.5)
            if reduce_amount > abs(position):
                reduce_amount = abs(position)
            position += reduce_amount
            balance -= reduce_amount * price
            print(f'Reduce position at {price:.4f} Amount: {reduce_amount:.4f} Balance: {balance:.4f} Position: {position:.4f}')

            # 检查是否需要触发止损单
            stop_price = price * (1 + stop_loss)
            if df['high'].iloc[i] >= stop_price:
                amount = abs(position)
                balance += amount * stop_price
                position = 0
                last_signal = 'buy'
                print(f'Buy at stop loss {stop_price:.4f} Amount: {amount:.4f} Balance: {balance:.4f} Position: {position:.4f}')
        # 判断是否需要触发移动止损单
        if last_sell_price > 0:
            trailing_stop_loss_price = min(last_sell_price * (1 + trailing_stop_loss_factor), stop_price)
            if df['high'].iloc[i] >= trailing_stop_loss_price:
                amount = abs(position)
                balance += amount * trailing_stop_loss_price
                position = 0
                last_signal = 'buy'
                print(f'Buy at trailing stop loss {trailing_stop_loss_price:.4f} Amount: {amount:.4f} Balance: {balance:.4f} Position: {position:.4f}')

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