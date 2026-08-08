import sys
import logging
import time
from transformer_in_memory import EurostatMemoryTransformer

#
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        logger.error(" You must provide a dataset name as an argument!")
        sys.exit(1)

    dataset_name = sys.argv[1]

    logger.info(f" Starting IN-MEMORY data transformation for dataset: {dataset_name}...")

    try:
        # Start counter
        start_time = time.perf_counter()
        # Call In Memory class
        transformer = EurostatMemoryTransformer(dataset_name)
        transformer.run()

        # End counter
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        logger.info("In-Memory transform script finished!")

        # Print the result
        logger.info(f" [IN MEMORY] Total Execution Time: {execution_time:.4f} seconds ({execution_time / 60:.2f} minutes)")
        print("=" * 60, flush=True)
      #  print(f" [IN-MEMORY] Total Execution Time: {execution_time:.4f} seconds ({execution_time / 60:.2f} min)",
        #      flush=True)
        #print("=" * 60, flush=True)

    except Exception as e:
        logger.exception(f" Obs! Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()