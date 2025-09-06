from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


@dataclass
class Page:
    """ The FastAPI app used in this technical test returns objects compatible
    with the `fastapi‑pagination` package.  Each response includes the
    current page number, total pages, total number of items and a list of
    items for that page.
    """

    page: int
    pages: int
    total: int
    size: int
    items: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Page":
        return cls(
            page=data.get("page", 1),
            pages=data.get("pages", 1),
            total=data.get("total", len(data.get("items", []))),
            size=data.get("size", len(data.get("items", []))),
            items=data.get("items", []),
        )


def fetch_paginated_endpoint(
    endpoint: str,
    base_url: str = "http://localhost:8000",
    page_size: int = 100,
    session: Optional[requests.Session] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all records from a paginated endpoint.

    Args:
        endpoint: Path of the endpoint (e.g. "tracks", "users").  It will
            be appended to the `base_url`.
        base_url: Base URL of the API (default points to local Uvicorn server).
        page_size: Number of items per page.  Must be between 1 and 100 for
            compatibility with the FastAPI app.  The default of 100 matches
            the server's own default.
        session: Optional `requests.Session` instance for connection
            pooling.  A new session will be created if one is not provided.

    Returns:
        A list of dictionaries representing all records returned by the endpoint.

    Raises:
        `requests.HTTPError` if any of the HTTP requests return a non‑2xx status.
    """
    if session is None:
        session = requests.Session()
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    all_items: List[Dict[str, Any]] = []
    current_page = 1
    while True:
        params = {"page": current_page, "size": page_size}
        logger.debug("Requesting %s page %s", endpoint, current_page)
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        page_obj = Page.from_dict(payload)
        all_items.extend(page_obj.items)
        logger.debug(
            "Fetched %d items (page %d/%d) from %s",
            len(page_obj.items),
            page_obj.page,
            page_obj.pages,
            endpoint,
        )
        if page_obj.page >= page_obj.pages:
            break
        current_page += 1
    logger.info("Retrieved %d records from %s", len(all_items), endpoint)
    return all_items


def save_json(data: Iterable[Dict[str, Any]], filepath: str) -> None:
    """Each item in the iterable will be written as a JSON object separated by
    newlines ("JSONL" format).  Existing files will be overwritten.

    Args:
        data: An iterable of dictionaries.
        filepath: Path of the output file.  Parent directories will be
            created if necessary.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf‑8") as f:
        for record in data:
            json.dump(record, f, default=str)
            f.write("\n")
    logger.info("Saved %d records to %s", sum(1 for _ in data), filepath)


def run_pipeline(
    base_url: str = "http://localhost:8000",
    output_dir: str = "output",
    page_size: int = 100,
) -> None:
    """The function sequentially downloads data from the three API endpoints and
    writes the results to the specified output directory.  Filenames are
    suffixed with the current date to make snapshots easy to identify.

    Args:
        base_url: Root URL of the FastAPI server.
        output_dir: Directory where JSON files should be stored.
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    endpoints = ["tracks", "users", "listen_history"]
    for endpoint in endpoints:
        records = fetch_paginated_endpoint(endpoint, base_url=base_url, page_size=page_size)
        filename = f"{endpoint}_{date_str}.jsonl"
        save_json(records, os.path.join(output_dir, filename))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download data from the MooVitamix API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Root URL of the API")
    parser.add_argument("--output-dir", default="output", help="Directory to store output JSON files")
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of items per page (1–100). Must match server constraints.",
    )
    args = parser.parse_args()

    run_pipeline(base_url=args.base_url, output_dir=args.output_dir, page_size=args.page_size)