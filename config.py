import os
from dotenv import load_dotenv

load_dotenv()

# Binance API密鑰
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')

# 交易對、策略參數等
SYMBOL = 'BTCUSDT'
TRADE_TYPE = 'SPOT'  # 'SPOT', 'MARGIN_LONG', 'MARGIN_SHORT'
ORDER_QUANTITY = 0.001  # 下單數量
MIN_ORDER_VALUE = 10  # 最小下單價值，用於交易量控制
LEVERAGE_LIMIT = 5  # 槓桿倍率上限
TRADING_LIMIT = 0.5  # 資金使用比例上限
RISK_LIMIT = 0.02  # 單次交易風險限制


# Strategy parameters
ART_FAST_PERIOD = 5
ART_SLOW_PERIOD = 20
ART_THRESHOLD = 0.5
TRADE_SIZE_PERCENT = 0.5
STOP_LOSS_THRESHOLD = 0.02
TAKE_PROFIT_THRESHOLD = 0.05
