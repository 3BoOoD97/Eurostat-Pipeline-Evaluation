import sys
import logging

from eurostat_downloader import EurostatDownloader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    # Get dataset name
    if len(sys.argv) < 2:
        logger.error("You must provide a dataset name as an argument!")
        sys.exit(1)

    dataset_name = sys.argv[1]

    logger.info(f"Starting data extraction for dataset: {dataset_name}")

    downloader = EurostatDownloader(dataset_name)
    updated = downloader.run()
    # Keep this as the final output line for Airflow XCom
    print(f"UPDATED={str(updated).lower()}", flush=True)


if __name__ == "__main__":
    main()
