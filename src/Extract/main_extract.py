import sys
from eurostat_downloader import EurostatDownloader


def main():
    # Get dataset name
    if len(sys.argv) < 2:
        raise ValueError("You must provide a dataset name as an argument")

    dataset_name = sys.argv[1]

    downloader = EurostatDownloader(dataset_name)
    downloader.run()


if __name__ == "__main__":
    main()
