import pandas as pd
import talib
import numpy as np
import matplotlib.pyplot as plt



# 设置交易对和参数
symbol = 'BTC/USDT'
balance = 40
position = 0
last_signal = None
leverage = 1
stop_loss = 0.03
trailing_stop_loss = 0.02
stop_profit = 0.05
trailing_stop_loss_factor = 0.02
initial_price = 0
# 定义和初始化变量
last_sell_price = 0
last_buy_price = 0
stop_profit_price = 0
trailing_stop_loss_price = 0

# 读取历史K线数据
df = pd.read_csv('BTCUSDT_1h_1613995871357_1677067871357.csv', index_col=0, parse_dates=True)

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
            margin = position / leverage
            balance -= margin
            last_signal = 'buy'
            print(f'Buy at {price:.4f} Amount: {abs(amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f} Stop price: {stop_price:.4f}')
        else:
            # 如果上一次交易信号也是买入，就增加仓位
            price = df['close'].iloc[i]
            last_price = df['close'].iloc[i - 1]
            current_profit = (price - last_price) / last_price
            max_add_amount = (balance * leverage * current_profit * 0.5) / price
            if max_add_amount > balance:
                max_add_amount = balance
            add_amount = max_add_amount - abs(position)
            if add_amount > 0:
                margin = add_amount / leverage
                balance -= margin
                position += add_amount
                # 计算新的止损价和移动止损价
                stop_price = (position * stop_loss + add_amount * (1 - stop_loss)) / position
                if last_sell_price is not None:
                    trailing_stop_loss_price = min(last_sell_price * (1 + trailing_stop_loss_factor), stop_price)
                else:
                    trailing_stop_loss_price = 0.0
                print(f'Increase position at {price:.4f} Amount: {abs(add_amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f} Stop price: {stop_price:.4f} Trailing stop loss price: {trailing_stop_loss_price}')

            # 检查是否需要触发止损单
            if stop_price is not None and df['low'].iloc[i] <= stop_price:
                margin = position / leverage
                amount = position
                balance += margin
                balance += abs(amount) * stop_price
                position = 0
                last_signal = 'sell'
                print(f'Sell at stop loss {stop_price:.4f} Amount: {abs(amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f}')


            # 判断是否需要触发移动止损单
            if last_buy_price > 0:
                trailing_stop_loss_price = max(last_buy_price * (1 - trailing_stop_loss_factor), stop_price)
                if trailing_stop_loss_price is not None and df['low'].iloc[i] <= trailing_stop_loss_price:
                    margin = position / leverage
                    amount = position
                    balance += margin
                    balance += abs(amount) * trailing_stop_loss_price
                    position = 0
                    last_signal = 'sell'
                    print(f'Sell at trailing stop loss {trailing_stop_loss_price:.4f} Amount: {abs(amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f}')
                    # 重置止损价
                    stop_price = None
                    trailing_stop_loss_price = None
            elif last_buy_price is None:
                trailing_stop_loss_price = None



    elif signal == 'sell':
        if last_signal != 'sell':
            price = df['close'].iloc[i]
            amount = (balance * leverage) / price
            stop_price = price * (1 + trailing_stop_loss)
            if amount > balance:
                amount = balance
            position -= amount
            margin = position / leverage
            balance -= margin
            last_signal = 'sell'
            print(f'Sell at {price:.4f} Amount: {abs(amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f} Stop price: {stop_price:.4f}')
        else:
            # 如果上一次交易信号也是卖出，就增加仓位
            price = df['close'].iloc[i]
            last_price = df['close'].iloc[i - 1]
            current_profit = (last_price - price) / last_price
            max_add_amount = (balance * leverage * current_profit * 0.5) / price
            if max_add_amount > balance:
                max_add_amount = balance
            add_amount = max_add_amount - abs(position)

            if add_amount > 0:
                margin = add_amount / leverage
                balance -= margin
                position -= add_amount
                # 计算新的止损价和移动止损价
                stop_price = (position * stop_loss + add_amount * (1 - stop_loss)) / position
                if last_sell_price is not None:
                    trailing_stop_loss_price = min(last_sell_price * (1 + trailing_stop_loss_factor), stop_price)
                else:
                    trailing_stop_loss_price = 0
                print(f'Increase position at {price:.4f} Amount: {abs(add_amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f} Stop price: {stop_price:.4f} Trailing stop loss price: {trailing_stop_loss_price}')




            # 检查是否需要触发止损单
            if stop_price is not None and df['high'].iloc[i] >= stop_price:
                margin = abs(position) / leverage
                amount = abs(position)
                balance += margin
                balance += abs(amount) * stop_price
                position = 0
                last_signal = 'buy'
                print(f'Buy at stop loss {stop_price:.4f} Amount: {abs(amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f}')

            # 判断是否需要触发移动止损单
            if last_sell_price > 0:
                if last_sell_price is not None and stop_price is not None:
                    trailing_stop_loss_price = min(last_sell_price * (1 + trailing_stop_loss_factor), stop_price)
                else:
                    trailing_stop_loss_price = None

                if df['high'].iloc[i] >= trailing_stop_loss_price:
                    margin = abs(position) / leverage
                    amount = abs(position)
                    balance += margin
                    balance += abs(amount) * trailing_stop_loss_price
                    position = 0
                    last_signal = 'buy'
                    print(f'Buy at trailing stop loss {trailing_stop_loss_price:.4f} Amount: {abs(amount):.4f} Balance: {balance:.4f} Position: {abs(position):.4f}')
                    # 重置止损价
                    stop_price = None
                    trailing_stop_loss_price = None
            elif last_sell_price is None:
                trailing_stop_loss_price = None

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