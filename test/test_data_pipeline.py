import os
import json
import pytest
from data_pipelines import daily_pipeline

@pytest.fixture
def setup_and_cleanup():
    # Run the pipeline
    daily_pipeline.fetch_and_store_data()
    yield
    # Cleanup
    for file in os.listdir(daily_pipeline.OUTPUT_DIR):
        if file.endswith(".json"):
            os.remove(os.path.join(daily_pipeline.OUTPUT_DIR, file))

def test_pipeline_creates_json_files(setup_and_cleanup):
    files = os.listdir(daily_pipeline.OUTPUT_DIR)
    assert len(files) == 3

def test_json_files_are_valid(setup_and_cleanup):
    for file in os.listdir(daily_pipeline.OUTPUT_DIR):
        if file.endswith(".json"):
            with open(os.path.join(daily_pipeline.OUTPUT_DIR, file)) as f:
                data = json.load(f)
                assert "items" in data
                assert isinstance(data["items"], list)
