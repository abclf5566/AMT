from decimal import Decimal
from typing import List

from .enums import OrderSide, OrderType, TimeInForce
from .utils import calc_trade_fee, get_next_candle_time, round_down, round_up
from .logger import logger


class Backtest:
    def __init__(self, symbol: str, interval: str, start_time: int, end_time: int, balance: Decimal,
                 fee_rate: Decimal, max_positions: int = 1):
        self.symbol = symbol
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.balance = balance
        self.fee_rate = fee_rate
        self.max_positions = max_positions

        self.current_time = start_time
        self.candles = []
        self.positions = []
        self.order_history = []

    def load_candles(self, candles: List[dict]):
        self.candles = candles

    def run(self, strategy):
        logger.info('Backtesting started')
        for i, candle in enumerate(self.candles):
            self.current_time = candle['close_time']
            self.update_positions(candle)
            signal = strategy.get_signal(candle, self.positions)
            self.handle_signal(signal, candle)
        self.close_all_positions()
        logger.info('Backtesting completed')

    def update_positions(self, candle):
        """更新持仓信息"""
        for position in self.positions:
            if position['side'] == OrderSide.BUY:
                position['unrealized_profit'] = (candle['close'] - position['entry_price']) * position['quantity']
            else:
                position['unrealized_profit'] = (position['entry_price'] - candle['close']) * position['quantity']
            position['value'] = position['entry_price'] * position['quantity'] + position['unrealized_profit']

    def handle_signal(self, signal, candle):
        if signal == 1 and len(self.positions) < self.max_positions:
            self.enter_long(candle['close'])
        elif signal == -1 and len(self.positions) < self.max_positions:
            self.enter_short(candle['close'])
        elif signal == 0 and len(self.positions) > 0:
            self.close_all_positions()

    def enter_long(self, price):
        """买入开多"""
        quantity = round_down(self.balance / price, 4)
        if quantity == 0:
            return
        stop_loss_price = round_down(price * 0.99, 2)
        take_profit_price = round_up(price * 1.01, 2)
        self.open_position(price, quantity, stop_loss_price, take_profit_price)

    def enter_short(self, price):
        """卖出开空"""
        quantity = round_down(self.balance / price, 4)
        if quantity == 0:
            return
        stop_loss_price = round_up(price * 1.01, 2)
        take_profit_price = round_down(price * 0.99, 2)
        self.open_position(price, -quantity, stop_loss_price, take_profit_price)

    def open_position(self, price, quantity, stop_loss_price, take_profit_price):
        if quantity > 0:
            side = OrderSide.BUY
            fee = calc_trade_fee(price, quantity, self.fee_rate)
            cost = price * quantity
        else:
            side = OrderSide.SELL
            fee = calc_trade_fee(price, -quantity, self.fee_rate)
            cost = -price * quantity
        if cost > self.balance:
            return
        self.balance -= cost + fee
        self.order_history.append
        
    def open_position(self, price, quantity, stop_loss_price, take_profit_price):
        """开仓"""
        self.current_position = Position(self.api_client, self.symbol)
        if quantity < 0:
            self.current_position.enter_short(-quantity, price)
        else:
            self.current_position.enter_long(quantity, price)
        if stop_loss_price is not None:
            self.current_position.set_stop_loss(stop_loss_price)
        if take_profit_price is not None:
            self.current_position.set_take_profit(take_profit_price)
        self.positions.append(self.current_position)

    def close_position(self, price):
        """平仓"""
        if self.current_position is not None:
            self.current_position.close_position(self.api_client)
            self.current_position = None
        if self.positions:
            self.positions[-1].update_position(self.api_client)
        if self.positions and not self.positions[-1].is_open:
            self.realized_pnl += self.positions[-1].unrealized_profit
            self.positions.pop()
