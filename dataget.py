import requests
import pandas as pd

def get_klines(symbol, interval, days):
    # 計算時間區間的開始和結束時間
    now = pd.Timestamp.now()
    start_time = now - pd.Timedelta(days=days)
    end_time = now

    # 計算時間區間的毫秒數
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)

    # 設定 API 請求 URL 和參數
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': 1000,
        'startTime': start_timestamp,
        'endTime': end_timestamp
    }

    # 透過 Binance API 取得 K 線資料
    klines = []
    while True:
        res = requests.get(url, params=params)
        data = res.json()
        if not data:
            break
        klines.extend(data)
        params['endTime'] = data[0][0] - 1
        if len(klines) >= days * 24:  # 超過 2 年分的 K 線資料
            break

    # 將 K 線資料轉換成 DataFrame
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore'])

    # 將時間戳記轉換成本地時間
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

def save_to_csv(df, symbol, interval, days):
    # 將資料輸出成 CSV 檔案
    filename = f'{symbol}_{interval}_{days}d_klines.csv'
    df.to_csv(filename, index=False)
    print(f'{filename} has been saved.')

if __name__ == '__main__':
    symbol = 'ETHUSDT'
    interval = '1h'
    days = 365 * 2  # 下載 2 年內的 K 線資料
    limit = 1000

    df = pd.DataFrame()
    while days > 0:
        # 每次下載 1 天內的 K 線資料
        df_temp = get_klines(symbol, interval, 1)
        df = pd.concat([df, df_temp])
        days -= 1

    save_to_csv(df, symbol, interval, days)



