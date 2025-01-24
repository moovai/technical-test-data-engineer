import logging
import os
from typing import Dict, Any
import datetime
import pandas as pd

from utils import fetch_all_pages, transform_tracks, transform_users, transform_listen_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1"
PORT = 8000
ENDPOINTS = {
    "tracks": "/tracks",
    "users": "/users",
    "listen_history": "/listen_history",
}
PAGE_SIZE = 100
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data/")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


class PipelineETL:
    def __init__(self, base_url:str=BASE_URL, port:int=PORT, endpoints:Dict[str, str]=ENDPOINTS):
        self.url = f"{base_url}:{port}"
        self.endpoints = endpoints
        self.transform_functions = {
            "tracks": transform_tracks,
            "users": transform_users,
            "listen_history": transform_listen_history,
        }

    def extract(self, source:str) -> pd.DataFrame:
        all_items = fetch_all_pages(url=source, params={'page':1, 'size':PAGE_SIZE})
        return pd.DataFrame(all_items)
            
    def transform(self, df:pd.DataFrame, endpoint:str) -> pd.DataFrame:
        try:         
            # Possibilité d'ajouter des transformations spécifiques pour chaque endpoint
            transform_func = self.transform_functions.get(endpoint)
            
            if transform_func:
                df = transform_func(df)
            else:
                logger.warning(f"No transformation function found for endpoint: {endpoint}")
                df = pd.DataFrame()
            return df
        except Exception as e:
            logger.error(f"Error transformation endpoint {endpoint}: {e}")
            return pd.DataFrame()

    def load(self, endpoint:str, data:pd.DataFrame):
        if data.empty:
            logger.warning(f"No data to load for endpoint {endpoint}")
            return
        try:    
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            data.to_csv(f"{OUTPUT_DIR}/{endpoint}/{endpoint}_{timestamp}.csv", index=False)
        except Exception as e:
            logger.error(f"Error loading endpoint {endpoint}: {e}")

    def run(self):
        logger.info("Starting pipeline")
        if not self.endpoints:
            logger.error("No endpoints found, please check your configuration. Pipeline will not run without endpoints.")
            return
        for endpoint, path in self.endpoints.items():
            logger.info(f"Initializing endpoint {endpoint}")
            try:
                if not os.path.exists(f"{OUTPUT_DIR}/{endpoint}"):
                    os.makedirs(f"{OUTPUT_DIR}/{endpoint}")
                logger.info(f"Extracting data from {self.url}{path}")
                data = self.extract(f"{self.url}{path}")
                logger.info(f"Transforming data for endpoint {endpoint}")
                transformed_data = self.transform(data, endpoint)
                logger.info(f"Loading data to {endpoint}")
                self.load(endpoint=endpoint, data=transformed_data)
                logger.info(f"Pipeline completed for endpoint {endpoint}")
            except Exception as e:
                logger.error(f"Error running pipeline for endpoint {endpoint}: {e}")
        logger.info("Pipeline completed")

if __name__ == "__main__":
    pipeline = PipelineETL(BASE_URL, 8001, ENDPOINTS)
    pipeline.run()
