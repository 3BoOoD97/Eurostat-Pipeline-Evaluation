import os
import time
import pandas as pd
import logging
import resource
from base_transformer import BaseEurostatTransformer
from data_validator import DataValidator

logger = logging.getLogger(__name__)


class EurostatMemoryTransformer(BaseEurostatTransformer):
    def __init__(self, dataset_name):
        super().__init__(dataset_name)
        self.output_data_file = os.path.join(self.BASE_DIR, "output", "processed", f"{self.dataset_name}_processed")

    # Unzip gzip raw data, read it as TSV, replace symbols to NaN
    def read_raw_data(self):
        return pd.read_csv(
            self.input_data_file,
            **self.get_read_options(),
        )

    def save_transformed_data(self, df):
        df.to_parquet(
            f"{self.output_data_file}.parquet",
            index=False,
            compression="snappy",
        )

    def run(self) -> pd.DataFrame:
        logger.info("***** Starting In-Memory Pipeline...")

        total_start_counter = time.perf_counter()

        if not self.raw_file_exists():
            raise FileNotFoundError(f"File not found: {self.input_data_file}")

        ### 1- Calculate Reading time
        read_start_counter = time.perf_counter()
        df_raw = self.read_raw_data()
        read_time = time.perf_counter() - read_start_counter
        logger.info(f" Disk Read I/O finished in: {read_time:.4f} sec")

        ### 2- Calculate Processing time
        processing_start_counter = time.perf_counter()

        df_work = self.split_dimension_column(df_raw)
        del df_raw

        df_work = self.apply_filters(df_work)
        df_work = self.wide_to_long_format(df_work)
        df_work = self.clean_values(df_work)

        df_work = df_work.dropna(
            subset=["metric_value"]
        ).copy()

        df_work = self.rename_columns(df_work)
        df_final = self.add_derived_columns(df_work)

        del df_work

        processing_time = (
                time.perf_counter()
                - processing_start_counter
        )
        logger.info(f"Processing finished in: {processing_time:.4f} sec")

        ### 3- Calculate Validation time
        validation_start_counter = time.perf_counter()
        DataValidator(df_final).run()
        validation_time = time.perf_counter() - validation_start_counter
        logger.info(f"Data Validation finished in: {validation_time:.4f} sec")

        ### 4- Calculate Write I/O time
        write_start_counter = time.perf_counter()
        self.save_transformed_data(df_final)
        write_time = time.perf_counter() - write_start_counter
        logger.info(f" Disk Write I/O finished in: {write_time:.4f} sec")

        ### 5- Calculate the total time
        total_time = time.perf_counter() - total_start_counter

        #Print the final total rows
        print(f"Total Rows   : {len(df_final)}", flush=True)

        ### Special printing for the THESIS
        print("=" * 75, flush=True)
        print("*******[THESIS PRINTING: IN-MEMORY ]*******", flush=True)
        print("=" * 75, flush=True)
        print(f"1- Disk Read I/O Time    : {read_time:8.4f} sec  ({(read_time/total_time)*100:5.1f}%)", flush=True)
        print(f"2- Data Processing Time   : {processing_time:8.4f} sec  ({(processing_time/total_time)*100:5.1f}%) [Core Processing Metric]", flush=True)
        print(f"3- Data Validation Time  : {validation_time:8.4f} sec  ({(validation_time/total_time)*100:5.1f}%)  [Single Batch Validation]", flush=True)
        print(f"4- Disk Write I/O Time   : {write_time:8.4f} sec  ({(write_time/total_time)*100:5.1f}%)", flush=True)
        print("-" * 75, flush=True)
        print(f"TOTAL TIME   : {total_time:8.4f} sec  ({total_time/60:.2f} min)", flush=True)
        print("=" * 75, flush=True)


        peak_memory_mb = (
                resource.getrusage(
                    resource.RUSAGE_SELF
                ).ru_maxrss / 1024
        )
        print(
            f"Peak Memory Usage : "
            f"{peak_memory_mb:.2f} MB",
            flush=True,
        )
        return df_final