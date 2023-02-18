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

class Config:
    # 请将下面的参数设置为您自己的值
    API_KEY = 'your_api_key'
    API_SECRET = 'your_api_secret'
    SYMBOL = 'BTCUSDT'
    STRATEGY_PARAMS = {
        'leverage': 1,
        'risk_level': 0.01,
        'initial_balance': 1000,
        'art_period': 10,
        'atr_period': 10,
        'atr_multiplier': 1,
        'take_profit': 0.02,
        'stop_loss': 0.01,
        'trailing_stop': 0.005,
        'max_volume': 0.1,
        'max_position_size': 0.3,
        'min_notional': 10
    }
