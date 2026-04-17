
import os
import pytest
from unittest.mock import Mock
from src.Extract.file_manager import FileManager


# ===== Constructor tests ======
def test_init_valid_dataset():
    manager = FileManager("test_9_cpa")

    assert manager.dataset_name == "test_9_cpa"
    assert manager.output_gz_data_path.endswith("test_9_cpa.tsv.gz")
    assert manager.last_download_file_date.endswith("test_9_cpa.txt")


def test_init_empty_dataset():
    with pytest.raises(ValueError):
        FileManager("")