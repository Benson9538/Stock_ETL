-- Active: 1774688185021@@172.25.112.1@5432@stock_db

CREATE TABLE IF NOT EXISTS stock_prices (
    id                  SERIAL PRIMARY KEY,
    ticker              VARCHAR(20) NOT NULL,
    datetime            TIMESTAMPTZ NOT NULL,
    open                FLOAT,
    high                FLOAT,
    low                 FLOAT,
    close               FLOAT,
    volume              BIGINT,
    ma20                FLOAT,
    ma60                FLOAT,
    rsi                 FLOAT,
    atr                 FLOAT,
    return_pct          FLOAT,
    volume_change_pct   FLOAT,
    golden_cross        BOOLEAN,
    death_cross         BOOLEAN,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, datetime)
)