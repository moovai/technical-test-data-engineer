import requests
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

log_dir = Path("/app/logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"data_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
    logging.FileHandler(log_file),
    logging.StreamHandler()
]
)

def extract_data():
    base_url = "http://fastapi:8000"
    endpoints = ["tracks", "users", "listen_history"]
    data_dir = Path("/app/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logging.info(f"Starting data extraction at {run_timestamp}")
    for endpoint in endpoints:
        all_data = []
        page = 1
        logging.info(f"Fetching endpoint: {endpoint}")
        while True:
            try:
                response = requests.get(f"{base_url}/{endpoint}?page={page}&size=100", timeout=10)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {endpoint} page {page}: {e}")
                raise
            
            if not data.get("items"):
                logging.info(f"No more items for {endpoint} at page {page}.")
                break
            
            all_data.extend(data["items"])
            logging.info(f"Fetched page {page} for {endpoint}, total items so far: {len(all_data)}")
            
            current_page = data.get("page", page)
            total_pages = data.get("pages", page)
            if current_page >= total_pages:
                logging.info(f"Reached last page {current_page}/{total_pages} for {endpoint}.")
                break
            page += 1
        
        df = pd.DataFrame(all_data)
        output_file = data_dir / f"{endpoint}_{run_timestamp}.csv"
        df.to_csv(output_file, index=False)
        logging.info(f"Saved {len(df)} records from {endpoint} to {output_file}")

    # Write completion marker
    completion_file = data_dir / f"pipeline_complete_{run_timestamp}.txt"
    with open(completion_file, "w") as f:
        f.write(datetime.now().isoformat())
    logging.info(f"Pipeline completion marker written to {completion_file}")
    # metadata for idempotency
    with open(data_dir / "latest_run.txt", "w") as f:
        f.write(run_timestamp)

if __name__ == "__main__":
    extract_data() 