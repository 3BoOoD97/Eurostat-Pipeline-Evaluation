import sys
import logging

from data_transformer import EurostatTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    # Check dataset argument
    if len(sys.argv) < 2:
        logger.error("You must provide a dataset name as an argument!")
        sys.exit(1)

    dataset_name = sys.argv[1]

    logger.info(f"Starting data transformation for dataset: {dataset_name}...")

    transformer = EurostatTransformer(dataset_name)
    transformer.run()

    logger.info("Transform finished successfully")


if __name__ == "__main__":
    main()
