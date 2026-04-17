
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

# ===== data_file_exists tests ======
# TEST FAILED NEEDS
def test_data_file_exists_false():
    manager = FileManager("test_dataset2")
    assert manager.data_file_exists() is False

# ===== save_data_file tests ======
def test_save_file_success():
    manager = FileManager("test_dataset")
    mock_stream = Mock()
    mock_stream.iter_content.return_value = [b"abc", b"123"]

    manager.save_file(mock_stream)

    assert manager.data_file_exists() is True
    assert manager.get_data_file_size_mb() > 0


# ===== save_last_download_date tests ======
def test_save_last_download_date():
    manager = FileManager("date_test")
    manager.save_last_download_date("2026-04-18T12:00:00+0200")
    assert os.path.exists(manager.last_download_file_date)

# ===== read_last_download_date tests ======
def test_read_last_download_date():
    manager = FileManager("read_test")
    manager.save_last_download_date("2026-04-18")
    result = manager.read_last_download_date()
    assert result == "2026-04-18"



