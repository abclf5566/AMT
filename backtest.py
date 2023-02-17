import backtrader as bt
from strategy import MyStrategy

# 設定回測參數
start_cash = 10000.0  # 回測初始資金
commission = 0.001  # 手續費
fromdate = bt.date2num(datetime.datetime(2022, 2, 9))  # 回測起始日期
todate = bt.date2num(datetime.datetime(2023, 2, 9))  # 回測結束日期

# 創建回測引擎
cerebro = bt.Cerebro()

# 加入資料源
data = bt.feeds.GenericCSVData(
    dataname='data/BTC-USDT.csv',
    fromdate=fromdate,
    todate=todate,
    nullvalue=0.0,
    dtformat=('%Y-%m-%d %H:%M:%S'),
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1
)
cerebro.adddata(data)

# 設定初始資金
cerebro.broker.setcash(start_cash)

# 設定手續費
cerebro.broker.setcommission(commission=commission)

# 加入策略
cerebro.addstrategy(MyStrategy)

# 開始回測
cerebro.run()

# 印出回測結果
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
