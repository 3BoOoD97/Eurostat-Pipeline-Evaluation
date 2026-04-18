import sys
from pathlib import Path
import unittest

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "Extract"))

from Extract.eurostat_downloader import EurostatDownloader
from Extract.file_manager import FileManager


class TestEurostatDownloader(unittest.TestCase):

    def setUp(self):
        self.valid_dataset = "migr_asyappctza"
        self.invalid_dataset = "invalid_dataset"

        self.valid_file_manager = FileManager(self.valid_dataset)
        self.invalid_file_manager = FileManager(self.invalid_dataset)

        # Clean old dataset
        if self.valid_file_manager.data_file_exists():
            self.valid_file_manager.output_gz_data_path.unlink() if hasattr(self.valid_file_manager.output_gz_data_path, "unlink") else None

        if Path(self.valid_file_manager.output_gz_data_path).exists():
            Path(self.valid_file_manager.output_gz_data_path).unlink()

        if Path(self.valid_file_manager.last_download_file_date).exists():
            Path(self.valid_file_manager.last_download_file_date).unlink()

    def test_valid_dataset_first_download(self):
        downloader = EurostatDownloader(self.valid_dataset)

        downloader.run()

        self.assertTrue(
            self.valid_file_manager.data_file_exists(),
            "Data file should exist after first download"
        )
        self.assertTrue(
            Path(self.valid_file_manager.last_download_file_date).exists(),
            "Last download date file should exist after first download"
        )
        self.assertGreater(
            self.valid_file_manager.get_data_file_size_mb(),
            0,
            "Downloaded file should not be empty"
        )

    def test_valid_dataset_already_up_to_date(self):
        downloader = EurostatDownloader(self.valid_dataset)

        # First run to download the data
        downloader.run()

        first_size = self.valid_file_manager.get_data_file_size_mb()
        first_date = self.valid_file_manager.read_last_download_date()

        # After we have the data already exists it should compare date and decide if we need to update the data
        downloader.run()

        second_size = self.valid_file_manager.get_data_file_size_mb()
        second_date = self.valid_file_manager.read_last_download_date()

        self.assertEqual(first_size, second_size, "File size should remain unchanged")
        self.assertEqual(first_date, second_date, "Saved update date should remain unchanged")

    def test_invalid_dataset_raises_exception(self):
        downloader = EurostatDownloader(self.invalid_dataset)

        with self.assertRaises(Exception):
            downloader.download_dataset()


if __name__ == "__main__":
    unittest.main(verbosity=2)