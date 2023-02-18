from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskManagement:
    """风险管理模块"""
    
    def __init__(self, max_position_pct, max_position_size, stop_loss_pct, take_profit_pct, fees_pct):
        self.max_position_pct = max_position_pct   # 最大仓位占比（0 ~ 1）
        self.max_position_size = max_position_size  # 最大仓位大小（计价货币）
        self.stop_loss_pct = stop_loss_pct         # 止损百分比（0 ~ 1）
        self.take_profit_pct = take_profit_pct     # 止盈百分比（0 ~ 1）
        self.fees_pct = fees_pct                   # 手续费占比（0 ~ 1）
        
    def set_max_position_pct(self, max_position_pct):
        """设置最大仓位占比"""
        self.max_position_pct = max_position_pct
        
    def set_max_position_size(self, max_position_size):
        """设置最大仓位大小"""
        self.max_position_size = max_position_size
        
    def set_stop_loss_pct(self, stop_loss_pct):
        """设置止损百分比"""
        self.stop_loss_pct = stop_loss_pct
        
    def set_take_profit_pct(self, take_profit_pct):
        """设置止盈百分比"""
        self.take_profit_pct = take_profit_pct
        
    def set_fees_pct(self, fees_pct):
        """设置手续费占比"""
        self.fees_pct = fees_pct
        
    def calculate_max_quantity(self, price, balance):
        """计算最大可开仓数量"""
        max_position_value = min(self.max_position_size, self.max_position_pct * balance * price)
        max_quantity = max_position_value / price
        return max_quantity
    
    def calculate_stop_loss_price(self, entry_price):
        """计算止损价"""
        if self.stop_loss_pct is not None:
            if entry_price is None:
                return None
            if self.stop_loss_pct == 0:
                return None
            if self.stop_loss_pct > 0:
                stop_loss_price = entry_price * (1 - self.stop_loss_pct)
            else:
                stop_loss_price = entry_price * (1 + self.stop_loss_pct)
            return stop_loss_price
        else:
            return None
        
    def calculate_take_profit_price(self, entry_price):
        """计算止盈价"""
        if self.take_profit_pct is not None:
            if entry_price is None:
                return None
            if self.take_profit_pct == 0:
                return None
            if self.take_profit_pct > 0:
                take_profit_price = entry_price * (1 + self.take_profit_pct)
            else:
                take_profit_price = entry_price * (1 - self.take_profit_pct)
            return take_profit_price
        else:
            return None
        
    def calculate_fees(self, quantity, price):
        """计算实际手续费"""
        return self.fees_pct * quantity * price
