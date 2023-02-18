import time
from datetime import datetime
from decimal import Decimal

from enums import PositionType
from logger import logger
from position import Position
from strategy import Strategy


class Backtest:
    def __init__(self, start_time: int, end_time: int, data: dict, fee: Decimal = Decimal('0.00075')):
        self.start_time = start_time
        self.end_time = end_time
        self.data = data
        self.fee = fee

    def run(self, api_key: str, secret_key: str, symbol: str, quantity: Decimal, leverage: int = 1,
            margin_type: str = 'isolated', initial_margin: Decimal = Decimal('100')):
        api_client = APIClient(api_key, secret_key, testnet=True)

        balance = self.get_balance(api_client, symbol)
        if balance is None:
            logger.error('Failed to get account balance')
            return

        position = Position(api_client, symbol)
        position.open_position(symbol, quantity, Decimal(self.data[self.start_time]['close']),
                               Decimal(self.data[self.start_time]['close']) * (1 - self.fee),
                               Decimal(self.data[self.start_time]['close']) * (1 + self.fee),
                               leverage, margin_type, initial_margin)
        strategy = Strategy(api_client, symbol, quantity, leverage, margin_type, initial_margin)

        for timestamp, tick in self.data.items():
            if timestamp < self.start_time or timestamp > self.end_time:
                continue

            price = Decimal(tick['close'])

            # 更新持仓信息
            position.update_position(api_client)
            strategy.update_position(position.quantity, position.entry_price, position.unrealized_profit)

            # 更新止损价
            position.update_stop_loss(price)

            # 更新交易策略
            strategy.update(price)

            # 执行交易
            if strategy.signal is not None:
                signal_type, signal_price = strategy.signal
                if signal_type == PositionType.LONG:
                    if position.is_open and position.position_type == PositionType.SHORT:
                        position.close_position(api_client)
                    if not position.is_open or position.position_type == PositionType.SHORT:
                        position.enter_long(quantity, price, price * (1 - self.fee), price * (1 + self.fee),
                                            leverage, margin_type, initial_margin)
                elif signal_type == PositionType.SHORT:
                    if position.is_open and position.position_type == PositionType.LONG:
                        position.close_position(api_client)
                    if not position.is_open or position.position_type == PositionType.LONG:
                        position.enter_short(quantity, price, price * (1 + self.fee), price * (1 - self.fee),
                                             leverage, margin_type, initial_margin)

            time.sleep(1)

        position.close_position(api_client)

    def get_balance(self, api_client, symbol):
        """获取当前余额"""
        response = api_client.request('GET', '/api/v2/account', auth=True, params={
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        })
        if response.status_code == 200:
            data = response.json()
            for balance in data['balances']:
                if balance['asset'] == symbol:
                    return Decimal(balance['free'])
            return Decimal(0)
        else:
            logger.error(f'Failed to get balance for {symbol}: {response.json()}')
            return Decimal(0)
