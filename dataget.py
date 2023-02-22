import requests
import pandas as pd

def get_klines(symbol, interval, start_time, end_time):
    # 設定 API 請求 URL 和參數
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000
    }

    # 透過 Binance API 取得 K 線資料
    klines = []
    while True:
        res = requests.get(url, params=params)
        data = res.json()
        if not data:
            break
        klines.extend(data)
        params['startTime'] = data[-1][0] + 1

    # 將 K 線資料轉換成 DataFrame
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades', 'taker buy base asset volume', 'taker buy quote asset volume', 'ignore'])

    # 將時間戳記轉換成本地時間
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

def save_klines_to_csv(df, symbol, interval, start_time, end_time):
    # 將資料輸出成 CSV 檔案
    filename = f'{symbol}_{interval}_{start_time}_{end_time}.csv'
    df.to_csv(filename, index=False)
    print(f'{filename} has been saved.')

if __name__ == '__main__':
    symbol = 'BTCUSDT'
    interval = '1h'
    days = 365 * 2  # 下載 2 年內的 K 線資料

    # 計算時間區間的開始和結束時間
    now = pd.Timestamp.now()
    end_time = now
    start_time = now - pd.Timedelta(days=days)

    # 循環獲取 K 線資料
    klines = pd.DataFrame()
    while start_time < end_time:
        # 計算本次 API 請求的結束時間
        next_end_time = start_time + pd.Timedelta(days=1)

        # 下載 K 線資料
        df = get_klines(symbol, interval, int(start_time.timestamp() * 1000), int(next_end_time.timestamp() * 1000))

        # 將 K 線資料合併到結果中
        klines = pd.concat([klines, df])

        # 計算下一次 API 請求的開始時間
        start_time = next_end_time

    # 儲存 K 線數據到 CSV 文件中
    save_klines_to_csv(klines, symbol, interval, int((now - pd.Timedelta(days=days)).timestamp() * 1000), int(now.timestamp() * 1000))
