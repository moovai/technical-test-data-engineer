import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

from unittest.mock import Mock, patch

from src.data_pipeline import fetch_paginated_endpoint, save_json


def make_page(page: int, pages: int, size: int, items: List[Dict[str, int]]) -> Dict[str, any]:
    """Helper to construct a payload similar to the FastAPI pagination format."""
    return {
        "page": page,
        "pages": pages,
        "total": pages * size,
        "size": size,
        "items": items,
    }


class TestDataPipeline(unittest.TestCase):
    def test_fetch_paginated_endpoint_multiple_pages(self) -> None:
        """`fetch_paginated_endpoint` should accumulate items across multiple pages."""
        page1 = make_page(1, 2, 2, items=[{"id": 1}, {"id": 2}])
        page2 = make_page(2, 2, 2, items=[{"id": 3}, {"id": 4}])
        responses = [
            Mock(status_code=200, json=Mock(return_value=page1)),
            Mock(status_code=200, json=Mock(return_value=page2)),
        ]
        mock_get = Mock(side_effect=responses)
        with patch("requests.Session.get", mock_get):
            items = fetch_paginated_endpoint("fake_endpoint", base_url="http://test")
            self.assertEqual([item["id"] for item in items], [1, 2, 3, 4])
            self.assertEqual(mock_get.call_count, 2)

    def test_fetch_paginated_endpoint_single_page(self) -> None:
        """`fetch_paginated_endpoint` should handle a single page gracefully."""
        single_page = make_page(1, 1, 2, items=[{"id": 42}, {"id": 43}])
        mock_get = Mock(return_value=Mock(status_code=200, json=Mock(return_value=single_page)))
        with patch("requests.Session.get", mock_get):
            items = fetch_paginated_endpoint("endpoint", base_url="http://test")
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]["id"], 42)
            self.assertEqual(mock_get.call_count, 1)

    def test_save_json(self) -> None:
        """`save_json` should write JSONL with one object per line."""
        records = [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "output.jsonl"
            save_json(records, str(file_path))
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
            self.assertEqual(len(lines), 2)
            objs = [json.loads(line) for line in lines]
            self.assertEqual(objs, records)


if __name__ == "__main__":
    unittest.main()