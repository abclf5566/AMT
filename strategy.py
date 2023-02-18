from typing import List, Tuple
from decimal import Decimal
from enum import Enum
from binance.enums import *
from api_client import APIClient
from position import Position, PositionType
from config import trading_pairs, risk_ratio, aggressive_ratio, conservative_ratio, \
    art_indicator_window, trading_amount, max_total_amount, api_key, api_secret


class TradingStrategy(Enum):
    AGGRESSIVE = 1
    CONSERVATIVE = 2


class ArtIndicator:
    def __init__(self, window: int):
        self.window = window
        self.prices = []

    def add_price(self, price: Decimal):
        self.prices.append(price)
        if len(self.prices) > self.window:
            self.prices.pop(0)

    def get_value(self) -> Tuple[Decimal, Decimal]:
        if len(self.prices) == self.window:
            ema = sum(self.prices) / self.window
            deviation = (sum([abs(p - ema) for p in self.prices]) / self.window).quantize(Decimal('.0001'))
            return ema, deviation
        return None, None


class TradingStrategyModule:
    def __init__(self, trading_strategy: TradingStrategy, api_key: str, api_secret: str):
        self.trading_strategy = trading_strategy
        self.api_client = APIClient(api_key, api_secret)
        self.art_indicator = ArtIndicator(art_indicator_window)
        self.positions = {symbol: Position(symbol) for symbol in trading_pairs}
        self.risk_ratio = risk_ratio
        self.aggressive_ratio = aggressive_ratio
        self.conservative_ratio = conservative_ratio
        self.trading_amount = trading_amount
        self.max_total_amount = max_total_amount

    def start(self):
        self.api_client.start()

    def stop(self):
        self.api_client.stop()

    def on_depth(self, symbol: str, depth: dict):
        # 更新 Art indicator
        bids = [Decimal(price) for price, _ in depth['bids']]
        asks = [Decimal(price) for price, _ in depth['asks']]
        prices = sorted(bids + asks)
        mid_price = prices[len(prices) // 2]
        self.art_indicator.add_price(mid_price)

        # 获取当前的交易量
        available_quantity = self.positions[symbol].get_available_quantity()
        total_quantity = self.positions[symbol].quantity
        if self.trading_strategy == TradingStrategy.AGGRESSIVE:
            target_quantity = Decimal(self.aggressive_ratio * self.trading_amount / mid_price).quantize(Decimal('.0001'))
        else:
            target_quantity = Decimal(self.conservative_ratio * self.trading_amount / mid_price).quantize(Decimal('.0001'))

        # 判断是否需要进行交易
        if available_quantity == 0 and total_quantity == 0:
            if target_quantity > 0:
                # 开仓
                self.open_position(symbol, target_quantity, mid_price)
        elif available_quantity > 0:
            if available_quantity / total_quantity > self.risk_ratio:
                # 加仓
                self.add_position(symbol, target_quantity, mid_price)
            else:
                # 不操作
                pass
        else:
            # 平仓
            self.close_position(symbol)

    def open_position(self, symbol: str, quantity: Decimal, price: Decimal):
        """开仓"""
        api_client = self.api_client
        response = api_client.request('POST', '/api/v3/order', params={
            'symbol': symbol,
            'side': self.position_type.value,
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': str(price),
            'newOrderRespType': 'FULL',
            'timestamp': int(time.time() * 1000),
        })
        if response.status_code == 200:
            self.update_position(api_client)
            logger.info(f'{self.position_type.name} position opened: {response.json()}')
            return True
        else:
            logger.error(f'Failed to open {self.position_type.name} position: {response.json()}')
            return False
