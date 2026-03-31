# pytest :
# test_*.py : pytest 自動找到檔案
# test_* : pytest 自動找到函式
# assert : 不成立就算失敗

import pandas as pd
import os
import sys

# 該 python 在 Stock-etl/tests/ 下面
# anspath : 轉成絕對路徑
# dirname * 2 : 取上一層目錄 * 2 -> cd ../..
# insert 0 : 把路徑放在最前面，確保優先找到
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import extract
from etl.transform import transform

# 確認 extract 回傳 DataFrame
def test_extract_returns_dataframe():
    df = extract(period='5d', interval='1d')
    assert isinstance(df, pd.DataFrame)
    
# 確認 extract 有必要欄位
def test_extract_has_required_columns():
    df = extract(period='5d', interval='1d')
    required_cols = ["ticker", "datetime", "open", "high", "low", "close", "volume"]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
        
# 確認所有股票都有抓到
def test_extract_has_all_tickers():
    df = extract(period='5d', interval='1d')
    expected_tickers = set(["2330.TW", "2308.TW", "0050.TW", "009816.TW",
                        "GOOGL", "NVDA", "SPY", "VT"])
    actual_tickers = df['ticker'].unique().tolist()
    for ticker in expected_tickers:
        assert ticker in actual_tickers, f"缺少股票：{ticker}"
        
# 確認 transform 有計算指標
def test_transform_adds_indicators():
    df_raw = extract(period='6mo', interval='1d')
    df = transform(df_raw)
    indicator_cols = ["ma20", "ma60", "rsi", "atr",
                    "return_pct", "volume_change_pct",
                    "golden_cross", "death_cross"]
    for col in indicator_cols:
        assert col in df.columns, f"Missing indicator column: {col}"
        
# 確認 rsi 值在合理範圍
def test_transform_rsi_range():
    df_raw = extract(period='6mo', interval='1d')
    df = transform(df_raw)
    # 保留 rsi 不為空且不為 0 的行
    rsi_values = df[df["rsi"].notna() & (df["rsi"] != 0)]
    assert (rsi_values["rsi"] >= 0).all(), "RSI with negative value"
    assert (rsi_values["rsi"] <= 100).all(), "RSI over 100"