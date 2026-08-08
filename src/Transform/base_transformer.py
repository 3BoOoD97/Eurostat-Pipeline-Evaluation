import os
import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseEurostatTransformer:
    def __init__(self, dataset_name):
        if not dataset_name or not dataset_name.strip():
            raise ValueError("Eurostat Dataset name should not be empty!")

        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        os.makedirs(os.path.join(self.BASE_DIR, "output", "processed"), exist_ok=True)

        self.dataset_name = dataset_name
        self.input_data_file = os.path.join(self.BASE_DIR, "output", "raw", f"{self.dataset_name}.tsv.gz")

    def get_read_options(self):
        return {
            "sep": "\t",
            "compression": "gzip",
            "dtype": str,
            "keep_default_na": True,
            "na_values": [":", ": ", "–", "-"],
        }
    def raw_file_exists(self):
        return os.path.exists(self.input_data_file)


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

    # Apply specific filters
    def apply_filters(self, df_wide):
        df_clean = df_wide.copy()
        # Include total sex and age only
        if "sex" in df_clean.columns:
             df_clean = df_clean[df_clean["sex"].astype(str).str.strip() == "T"].copy()
        if "age" in df_clean.columns:
            df_clean = df_clean[df_clean["age"].astype(str).str.strip() == "TOTAL"].copy()
            # Remove unwanted aggregate geo codes
        if "geo" in df_clean.columns:
            unwanted = ["EA19", "EA20", "EA", "EU28"]
            geo_clean = df_clean["geo"].astype(str).str.strip()

            df_clean = df_clean[~geo_clean.isin(unwanted)].copy()
        return df_clean

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
        df_long["value_raw"] = df_long["value_raw"].replace(r"^\s*:\s*$", pd.NA, regex=True)
        # Extract numeric values including decimals and convert them from string to numeric
        df_long["metric_value"] = pd.to_numeric(df_long["value_raw"].str.extract(r"(-?\d+\.?\d*)", expand=False), errors="coerce")
        df_long["flag"] = df_long["value_raw"].str.extract(r"([peb])$", expand=False)
        return df_long

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
        if "country_code" in df_clean.columns:
            country_code_clean = (
                df_clean["country_code"]
                .astype(str)
                .str.strip()
            )

            # Save the normalized country code
            df_clean["country_code"] = country_code_clean

            # Retain EU27_2020 and mark it as an aggregate
            df_clean["is_aggregate"] = (
                    country_code_clean == "EU27_2020"
            )
            # Countries dictionary
            country_map = {
                "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
                "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark",
                "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
                "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
                "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
                "LV": "Latvia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway",
                "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SE": "Sweden",
                "SI": "Slovenia", "SK": "Slovakia", "LI": "Liechtenstein", "UK": "United Kingdom", "EU27_2020": "European Union - 27 countries",
            }
            # Create a new column and map the country_code with its name from the dictionary
            df_clean["country_name"] = df_clean["country_code"].map(country_map)
            # Any country doesn't exist in the dictionary in the then save it using its country_code
            df_clean["country_name"] = df_clean["country_name"].fillna(df_clean["country_code"])
        return df_clean