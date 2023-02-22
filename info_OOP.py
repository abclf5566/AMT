import binance

class BinanceClient:
    """
    Binance用戶端類別，封裝了Binance API，提供了許多方便的方法來獲取用戶資訊。
    """

    def __init__(self, api_key, api_secret):
        """
        初始化Binance用戶端
        :param api_key: API Key
        :param api_secret: API Secret
        """
        self.client = binance.Client(api_key, api_secret)

    def get_futures_account(self):
        """
        獲取Binance合約賬戶信息
        :return: 賬戶信息
        """
        account = self.client.futures_account()
        return account

    def get_spot_account(self):
        """
        獲取Binance現貨賬戶信息
        :return: 賬戶信息
        """
        account = self.client.get_account()
        return account

    def get_balance(self, asset, account_type='spot'):
        """
        獲取Binance用戶指定幣種的可用餘額
        :param asset: 幣種
        :param account_type: 賬戶類型，'spot'表示現貨賬戶，'futures'表示合約賬戶
        :return: 可用餘額
        """
        if account_type == 'spot':
            account = self.get_spot_account()
            balance = float(account['balances'][asset]['free'])
        elif account_type == 'futures':
            account = self.get_futures_account()
            balance = float(account['totalWalletBalance'])
        else:
            raise ValueError('Invalid account type')

        return balance

    def get_trade_fee_rate(self, symbol):
        """
        獲取指定交易對的交易手續費率
        :param symbol: 交易對
        :return: 交易手續費率
        """
        trade_fee = self.client.get_trade_fee(symbol=symbol)
        return float(trade_fee['makerCommission']) / 10000
