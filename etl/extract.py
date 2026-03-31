import yfinance as yf
import pandas as pd

STOCKS = {
    "台股": ["2330.TW", "2308.TW", "0050.TW", "009816.TW"],
    "美股": ["GOOGL", "NVDA", "SPY", "VT"],
}


# 從 Yahoo Finance 提取股票數據
# period 抓多長時間 : 1d , 5d , 1mo , 3mo ...
# interval 間隔多久 : 1m , 2m , 5m , 15m , 30m , 60m ...
def extract(period="6mo", interval="1d"):
    all_stocks = STOCKS["台股"] + STOCKS["美股"]

    dfs = []
    for ticker in all_stocks:
        print(f"抓取 {ticker}")

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,  # 不顯示進度條
            auto_adjust=True,  # 自動調整價格 (考慮除權息等因素)
        )

        if df.empty:
            print(f"{ticker} 無資料")
            continue

        # ("Open" , "2330.TW") -> "Open"
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df["ticker"] = ticker
        df = df.reset_index()  # 把時間從 index 變成 column
        df = df.rename(
            columns={
                "Datetime": "datetime",
                "Date": "datetime",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )

        df = df.dropna()
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    res = pd.concat(dfs, ignore_index=True)
    print(f"共抓取 {len(res)} 筆資料")
    return res


if __name__ == "__main__":
    df = extract()
    print(df.head())
    print(df.columns.tolist())
