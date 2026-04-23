import os
import re
import pandas as pd
from data_validator import DataValidator

class EurostatTransformer:
    def __init__(self, dataset_name):
        # Check if the user didn't provide dataset name
        if not dataset_name or not dataset_name.strip():
            raise ValueError("Eurostat Dataset name should not be empty!")

        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        # Create folders to save processed data if it doesn't exist
        os.makedirs(os.path.join(BASE_DIR, "output", "processed"), exist_ok=True)


        self.dataset_name = dataset_name
        self.input_data_file = os.path.join(BASE_DIR, "output", "raw", f"{self.dataset_name}.tsv.gz")
        self.output_data_file = os.path.join(BASE_DIR, "output", "processed", f"{self.dataset_name}_processed")



    # This function is to check if the raw data file exists
    def raw_file_exists(self):
        return os.path.exists(self.input_data_file)

    # This function is to load raw data into pandas DataFrame
    def read_raw_data(self):
        df_raw = pd.read_csv(
            self.input_data_file,
            sep="\t",
            compression="gzip",
            low_memory=False, # Read the entire file at once using more memory capacity
            na_values=[":", ": ", "–", "-"] #Replace these symbols with Nan
        )
        return df_raw

    # This function is to split the combined Eurostat dimension column into separate columns
    def split_dimension_column(self, df):
        # Identify the name of the first column
        dim_col = df.columns[0]
        # Cut off the name after \. FX, applicant,age,geo\TIME_PERIOD so it cuts TIME_PERIOD
        # Since it is not needed it as a column name.
        dim_part = dim_col.split("\\")[0]
        # Split by comma and clean spaces. FX, applicant,age,geo...
        dim_names = [col.strip() for col in dim_part.split(",")]

        # Split the stacked elements in the entire first column into separate columns
        dims = df[dim_col].astype(str).str.split(",", expand=True)
        # Assign the extracted real names to our new columns
        dims.columns = dim_names

        # Replace the old columns with the new ones we created
        df = pd.concat([dims, df.drop(columns=[dim_col])], axis=1)
        # Clean the extra spaces in headers
        df.columns = df.columns.str.strip()

        return df

    # This function is to check if a column name is a time period or not
    def is_time_column(self, col_name):
        # Get column name without any space
        col_name = str(col_name).strip()

        # Monthly or yearly dates. FX 2008-01 or 2008
        return bool(
            re.fullmatch(r"\d{4}", col_name) or
            re.fullmatch(r"\d{4}-\d{2}", col_name)
        )

    # This function is to convert the time periods from wide format to long format
    def wide_to_long_format(self, df):
        # Extract a list of all time-related columns
        time_cols = [col for col in df.columns if self.is_time_column(col)]
        # Take all columns that are not a time period
        id_vars = [col for col in df.columns if col not in time_cols]

        if not time_cols:
            raise ValueError("No time period columns were detected in the dataset")

        # Put the time periods in a new column called time_period, and the value for each
        # time_period put it in a new column called value_raw
        df_long = df.melt(
            id_vars=id_vars,
            value_vars=time_cols,
            var_name="time_period",
            value_name="value_raw"
        )

        return df_long

    # This function is to clean raw value column and convert it into usable numeric values
    def clean_values(self, df_long):
        # Remove leading and trailing spaces
        df_long["value_raw"] = df_long["value_raw"].astype(str).str.strip()
        # Replace : with NA
        df_long["value_raw"] = df_long["value_raw"].replace(
            r"^\s*:\s*$", pd.NA, regex=True
        )

        # Extract numeric values including decimals and convert them from string to numeric
        df_long["metric_value"] = pd.to_numeric(
            df_long["value_raw"].str.extract(r"(-?\d+\.?\d*)", expand=False),
            errors="coerce"
        )

        # Extract p(Provisional) / e(Estimated) symbols and save them  in a new column called flag
        df_long["flag"] = df_long["value_raw"].str.extract(r"([pe])$", expand=False)

        return df_long

    # Apply specific filters
    def apply_filters(self, df_long):
        df_clean = df_long.copy()

        # Include total sex and age only
        if "sex" in df_clean.columns:
            df_clean = df_clean[df_clean["sex"].astype(str).str.strip() == "T"].copy()

        if "age" in df_clean.columns:
            df_clean = df_clean[df_clean["age"].astype(str).str.strip() == "TOTAL"].copy()

        # Remove unwanted aggregate geo codes
        if "geo" in df_clean.columns:
            unwanted_country_codes = ["EA19", "EA20", "EA", "EU28"]
            df_clean = df_clean[~df_clean["geo"].isin(unwanted_country_codes)].copy()

        # Remove rows with missing numeric values
        df_clean = df_clean.dropna(subset=["metric_value"]).copy()

        return df_clean

    # This function is to rename columns to more clear and descriptive names.
    def rename_columns(self, df_clean):
        rename_map = {}

        if "geo" in df_clean.columns:
            rename_map["geo"] = "country_code"
        if "citizen" in df_clean.columns:
            rename_map["citizen"] = "nationality_code"
        if "applicant" in df_clean.columns:
            rename_map["applicant"] = "applicant_type"
        if "age" in df_clean.columns:
            rename_map["age"] = "age_group"

        df_clean = df_clean.rename(columns=rename_map)
        return df_clean

    # This function translates short country codes into full names and marks EU totals.
    def add_derived_columns(self, df_clean):
        # If country_code = EU27_2020 then is_aggregate = true to analysis the data easily later
        if "country_code" in df_clean.columns:
            df_clean["is_aggregate"] = df_clean["country_code"].isin(["EU27_2020"])

            # Countries dictionary
            country_map = {
                "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
                "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark",
                "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
                "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
                "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
                "LV": "Latvia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway",
                "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SE": "Sweden",
                "SI": "Slovenia", "SK": "Slovakia", "LI": "Liechtenstein",
                "UK": "United Kingdom"
            }
            # Create a new column and map the country_code with its name from the dictionary
            df_clean["country_name"] = df_clean["country_code"].map(country_map)
            # Any country doesn't exist in the dictionary in the then save it using its  country_code
            df_clean["country_name"] = df_clean["country_name"].fillna(df_clean["country_code"])

        return df_clean


    # This function saves the data
    def save_transformed_data(self, df):
        try:
            df.to_csv(f"{self.output_data_file}.csv", index=False)
            df.to_parquet(f"{self.output_data_file}.parquet", index=False)
        except Exception as e:
            raise IOError(f"Failed to save transformed data: {e}")



    def run(self) -> pd.DataFrame:
        # Make sure the raw data file exists
        if not self.raw_file_exists():
            raise FileNotFoundError(f"Raw input file not found: {self.input_data_file}")
        # 1- Read raw data file and save it as a pandas df
        df_raw = self.read_raw_data()
        # 2- Split the df combined columns into separate columns
        df_split = self.split_dimension_column(df_raw)
        # 3- Reshape the time periods from wide format to long format
        df_long = self.wide_to_long_format(df_split)
        # 4- Clean raw value column and convert it into usable numeric values
        df_cleaned = self.clean_values(df_long)
        # 5- Apply specific filters
        df_filtered = self.apply_filters(df_cleaned)
        # 6- Rename columns to more clear and descriptive names.
        df_renamed = self.rename_columns(df_filtered)
        # 7- Add derived columns and map the country code with its name
        df_final = self.add_derived_columns(df_renamed)
        # 8- Validate the final dataset (check for empty data and required columns)
        validator = DataValidator(df_final)
        validator.run()
        # Save the data
        self.save_transformed_data(df_final)

        print(f"Saved files:")
        print(f"- {self.output_data_file}.csv")
        print(f"- {self.output_data_file}.parquet")

        return df_final

