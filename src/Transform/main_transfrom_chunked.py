import sys
import logging
import time
from transformer_chunked import EurostatChunkedTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        logger.error("You must provide a dataset name as an argument!")
        sys.exit(1)

    dataset_name = sys.argv[1]
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50000

    logger.info(f" Starting CHUNKED streaming transformation for dataset: {dataset_name} (Chunk size: {chunk_size})...")

    try:
        # Start counter
        start_time = time.perf_counter()

        # Call the Chunked class
        transformer = EurostatChunkedTransformer(dataset_name, chunk_size=chunk_size)
        transformer.run()

        # End counter
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        logger.info("Chunked streaming transform finished!")

        # Print the result
        print("=" * 60, flush=True)
        print(f"[CHUNKED] Total Execution Time: {execution_time:.4f} seconds ({execution_time / 60:.2f} min)",
              flush=True)
        print("=" * 60, flush=True)

    except Exception as e:
        logger.exception(f" Obs! Pipeline failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()