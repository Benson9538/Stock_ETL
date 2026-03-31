import os
import pandas as pd
from sqlalchemy import create_engine , text
from dotenv import load_dotenv

load_dotenv(override=False)

def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    
def load(df):
    if df.empty:
        return 
    engine = get_engine()
    
    cols = [
        "ticker", "datetime", "open", "high", "low", "close", "volume",
        "ma20", "ma60", "rsi", "atr",
        "return_pct", "volume_change_pct",
        "golden_cross", "death_cross"
    ]
    df_load = df[cols].copy()
    
    with engine.connect() as conn:
        for _ , row in df_load.iterrows():
            conn.execute(text("""
                INSERT INTO stock_prices(
                    ticker , datetime , open , high , low , close , volume,
                    ma20 , ma60 , rsi , atr ,
                    return_pct , volume_change_pct,
                    golden_cross , death_cross
                )
                VALUES(
                    :ticker, :datetime, :open, :high, :low, :close, :volume,
                    :ma20, :ma60, :rsi, :atr,
                    :return_pct, :volume_change_pct,
                    :golden_cross, :death_cross
                )
                ON CONFLICT (ticker , datetime) DO NOTHING
            """), row.to_dict())
            
        conn.commit()
        
    print("Data loaded successfully.")
    
if __name__ == "__main__":
    from extract import extract
    from transform import transform
    
    df_raw = extract(period="6mo" , interval="1d")
    df_transformed = transform(df_raw)
    load(df_transformed)