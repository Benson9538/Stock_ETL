# Stock ETL pipeline

自動化股票資料抓取、技術指標計算、AI 分析報告

## 架構

1. yfinance : 定時自動抓取 Yahoo Finance 中的股票資料

2. ETL (Extract / Transform / Load): 進行數據清理、計算指標

3. PostgreSQL : 儲存股票資料及指標數據

4. Ollama : 透過 llama3.2 產出分析報告

5. cron : 設定自動排程，定時執行上述步驟，並產出各股票報告

6. CI/CD : Github Actions 自動執行格式檢查及單元測試