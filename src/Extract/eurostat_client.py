import requests
import time


class EurostatClient:
    def __init__(self, dataset_name: str = None):
        # Check if dataset name provided is empty or null
        if not dataset_name or not dataset_name.strip():
            raise ValueError("Dataset name should not be empty!!")

        # Assign dataset name for reuse across API calls
        self.dataset_name = dataset_name
        # To retrieve the latest metadata and check for the latest update
        self.metadata_url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/ESTAT/{dataset_name}?format=JSON"
        # To download the data in TSV.gz format
        self.data_url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/{dataset_name}/1.0?compress=true&format=tsv"

    # This function is just to make sure that the dataset exists in Eurostat
    def validate_dataset(self):
        try:
            # Send GET req to metadata_url
            response = requests.get(self.metadata_url, timeout=10)
            # Check what kind of res we got
            response.raise_for_status()
            # If the res was 200 then the data exists and we return true
            return True
        # If the res was anything but not 200 then catch the exception
        except requests.exceptions.HTTPError as e:
            # If the exception = 404 it means the data doesn't exist so it returns false
            if e.response is not None and e.response.status_code == 404:
                return False
            # For any other HTTP error, re-raise the exception
            raise
        # Catch any other unexpected errors, return False because we cannot confirm the dataset exists
        except Exception as e:
            raise ConnectionError(f"Failed to validate dataset due to connection issue: {e}")

    # This function is to fetch the last update date for the selected dataset
    def fetch_last_update_date(self):
        # Try connection for 3 times
        for i in range(3):
            try:
                # Send GET req to metadata_url
                response = requests.get(self.metadata_url, timeout=30)
                # Check what kind of res we got
                response.raise_for_status()
                # Convert res to JSON format
                data = response.json()
                # Extract the list of annotations
                annotations = data.get('extension', {}).get('annotation', [])

                last_update = None

                # Loop on every element in the list
                for item in annotations:
                    # if the element is dic and the type = 'UPDATE_DATA' then save the date and break
                    if isinstance(item, dict) and item.get('type') == 'UPDATE_DATA':
                        last_update = item.get('date')
                        break
                return last_update
            # If any error happened
            except Exception as e:
                print(f"Download attempt: {i + 1} Failed {e}")
        # If the connection failed in the 3 times throw an exception
        raise Exception("Connection failed after 3 attempts")


    # Attempting to download the Dataset data from Eurostat as a stream
    def download_stream(self):
        # Try connection for 3 times
        for i in range(3):
            try:
                # Send a get req to download the data stream=True to not load the entire file into memory at once.
                # But  loading the data in batches (chunks).
                response = requests.get(self.data_url, stream=True, timeout=120)
                # Check what kind of res we got and return it if it was 2xx otherwise throw exception
                response.raise_for_status()
                return response
            # Catch errors while trying to download the data
            except Exception as e:
                print(f" Download attempt: {i + 1} Failed {e}")
                # Sleep 2 sec to give the server a better chance
                time.sleep(2)
        # If the connection failed in the 3 times throw an exception
        raise ConnectionError("Data loading failed!")










