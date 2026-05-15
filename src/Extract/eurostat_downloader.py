import eurostat_client as eurostat_client
import file_manager as file_manager
from dateutil import parser
import logging

logger = logging.getLogger(__name__)


class EurostatDownloader:
    def __init__(self, dataset_name):
        # Initialize values
        self.dataset_name = dataset_name
        self.eus_client = eurostat_client.EurostatClient(self.dataset_name)
        self.file_manager = file_manager.FileManager(self.dataset_name)

    # Function to convert string date into datetime
    def parse_date(self, date_str):
        try:
            if date_str is None:
                return None
            return parser.parse(date_str)
        except Exception:
            return None

    # This function to decide whether dataset needs an update or not
    def needs_update(self, eus_date_str, local_date_str):
        last_update_eus = self.parse_date(eus_date_str)
        last_local_date = self.parse_date(local_date_str)

        # If there is no local date txt file exists return true
        if last_local_date is None:
            logger.info("No local date txt file was found!")
            return True

        # If failed to fetch the last update date from Eurostat metadata return true.
        if last_update_eus is None:
            logger.warning("Failed to fetch the last update date from Eurostat, the data will be downloaded")
            return True

        # Compare if the last update data in Eurostat is more recent than the local.
        return last_update_eus > last_local_date

    # This function is responsible to call other functions and download the dataset and check updates
    def download_dataset(self):
        if not self.eus_client.validate_dataset():
            raise ValueError(f"Dataset '{self.dataset_name}' was not found in Eurostat")

        try:
            eus_last_update_date = self.eus_client.fetch_last_update_date()

            # If first run
            if not self.file_manager.data_file_exists():
                logger.info(f"First time download for dataset: {self.dataset_name}")
                self.perform_download(eus_last_update_date)
                logger.info(f"Download completed for {self.dataset_name}")
                return True

            else:
                local_last_update_date = self.file_manager.read_last_download_date()

                # If update needed
                if self.needs_update(eus_last_update_date, local_last_update_date):
                    logger.info(f"New update detected for {self.dataset_name}")
                    self.perform_download(eus_last_update_date)
                    logger.info(f"Data updated successfully for {self.dataset_name}")
                    return True

                # If no update
                else:
                    logger.info(f"Data is already up to date for {self.dataset_name}")
                    return False

        except Exception as e:
            logger.exception(f" Download failed for {self.dataset_name}")
            raise

    def perform_download(self, last_update_date):
        try:
            eu_stream_download = self.eus_client.download_stream()
            # Save the file
            self.file_manager.save_file(eu_stream_download)
            # Only if saving succeeded, we save the new date
            self.file_manager.save_last_download_date(last_update_date)

        except Exception as e:
            logger.exception(f"Error during perform_download for dataset: {self.dataset_name}")
            raise

    def run(self):
        return self.download_dataset()
