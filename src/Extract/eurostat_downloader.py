import eurostat_client as eurostat_client
import file_manager as file_manager


from dateutil import parser

class EurostatDownloader:
    def __init__(self, dataset_name):

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

    # This function to decide whether dataset needs a new download
    def needs_update(self, eus_date_str, local_date_str):
        last_update_eus = self.parse_date(eus_date_str)
        last_local_date = self.parse_date(local_date_str)

        # If there is no local date txt file, it means the data is never downloaded
        # Or the date txt file removed or moved so we need to download the data
        if last_local_date is None:
            print("No local date txt file was found!")
            return True

        # If failed to fetch the last update date from Eurostat.
        # Then, we need to download the data again in case
        if last_update_eus is None:
            print("Failed to fetch the last update date from Eurostat, the data will be downloaded")
            return True

        # Compare last locally downloaded data date and the date of last modification in Eurostat
        # If the modification data in Eurostat is more recent than the date we have locally.
        # Then, it means our data is outdated and we need to update it so it will return true
        return last_update_eus > last_local_date


    def download_dataset(self):
        if not self.eus_client.validate_dataset():
            raise ValueError(f"Dataset '{self.dataset_name}' was not found in Eurostat")

        try:
            eus_last_update_date = self.eus_client.fetch_last_update_date()

            # If first run
            if not self.file_manager.data_file_exists():
                print(f"First time download for dataset: {self.dataset_name}")
                self.perform_download(eus_last_update_date)
                print(f"Download completed for {self.dataset_name}")
                return True

            else:
                local_last_update_date = self.file_manager.read_last_download_date()

                # If update needed
                if self.needs_update(eus_last_update_date, local_last_update_date):
                    print(f"New update detected for {self.dataset_name}")
                    self.perform_download(eus_last_update_date)
                    print(f"Data updated successfully for {self.dataset_name}")
                    return True

                # If no update
                else:
                    print(f"Data is already up to date for {self.dataset_name}")
                    return False

        except Exception as e:
            print(f" Download failed for {self.dataset_name}: {e}")
            raise


    def perform_download(self, last_update_date):
        try:
            eu_stream_download = self.eus_client.download_stream()
            # Save the file first
            self.file_manager.save_file(eu_stream_download)
            # Only if saving succeeded, we save the new date
            self.file_manager.save_last_download_date(last_update_date)

        except Exception as e:
            print(f"Error during perform_download for {self.dataset_name}: {e}")
            raise

    def run(self):
            return self.download_dataset()




