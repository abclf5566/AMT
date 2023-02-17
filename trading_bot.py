import time
import logging
import schedule
import configparser
from strategy import BinanceStrategy
from binance.exceptions import BinanceAPIException


def run_bot():
    """執行交易機器人"""
    try:
        # 讀取config
        config = configparser.ConfigParser()
        config.read('config.ini')
        api_key = config.get('BINANCE', 'API_KEY')
        api_secret = config.get('BINANCE', 'API_SECRET')
        symbol = config.get('BOT', 'SYMBOL')
        quantity = float(config.get('BOT', 'QUANTITY'))
        leverage = int(config.get('BOT', 'LEVERAGE'))
        stop_loss_pct = float(config.get('BOT', 'STOP_LOSS_PCT'))
        take_profit_pct = float(config.get('BOT', 'TAKE_PROFIT_PCT'))

        # 初始化策略
        strategy = BinanceStrategy(api_key, api_secret, symbol)

        # 設定交易參數
        strategy.set_stop_loss_pct(stop_loss_pct)
        strategy.set_take_profit_pct(take_profit_pct)

        # 啟動交易機器人
        strategy.start_trading(quantity=quantity, leverage=leverage)

    except BinanceAPIException as e:
        logging.error(f"下單失敗: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()])

    # 每30秒執行一次交易
    schedule.every(30).seconds.do(run_bot)

    while True:
        schedule.run_pending()
        time.sleep(1)
