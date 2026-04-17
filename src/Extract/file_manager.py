import os
import gzip

class FileManager:
    def __init__(self, dataset_name: str = None):
        if not dataset_name or not dataset_name.strip():
            raise ValueError("Dataset name should not be empty!!")

        # Create folders to save the data and date if they don't exist
        os.makedirs("./output/last_download_date", exist_ok=True)

        self.dataset_name = dataset_name
        self.output_gz_data_path = os.path.join("./output", f"{self.dataset_name}.tsv.gz")
        self.last_download_file_date = f"./output/last_download_date/{self.dataset_name}.txt"

    # This function checks if the data file exists locally or not
    def data_file_exists(self):
        return os.path.exists(self.output_gz_data_path)

    # This function saves the stream coming from Eurostat locally as a .gz file.
    def save_file(self, stream):
        try:
            # Prepare the file to write the data in binary access mode
            with open(self.output_gz_data_path, "wb") as f:
                # Start the download process, as chunks, each one has a size of 1MB
                for chunk in stream.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        # Catch general exceptions
        except Exception as e:
            raise IOError(f"Error saving file: {e}")
        # Make sure the data file exists locally
        if not self.data_file_exists():
            raise FileNotFoundError("Data file was not created")
        # Make sure the data file is not empty
        if self.get_data_file_size_mb() == 0:
            raise ValueError("Downloaded data file is empty")

    # This function returns the size of the local data file in MB if it exists
    def get_data_file_size_mb(self):
        if not self.data_file_exists():
            return 0
        return  os.path.getsize(self.output_gz_data_path) / (1024 * 1024)


    def save_last_date(self, date):
        pass

    def read_last_date(self):
        pass