# uvicorn : 一個輕量級的 ASGI 伺服器，適合開發和測試 FastAPI 應用程式。
# -> swagger UI : FastAPI 內建的互動式 API 文件界面，讓開發者可以輕鬆測試和理解 API 的功能。
# uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

import os
import psycopg2
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Stock ETL API", description="股票技術指標與分析報告 API", version="1.0.0"
)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# 取得所有股票清單
@app.get("/stocks")
def get_stocks():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT ticker FROM stock_prices ORDER BY ticker;
    """)
    tickers = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"tickers": tickers}


# 取得特定股票的最新技術指標數據
@app.get("/stocks/{ticker}")
def get_stock(ticker: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ticker, datetime, close, ma20, ma60, rsi, atr,
                return_pct, volume_change_pct, golden_cross, death_cross
        FROM stock_prices
        WHERE ticker = %s
            AND ma20 IS NOT NULL
            AND rsi  IS NOT NULL
            AND rsi  != 0
            AND atr  IS NOT NULL
        ORDER BY datetime DESC
        LIMIT 1;
    """,
        (ticker.upper(),),
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=404, detail="Stock not found or insufficient data"
        )

    cols = [
        "ticker",
        "datetime",
        "close",
        "ma20",
        "ma60",
        "rsi",
        "atr",
        "return_pct",
        "volume_change_pct",
        "golden_cross",
        "death_cross",
    ]

    return dict(zip(cols, row))


# 某支股票的最新分析報告
@app.get("/stocks/{ticker}")
def get_report(ticker: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ticker, report_date, content
        FROM analysis_reports
        WHERE tocker = %s
        ORDER BY report_date DESC
        LIMIT 1;
    """,
        (ticker.upper(),),
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "ticker": row[0],
        "report_date": row[1],
        "content": row[2],
    }


# 取得今日所有股票的最新報告
@app.get("/reports")
def get_all_reports():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ticker, report_date, content
        FROM analysis_reports
        ORDER BY ticker, report_date DESC;
    """)

    cols = ["ticker", "report_date", "content"]
    row = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"reports": [dict(zip(cols, r)) for r in row]}
