import math
from decimal import Decimal, ROUND_HALF_DOWN
from api_client import BinanceApiClient
import config


class PositionManager:
    def __init__(self):
        self.api_client = BinanceApiClient(config.API_KEY, config.API_SECRET)
        self.symbol = config.SYMBOL
        self.trade_type = config.TRADE_TYPE
        self.order_quantity = config.ORDER_QUANTITY
        self.min_order_value = config.MIN_ORDER_VALUE
        self.leverage_limit = config.LEVERAGE_LIMIT
        self.trading_limit = config.TRADING_LIMIT
        self.risk_limit = config.RISK_LIMIT
        self.position = None
        self.account_info = None
        self.current_price = None

    def update_position(self):
        if self.trade_type == 'SPOT':
            self.position = self.api_client.get_spot_position(self.symbol)
            self.account_info = self.api_client.get_spot_account_info()
        else:
            raise ValueError('Unsupported trade type')

    def open_position(self, side, quantity, price=None):
        if self.trade_type == 'SPOT':
            if price is None:
                # 市價單
                order = self.api_client.create_spot_order(
                    symbol=self.symbol,
                    side=side,
                    quantity=quantity,
                    order_type=ORDER_TYPE_MARKET
                )
            else:
                # 限價單
                order = self.api_client.create_spot_order(
                    symbol=self.symbol,
                    side=side,
                    quantity=quantity,
                    order_type=ORDER_TYPE_LIMIT,
                    price=price
                )
        else:
            raise ValueError('Unsupported trade type')
        return order

    def close_position(self, side, quantity=None, price=None):
        if self.trade_type == 'SPOT':
            if quantity is None:
                # 全部平倉
                quantity = self.position['positionAmt']
            if price is None:
                # 市價單
                order = self.api_client.create_spot_order(
                    symbol=self.symbol,
                    side=side,
                    quantity=abs(float(quantity)),
                    order_type=ORDER_TYPE_MARKET
                )
            else:
                # 限價單
                order = self.api_client.create_spot_order(
                    symbol=self.symbol,
                    side=side,
                    quantity=abs(float(quantity)),
                    order_type=ORDER_TYPE_LIMIT,
                    price=price
                )
        else:
            raise ValueError('Unsupported trade type')
        return order
class StopLossManager:
    def __init__(self):
        self.position_manager = PositionManager()
        self.symbol = config.SYMBOL
        self.stop_loss_threshold = None
        self.trailing_stop_loss = False

    def set_stop_loss(self, stop_loss_threshold, trailing_stop_loss=False):
        self.stop_loss_threshold = stop_loss_threshold
        self.trailing_stop_loss = trailing_stop_loss

    def update_stop_loss(self):
        current_price = self.position_manager.current_price
        position_size = self.position_manager.position['positionAmt']
        side = 'SELL' if float(position_size) > 0 else 'BUY'
        if self.trailing_stop_loss:
            stop_price = self._calculate_trailing_stop_price(side, current_price)
        else:
            stop_price = self._calculate_stop_price(side, current_price)
        self.position_manager.set_stop_loss(stop_price, side)

    def _calculate_stop_price(self, side, current_price):
        if side == 'SELL':
            stop_price = current_price * (1 - self.stop_loss_threshold)
        else:
            stop_price = current_price * (1 + self.stop_loss_threshold)
        stop_price = self._round_price(stop_price)
        return stop_price

    def _calculate_trailing_stop_price(self, side, current_price):
        # TODO: Implement trailing stop loss strategy
        raise NotImplementedError

    def _round_price(self, price):
        decimal_places = self._get_decimal_places()
        rounded_price = Decimal(str(price)).quantize(
            Decimal('.' + '0' * decimal_places), rounding=ROUND_HALF_DOWN)
        return float(rounded_price)

    def _get_decimal_places(self):
        min_notional = self.position_manager.api_client.get_symbol_info(self.symbol)['filters'][3]['minNotional']
        decimal_places = abs(int(math.log10(float(min_notional))))
        return decimal_places
