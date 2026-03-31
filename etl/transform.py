# 趨勢 :
#   - MA20/MA60 : 中長期趨勢，在均線上面為趨勢向上
#   - 黃金/死亡交叉 : 買進/賣出訊號

# 波動 :
#   - ATR 平均真實波幅 : 衡量每天波動幅度
#   - 最大回撤 : 最大跌幅

# 市場熱度 :
#   - 成交量變化率 : 量增價跌 -> 賣壓增大 , 量縮價漲 -> 少數人堆高
#   - RSI 相對強弱指標 : 0 ~ 100 衡量超買(>70)/超賣(<30)

import pandas as pd


def transform(df):
    if df.empty:
        return df

    res = []

    for ticker in df["ticker"].unique():
        df_ticker = df[df["ticker"] == ticker].copy()
        df_ticker = df_ticker.sort_values("datetime").reset_index(drop=True)

        df_ticker["ma20"] = df_ticker["close"].rolling(window=20).mean()
        df_ticker["ma60"] = df_ticker["close"].rolling(window=60).mean()

        # shift(1) : 前一筆資料
        df_ticker["golden_cross"] = (df_ticker["ma20"] > df_ticker["ma60"]) & (
            df_ticker["ma20"].shift(1) <= df_ticker["ma60"].shift(1)
        )

        df_ticker["death_cross"] = (df_ticker["ma20"] < df_ticker["ma60"]) & (
            df_ticker["ma20"].shift(1) >= df_ticker["ma60"].shift(1)
        )

        # RSI
        delta = df_ticker["close"].diff()
        # clip(lower=0) : 負數變成 0 , upper=0 : 正數變成 0
        gain = delta.clip(lower=0)
        avg_gain = gain.rolling(window=14).mean()
        # 正數才能做除法
        loss = -delta.clip(upper=0)
        avg_loss = loss.rolling(window=14).mean()
        avg_loss = avg_loss.replace(0, float("nan"))
        rs = avg_gain / avg_loss
        df_ticker["rsi"] = 100 - (100 / (1 + rs))

        df_ticker["rsi"] = df_ticker["rsi"].fillna(
            df_ticker["rsi"].apply(lambda x: 100 if avg_gain.mean() > 0 else 0)
        )

        # 報酬率
        df_ticker["return_pct"] = df_ticker["close"].pct_change() * 100

        # 成交量變化率
        df_ticker["volume_change_pct"] = df_ticker["volume"].pct_change() * 100

        # ATR(14期) , 取三者最大值 : 當天高點-低點 , 昨收-當天高點 , 昨收-當天低點
        high_low = df_ticker["high"] - df_ticker["low"]
        high_close = (df_ticker["high"] - df_ticker["close"].shift(1)).abs()
        low_close = (df_ticker["low"] - df_ticker["close"].shift(1)).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df_ticker["atr"] = true_range.rolling(window=14).mean()

        res.append(df_ticker)

    df_res = pd.concat(res, ignore_index=True)
    print(f"transform {len(df_res)} 筆資料")
    return df_res


if __name__ == "__main__":
    from extract import extract

    df_raw = extract()
    df_transformed = transform(df_raw)
    print(
        df_transformed[["ticker", "datetime", "close", "ma20", "rsi", "atr"]]
        .dropna()
        .head()
    )
