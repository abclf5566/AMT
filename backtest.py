import backtrader as bt
import pandas as pd
from datetime import datetime
from quant_strategy import QuantStrategy

# 載入歷史數據
df = pd.read_csv('BTCUSDT-1m.csv')
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('datetime', inplace=True)

# 創建 Cerebro 引擎
cerebro = bt.Cerebro()

# 添加資料
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# 添加策略
cerebro.addstrategy(QuantStrategy)

# 設置初始資金和手續費率
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.0004)

# 設置回測期間
start_date = datetime(2021, 1, 1)
end_date = datetime(2021, 2, 1)
cerebro.adddata(data.loc[start_date:end_date])

# 開始回測
cerebro.run()
cerebro.plot()
