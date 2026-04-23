import sys
from eurostat_downloader import EurostatDownloader


def main():
    # Get dataset name
    if len(sys.argv) < 2:
        print("You must provide a dataset name as an argument!")
        sys.exit(1)

    dataset_name = sys.argv[1]

    print(f"Starting data extraction for dataset: {dataset_name}")

    downloader = EurostatDownloader(dataset_name)
    downloader.run()

if __name__ == "__main__":
    main()
