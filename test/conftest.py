import pytest
import tempfile
import os
import shutil

@pytest.fixture
def temp_data_dir():
    """Fixture qui crée un dossier temporaire pour les fichiers de test."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)