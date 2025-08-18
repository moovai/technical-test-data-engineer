import requests
import os
import datetime
from urllib3.exceptions import NotOpenSSLWarning
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def retry_mechanism(total = 3, backoff = 1):
    session = requests.Session()
    retry = Retry(
        total=total,
        backoff_factor=backoff,
        status_forcelist=(500, 502, 503, 504, 429),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)

    return session

def iter_pages(endpoint: str, size):
    sess = retry_mechanism()
    page = 1
    while True:
        resp = sess.get(f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}",
                        params={"page": page, "size": size}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        yield data # This will yield (stream) each page of data as a dictionary. It streams pages and bulk upserts per page, which minimizes memory.
        if page >= data.get("pages", page):
            break
        page += 1

if __name__ == "__main__":
    main()

