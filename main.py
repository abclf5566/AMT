import ccxt
import talib

# 設定交易所和貨幣對
exchange = ccxt.binance()
symbol = 'BTC/USDT'

# 設定指標和參數
sma_period = 20
lma_period = 50
lux_period = 14
oversold_level = 20
overbought_level = 80

# 獲取歷史K線數據
history = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=100)

# 轉換K線數據為DataFrame格式
df = pd.DataFrame(history, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# 計算移動平均線和Smart Money Concepts指標
df['sma'] = talib.SMA(df['close'][:-1], sma_period)
df['lma'] = talib.SMA(df['close'][:-1], lma_period)
df['lux'] = talib.EMA(df['volume'][:-1] * (df['close'][:-1] - df['low'][:-1] - df['high'][:-1] + df['open'][:-1]) / (df['high'][:-1] - df['low'][:-1]), lux_period)

# 確定交易信號
if df['sma'].iloc[-1] > df['lma'].iloc[-1] and df['lux'].iloc[-1] < oversold_level:
    # 買入貨幣
    amount = 0.01 # 買入數量
    price = exchange.fetch_ticker(symbol)['bid'] # 獲取買一價格
    order = exchange.create_market_buy_order(symbol, amount, params={'quoteOrderQty': amount * price})
    print(order)
elif df['sma'].iloc[-1] < df['lma'].iloc[-1] and df['lux'].iloc[-1] > overbought_level:
    # 賣出貨幣
    amount = 0.01 # 賣出數量
    price = exchange.fetch_ticker(symbol)['ask'] # 獲取賣一價格
    order = exchange.create_market_sell_order(symbol, amount)
    print(order)
else:
    # 未發出交易信號
    print('No trade signal')