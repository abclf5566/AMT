class Config:
    API_KEY = "YOUR_API_KEY"  # 請替換成你自己的API KEY
    SECRET_KEY = "YOUR_SECRET_KEY"  # 請替換成你自己的SECRET KEY
    SYMBOL = "BTCUSD"  # 交易的標的
    POSITION_SIZE = 0.01  # 每次下單的交易量，單位是BTC
    LEVERAGE = 1  # 下單的杠桿倍數
    STOP_LOSS_PCT = 0.05  # 止損設置的百分比
    TAKE_PROFIT_PCT = 0.1  # 止盈設置的百分比
