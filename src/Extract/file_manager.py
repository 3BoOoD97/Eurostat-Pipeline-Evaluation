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

    # This function check if the data file exists locally or not
    def data_file_exists(self):
        return os.path.exists(self.output_gz_data_path)


    def save_file(self, stream):
        pass

    def get_file_size(self):
        pass

    def save_last_date(self, date):
        pass

    def read_last_date(self):
        pass