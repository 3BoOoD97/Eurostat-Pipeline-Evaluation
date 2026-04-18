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

        # Just to test. SHOULD BE DELETED LATER!
        print("TYPES:", type(last_update_eus), type(last_local_date))

        # If there is no local date txt file, it means the data is never downloaded
        # Or the date txt file removed or moved so we need to download the data
        if last_local_date is None:
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
        # Check if the user provided a valid dataset name
        if not self.eus_client.validate_dataset():
            raise Exception("Please provide a valid dataset name")


        try:
            # Fetch latest update date from Eurostat
            eus_last_update_date =  self.eus_client.fetch_last_update_date()

            # Check if local data file exists
            if self.file_manager.data_file_exists():
                # If file exists: Read local saved date and Check needs_update()
                local_last_update_date = self.file_manager.read_last_download_date()
                # Compare the local update date with latest Eurostat update date
                if self.needs_update(eus_last_update_date, local_last_update_date):
                    self.perform_download(eus_last_update_date)
                    print(f"Download {self.dataset_name} Completed and date saved")
                    # if the local date is not older than Eurostat then no need to update
                else:
                    print(f"The data for {self.dataset_name} is already up to date!")
            # If local data file doesn't exist
            else:
                # First time download
                self.perform_download(eus_last_update_date)
                print(f"Download {self.dataset_name} completed and date saved.")

        except Exception as e:
            print(f"Download failed for {self.dataset_name}: {e}")



    def perform_download(self, last_update_date):
        try:
            eu_stream_download = self.eus_client.download_stream()
            # Save the file first
            self.file_manager.save_file(eu_stream_download)
            # Only if saving succeeded, we save the new date
            self.file_manager.save_last_download_date(last_update_date)

            print(f"File for {self.dataset_name} saved successfully.")

        except Exception as e:
            print(f"Error during perform_download for {self.dataset_name}: {e}")
            raise

    def run(self):
        try:
            self.download_dataset()
        except Exception as e:
            print(f"Run failed for dataset '{self.dataset_name}': {e}")



