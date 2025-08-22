import os
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_PAGE_SIZE = int(os.getenv("API_PAGE_SIZE", "100"))
DATA_DIR = os.getenv("DATA_DIR", "./data")
