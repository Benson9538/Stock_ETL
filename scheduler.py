"""
APScheduler : python 排程套件，設定程式在特定時間自動執行
    - interval : 每隔多久執行一次
    - cron : 在特定時間點執行
    - date : 在特定日期時間執行一次
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apsecheduler.triggers.cron import CronTrigger

from etl.extract import extract
from etl.transform import transform
from etl.load import load

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s"

)
logger = logging.getLogger(__name__)

def run_etl():
    logger.info("開始執行 ETL")
    try:
        df_raw = extract(period="5d" , interval="1d")
        df_transformed = transform(df_raw)
        load(df_transformed)
        logger.info("ETL 執行完成")
    except Exception as e:
        logger.error(f"ETL 執行失敗: {e}")
        
if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    
    scheduler.add_job(
        run_etl,
        CronTrigger(hour=14, minute=0) # 每天 18:00 執行
        id = "daily_etl",
        name = "每日股票資料抓取",
    )
    
    logger.info("排程啟動，每天 18:00 執行 ETL")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt):
        logger.info("排程已停止")