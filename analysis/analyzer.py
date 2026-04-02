import ollama
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TICKER_NAMES = {
    "2330.TW": "台積電",
    "2308.TW": "台達電",
    "0050.TW": "元大台灣50",
    "009816.TW": "凱基台灣TOP50",
    "GOOGL": "Google",
    "NVDA": "輝達",
    "SPY": "標普500 ETF",
    "VT": "Vanguard全球ETF",
}

ETF_TICKERS = {"0050.TW", "009816.TW", "SPY", "VT"}

OLLAMA_HOST = os.getenv("OLLAMA_HOST")


def get_latest_indicators():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT ON (ticker)
            ticker, datetime, close, ma20, ma60,
            rsi, atr, return_pct, volume_change_pct,
            golden_cross, death_cross
        FROM stock_prices
        WHERE ma20 IS NOT NULL AND rsi != 0 AND rsi IS NOT NULL
        ORDER BY ticker, datetime DESC
    """)

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [dict(zip(cols, row)) for row in rows]

def analyze_fundamental(ticker, name):
    is_etf = ticker in ETF_TICKERS

    if is_etf:
        prompt = f"""
你是一位專業的投資分析師，請針對以下 ETF 進行分析。
請用純繁體中文回答，不要使用任何英文單字。

ETF 名稱：{name}（{ticker}）

請依照以下格式回答，每點不超過三句話：

1. ETF 簡介（追蹤哪個指數，主要成分股是什麼）
2. 費用率與效率（管理費是否合理，追蹤誤差如何）
3. 長期報酬（歷史上這個指數的長期年化報酬率）
4. 主要風險（投資這個 ETF 最大的風險是什麼）
5. 長期投資建議（適合長期持有、定期定額，還是觀望）
"""
    else:
        prompt = f"""
你是一位專業的股票分析師，請針對以下股票進行基本面分析。
請用純繁體中文回答，不要使用任何英文單字。

股票名稱：{name}（{ticker}）

請依照以下格式回答，每點不超過三句話：

1. 財務狀況（過去幾年營收、獲利趨勢是否健康）
2. 估值分析（目前本益比是否合理，與同業相比是否被高估或低估）
3. 成長潛力（未來3~5年的成長空間，是否有護城河或競爭優勢）
4. 主要風險（投資這支股票最大的風險是什麼）
5. 長期投資建議（適合長期持有、觀望，還是避開）
"""

    client = ollama.Client(host=OLLAMA_HOST)
    response = client.generate(
        model="llama3.2",
        prompt=prompt,
        options={"temperature": 0.1}
    )
    return response.response

def build_prompt(stock):
    ticker = stock["ticker"]
    # 找不到就用代碼
    name = TICKER_NAMES.get(ticker, ticker)
    ma20 = f"{stock['ma20']:.2f}" if stock["ma20"] is not None else "N/A"
    ma60 = f"{stock['ma60']:.2f}" if stock["ma60"] is not None else "N/A"
    rsi = f"{stock['rsi']:.2f}" if stock["rsi"] is not None else "N/A"
    atr = f"{stock['atr']:.2f}" if stock["atr"] is not None else "N/A"
    ret = f"{stock['return_pct']:.2f}" if stock["return_pct"] is not None else "N/A"
    vol = (
        f"{stock['volume_change_pct']:.2f}"
        if stock["volume_change_pct"] is not None
        else "N/A"
    )

    return f"""

【規則】
- 全程使用繁體中文，除了專有名詞（如指標名稱）外，不要使用英文。
- 避免用過於專業的術語，讓一般投資人也能理解。
- 每點分析盡量簡潔，重點突出，不要冗長。
- 回答格式須統一，按照以下格式，每一段中間隔一行：
股票名稱：
1. 技術面概況
2. 趨勢方向
3. 買賣壓力分析
4. 波動風險
5. 投資建議（持有、觀望或減碼）

你是一位專業的股票分析師，請根據以下技術指標，用繁體中文分析這支股票是否適合長期持有。

股票名稱 : {name}({ticker})
日期 : {stock['datetime']}
收盤價 : {stock['close']:.2f}
20日均線 : {ma20}
60日均線 : {ma60}
RSI : {rsi}
ATR : {atr}
日報酬率 : {ret}%
成交量變化率 : {vol}%
黃金交叉 : {"是" if stock['golden_cross'] else "否"}
死亡交叉 : {"是" if stock['death_cross'] else "否"}

請提供 :
1. 這支股票的技術面分析
2. 趨勢判斷
3. 超買超賣分析
4. 波動風險評估
5. 綜合建議 (持有/觀望/減碼)

請簡潔回答，每點不超過兩句話
"""


def analyze(stock):
    prompt = build_prompt(stock)
    client = ollama.Client(host=OLLAMA_HOST)
    response = client.generate(model="llama3.2", prompt=prompt)
    return response.response


def save_report(ticker, content):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cursor = conn.cursor()
    # DO UPDATE SET content = EXCLUDED.content
    # 遇到重複的 ticker 和 report_date 時，更新 content 欄位
    cursor.execute(
        """
        INSERT INTO analysis_reports (ticker, report_date, content)
        VALUES (%s, %s, %s)
        ON CONFLICT (ticker, report_date) DO UPDATE
        SET content = EXCLUDED.content
    """,
        (ticker, datetime.now().date(), content),
    )
    conn.commit()
    cursor.close()
    conn.close()


def run_analysis():
    stocks = get_latest_indicators()
    today = datetime.now().strftime("%Y-%m-%d")
    report_lines = [f"股票分析報告 - {today}", "=" * 30]

    for stock in stocks:
        ticker = stock['ticker']
        name = TICKER_NAMES.get(ticker, ticker)
        print(f"\n分析 {name}（{ticker}）...")

        # 技術面分析
        technical = analyze(stock)

        # 基本面分析
        fundamental = analyze_fundamental(ticker, name)

        # 存進資料庫
        combined = f"【技術面】\n{technical}\n\n【基本面】\n{fundamental}"
        save_report(ticker, combined)

        report_lines.append(f"\n{'='*30}")
        report_lines.append(f"股票名稱：{name}（{ticker}）")
        report_lines.append(f"\n【技術面分析】")
        report_lines.append(technical)
        report_lines.append(f"\n【基本面分析】")
        report_lines.append(fundamental)
        report_lines.append("-" * 30)

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = f"{report_dir}/{today}.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n 報告已儲存至 {report_path}")


if __name__ == "__main__":
    run_analysis()
