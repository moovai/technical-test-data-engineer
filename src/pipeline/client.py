from typing import Iterable
import httpx
from .config import API_BASE_URL, API_PAGE_SIZE


def iter_paginated(path: str, size: int = API_PAGE_SIZE) -> Iterable[dict]:
    page = 1
    with httpx.Client(base_url=API_BASE_URL, timeout=30) as client:
        while True:
            response = client.get(path, params={"page": page, "size": size})
            response.raise_for_status()

            data = response.json()

            items = data.get("items", [])
            if not items:
                break
            for row in items:
                yield row

            if len(items) < size:
                break
            page += 1
