import requests
import pandas as pd

# 設定所需下載的交易對和時間區間
symbol = 'AVAXUSDT'
interval = '1h'
limit = 1000

# 設定 API 請求 URL 和參數
url = 'https://api.binance.com/api/v3/klines'
params = {
    'symbol': symbol,
    'interval': interval,
    'limit': limit,
    'endTime': int(pd.Timestamp.now().timestamp() * 1000)  # 現在時間的毫秒數
}

# 計算開始時間的毫秒數
DAYS = 365  # 設定需要下載的天數
start_timestamp = int((pd.Timestamp.now() - pd.Timedelta(days=DAYS)).timestamp() * 1000)
params['startTime'] = start_timestamp

# 透過 Binance API 取得 K 線資料
klines = []
while True:
    res = requests.get(url, params=params)
    data = res.json()
    if not data:
        break
    klines.extend(data)
    params['endTime'] = data[0][0] - 1

# 將 K 線資料轉換成 DataFrame
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore'])

# 將時間戳記轉換成本地時間
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 將資料輸出成 CSV 檔案
filename = f'{symbol}_{interval}_{DAYS}d_klines.csv'
df.to_csv(filename, index=False)

print(f'{filename} has been saved.')
