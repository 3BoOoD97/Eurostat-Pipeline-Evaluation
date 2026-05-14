
class DataValidator:
    def __init__(self, df):
        self.df = df
        if df.empty:
            raise ValueError("Transformed DataFrame is empty")

    # Check if required columns exist or not
    def validate_required_columns(self, required_columns):
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(
                f"Required columns: {missing_columns} are missing"
            )

    # Check if there are columns have null values
    def validate_no_nulls_in_columns(self, columns):
        null_columns = [
            col for col in columns
            if col in self.df.columns and self.df[col].isna().any()
        ]
        if null_columns:
            raise ValueError(
                f"The dataset contains null values in columns: {null_columns}"
            )

    # Check if there are negative values in "metric_value" column
    def validate_non_negative_metric(self, metric_column: str = "metric_value"):
        if metric_column in self.df.columns:
            if (self.df[metric_column] < 0).any():
                raise ValueError(
                    f"The dataset contains negative values in '{metric_column}'"
                )

    # To check if time period is in a correct format or not
    def validate_time_period_format(self, column_name: str = "time_period"):
        if column_name not in self.df.columns:
            return

        invalid_values = self.df[
            ~self.df[column_name].astype(str).str.match(r"^\d{4}(-\d{2})?$", na=False)
        ][column_name].unique()

        if len(invalid_values) > 0:
            raise ValueError(
                f" The dataset contains invalid time_period values: {list(invalid_values[:10])}"
            )

    def run_basic_validation(self):
        self.validate_required_columns(["time_period", "metric_value", "country_code"])
        self.validate_no_nulls_in_columns(["time_period", "metric_value", "country_code"])
        self.validate_non_negative_metric("metric_value")
        self.validate_time_period_format("time_period")

    def run(self):
        self.run_basic_validation()
