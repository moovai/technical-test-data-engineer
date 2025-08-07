import schedule
import time
from datetime import datetime
from daily_pipeline import fetch_and_store_data
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    logging.info("Starting scheduled data pipeline run")
    try:
        fetch_and_store_data()
        logging.info("Pipeline run completed successfully")
    except Exception as e:
        logging.error(f"Error during pipeline execution: {str(e)}")

def main():
    # Schedule the pipeline to run daily at 2 AM
    schedule.every().day.at("02:00").do(run_pipeline)
    
    logging.info("Scheduler started. Waiting for scheduled runs...")
    
    # Initial run (optional)
    run_pipeline()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()