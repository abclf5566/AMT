import time
import logging
from strategy import BinanceStrategy


class BinanceTradingBot:
    def __init__(self, api_key, api_secret, symbol):
        self.strategy = BinanceStrategy(api_key, api_secret, symbol)
        
        # 設定logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(handler)

        self.running = False
        self.trades = []
        self.open_orders = []

    def start(self, quantity=0.01, leverage=1, stop_loss_pct=0.05, take_profit_pct=0.1):
        """啟動交易機器人"""
        self.running = True
        self.logger.info("交易機器人已啟動")
        self.logger.info(f"交易品種: {self.strategy.symbol}")
        self.logger.info(f"下單數量: {quantity}")
        self.logger.info(f"使用杠杆: {leverage}")
        self.logger.info(f"停損比例: {stop_loss_pct}")
        self.logger.info(f"止盈比例: {take_profit_pct}")

        # 進入主循環
        while self.running:
            # 檢查開盤委託單
            self.check_open_orders()

            # 執行策略
            self.strategy.get_asset_balance()
            self.strategy.get_btc_balance()
            self.strategy.start_trading(
                quantity=quantity, 
                leverage=leverage, 
                stop_loss_pct=stop_loss_pct, 
                take_profit_pct=take_profit_pct
            )

            # 暫停一段時間
            time.sleep(5)

    def stop(self):
        """停止交易機器人"""
        self.running = False
        self.logger.info("交易機器人已停止")

    def check_open_orders(self):
        """檢查開盤委託單"""
        orders = self.strategy.client.futures_get_open_orders(symbol=self.strategy.symbol)

        if len(orders) > 0:
            self.logger.info("有開盤委託單")
            self.logger.info(orders)
            self.open_orders = orders

        return orders
    def close_open_orders(self):
        """關閉所有開盤委託單"""
        if len(self.open_orders) > 0:
            for order in self.open_orders:
                self.logger.info(f"關閉開盤委託單 {order['orderId']}")
                self.strategy.client.futures_cancel_order(
                    symbol=self.strategy.symbol, 
                    orderId=order['orderId']
                )
            self.open_orders = []

    def close_all_positions(self):
        """關閉所有持倉"""
        self.logger.info("正在關閉所有持倉...")
        position = self.strategy.client.futures_position_information(symbol=self.strategy.symbol)

        if position[0]['positionAmt'] > 0:
            side = SIDE_SELL
        else:
            side = SIDE_BUY

        quantity = abs(float(position[0]['positionAmt']))
        self.strategy.client.futures_create_order(
            symbol=self.strategy.symbol, 
            side=side, 
           
