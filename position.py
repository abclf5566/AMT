from decimal import Decimal
import time

from .enums import PositionType
from .api_client import APIClient
from .logger import logger


class Position:
    def __init__(self, api_client: APIClient, symbol: str):
        self.api_client = api_client
        self.symbol = symbol
        self.is_open = False
        self.quantity = Decimal(0)
        self.entry_price = Decimal(0)
        self.position_type = None
        self.trailing_stop = None

    def update_position(self, api_client: APIClient):
        """获取当前仓位信息"""
        response = api_client.request('GET', '/api/v2/account', auth=True, params={
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        })
        if response.status_code == 200:
            data = response.json()
            for position in data['positions']:
                if position['symbol'] == self.symbol:
                    self.quantity = Decimal(position['positionAmt'])
                    self.entry_price = Decimal(position['entryPrice'])
                    self.position_type = PositionType.from_value(position['positionSide'])
                    self.is_open = self.quantity != 0
                    break

    def open_position(self, symbol: str, quantity: Decimal, price: Decimal):
        """开仓"""
        if quantity <= 0:
            return
        if self.is_open:
            self.close_position(self.api_client)
        if quantity < 0:
            side = 'SELL'
            quantity = abs(quantity)
        else:
            side = 'BUY'
        response = self.api_client.request('POST', '/api/v3/order', params={
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'quantity': quantity,
            'price': price,
            'timeInForce': 'GTC',
            'newOrderRespType': 'FULL',
            'timestamp': int(time.time() * 1000),
        })
        if response.status_code == 200:
            self.update_position(self.api_client)
            logger.info(f'{side} {quantity} {symbol} at {price}')
        else:
            logger.error(f'Failed to open position: {response.json()}')

    def enter_long(self, quantity, price):
        """买入开多"""
        self.open_position(self.symbol, quantity, price)

    def enter_short(self, quantity, price):
        """卖出开空"""
        self.open_position(self.symbol, -quantity, price)

    def set_stop_loss(self, stop_loss_price):
        """设置止损价"""
        response = self.api_client.request('POST', '/api/v3/order', params={
            'symbol': self.symbol,
            'side': self.position_type.opposite().value,
            'type': 'STOP_MARKET',
            'stopPrice': stop_loss_price,
            'quantity': self.quantity,
            'newOrderRespType': 'FULL',
            'timestamp': int(time.time() * 1000),
        })
        if response.status_code == 200:
            logger.info(f'Stop loss order placed at {stop_loss_price}')
        else:
            logger.error(f'Failed to set stop loss: {response.json()}')

    def set_trailing_stop(self, trailing_stop):
        """设置Trailing Stop参数"""
        self.trailing_stop = trailing_stop

    def update_stop_loss(self, price):
        """更新止损价，根据Trailing Stop参数进行计算"""
        if self.trailing_stop is not None:
            if self.position_type == PositionType.LONG:
                stop_loss_price = max(self.entry_price * (1 + self.trailing_stop), price * (1 + self.trailing_stop))
            elif self.position_type == PositionType.SHORT:
                stop_loss_price = min(self.entry_price * (1 - self.trailing_stop), price * (1 - self.trailing_stop))
            else:
                return
            self.set_stop_loss(stop_loss_price)

    def close_position(self, api_client):
        """平仓"""
        if self.is_open:
            response = api_client.request('POST', '/api/v3/order', params={
                'symbol': self.symbol,
                'side': self.position_type.value,
                'type': 'MARKET',
                'quantity': self.quantity,
                'newOrderRespType': 'FULL',
                'timestamp': int(time.time() * 1000),
            })
            if response.status_code == 200:
                self.is_open = False
                self.update_position(api_client)
                logger.info(f'{self.position_type.name} position closed')
            else:
                logger.error(f'Failed to close {self.position_type.name} position: {response.json()}')

    def update_position(self, api_client):
        """更新持仓信息"""
        response = api_client.request('GET', '/api/v3/positionRisk')
        if response.status_code == 200:
            position_risks = response.json()
            for position_risk in position_risks:
                if position_risk['symbol'] == self.symbol:
                    self.quantity = Decimal(position_risk['positionAmt'])
                    self.entry_price = Decimal(position_risk['entryPrice'])
                    self.unrealized_profit = Decimal(position_risk['unRealizedProfit'])
                    break
        else:
            logger.error(f'Failed to update {self.position_type.name} position: {response.json()}')

    def update_unrealized_profit(self, api_client):
        """更新未实现盈亏"""
        response = api_client.request('GET', '/api/v2/account', auth=True, params={
            'timestamp': int(time.time() * 1000),
            'recvWindow': 5000,
        })
        if response.status_code == 200:
            data = response.json()
            for position in data['positions']:
                if position['symbol'] == self.symbol:
                    self.unrealized_profit = Decimal(position['unRealizedProfit'])
                    break
        else:
            logger.error(f'Failed to update {self.position_type.name} unrealized profit: {response.json()}')
