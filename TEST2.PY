import pandas as pd
import talib
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
df = pd.read_csv('btc_usdt_hourly_data.csv', index_col=0, parse_dates=True)

# 计算Normalized MACD指标
normalized_macd = talib.MACD(df['close'], fastperiod=13, signalperiod=26, slowperiod=50)[2] / talib.MACD(df['close'], fastperiod=13, signalperiod=26, slowperiod=50)[1]

# 计算5 IN 1指标
rsi_period = 21
sma_period = 55
rsi = talib.RSI(df['close'], rsi_period)
sma = talib.SMA(df['close'], sma_period)
max_high = talib.MAX(df['high'], rsi_period)
min_low = talib.MIN(df['low'], rsi_period)
stoch = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
five_in_one = (rsi / 100.0) * (sma / df['close']) * (max_high / df['close']) * (df['close'] / min_low) * (stoch[0] / 100.0)
df['5_in_1'] = five_in_one

# 计算移动平均线MA
ma_period = 13
ma = talib.SMA(df['close'], timeperiod=ma_period)
df['ma'] = ma

for i in range(max(sma_period, lma_period, rsi_period) + 1, len(df)):
    # Normalized MACD指標、5 IN 1指標、RSI和移動平均線MA
    rsi = df['5_in_1'][i]
    close = df['close'][i]
    ma = df['ma'][i]
    macd = normalized_macd[i]
    macd_prev = normalized_macd[i-1]

    # 生成交易信号
    if macd_prev > macd and rsi > 1/1.85 and close < ma:
        signal = 'sell'
        price = df['close'][i]
        last_sell_price = price
    elif macd_prev < macd and rsi > 1/1.85 and close > ma:
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

            # 如果价格涨幅超过了设定的止盈阈值，就设置动态止盈价
            if price / last_buy_price - 1 >= stop_profit:
                stop_profit_price = price * (1 - trailing_stop_loss_factor)
                print('Stop profit price set to', stop_profit_price)

    if signal == 'sell':
        if last_signal != 'sell':
            price = df['close'].iloc[i]
            amount = (balance * leverage) / price
            stop_price = price * (1 + trailing_stop_loss)
            position -= amount
            balance += amount * price
            last_signal = 'sell'
            print('Sell at', price, 'Amount:', amount, 'Balance:', balance, 'Position:', position, 'Stop price:', stop_price)
        else:
            # 如果上一次交易信号也是卖出，就增加仓位
            price = df['close'].iloc[i]
            last_price = df['close'].iloc[i - 1]
            current_profit = (last_price - price) / last_price
            add_amount = (balance * leverage * current_profit * 0.5) / price
            position -= add_amount
            balance += add_amount * price
            print('Increase position at', price, 'Amount:', add_amount, 'Balance:', balance, 'Position:', position)

            # 检查是否需要触发止损单
            stop_price = price * (1 + stop_loss)
            if df['high'].iloc[i] >= stop_price:
                amount = abs(position)
                balance += amount * stop_price
                position = 0
                last_signal = 'buy'
                print('Buy at stop loss', stop_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)

            # 如果价格跌幅超过了设定的止盈阈值，就设置动态止盈价
            if last_sell_price / price - 1 >= stop_profit:
                stop_profit_price = price * (1 + trailing_stop_loss_factor)
                print('Stop profit price set to', stop_profit_price)


        # 计算动态止损价
        trailing_stop_loss_price = min(last_price * (1 + trailing_stop_loss_factor), stop_price)
        if df['high'].iloc[i] >= trailing_stop_loss_price:
            amount = abs(position)
            balance += amount * trailing_stop_loss_price
            position = 0
            last_signal = 'buy'
            print('Buy at trailing stop loss', trailing_stop_loss_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)
            # 重置止损价
            stop_price = None

        # 计算动态止损价
        trailing_stop_loss_price = max(last_price * (1 - trailing_stop_loss_factor), stop_price)
        if df['low'].iloc[i] <= trailing_stop_loss_price:
            amount = position
            balance += amount * trailing_stop_loss_price
            position = 0
            last_signal = 'buy'
            print('Sell at trailing stop loss', trailing_stop_loss_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)
            # 重置止损价
            stop_price = None



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

        # 检查是否需要触发止盈单
        if position > 0:
            stop_profit_price = last_buy_price * (1 + stop_profit)
            if df['high'].iloc[i] >= stop_profit_price:
                amount = position
                balance += amount * stop_profit_price
                position = 0
                last_signal = 'sell'
                print('Sell at stop profit', stop_profit_price, 'Amount:', amount, 'Balance:', balance, 'Position:', position)

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
