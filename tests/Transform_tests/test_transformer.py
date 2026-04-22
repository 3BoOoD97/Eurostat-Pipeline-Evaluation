import unittest
import pandas as pd
from src.Transform.data_transformer import EurostatTransformer


class TestEurostatTransformer(unittest.TestCase):

    def setUp(self):
        self.transformer = EurostatTransformer("test_dataset")

    # Split_dimension_column test
    def test_split_dimension_column(self):
        df = pd.DataFrame({
            "freq,unit,geo\\TIME_PERIOD": ["A,PER,SE", "A,PER,DE"],
            "2008": [1, 2]
        })

        result = self.transformer.split_dimension_column(df)

        self.assertIn("freq", result.columns)
        self.assertIn("unit", result.columns)
        self.assertIn("geo", result.columns)

    #  Detect time columns test
    def test_is_time_column(self):
        self.assertTrue(self.transformer.is_time_column("2008"))
        self.assertTrue(self.transformer.is_time_column("2008-01"))
        self.assertFalse(self.transformer.is_time_column("geo"))

    # Wide_to_long_format test
    def test_wide_to_long_format(self):
        df = pd.DataFrame({
            "geo": ["SE"],
            "2008": [10],
            "2009": [20]
        })

        result = self.transformer.wide_to_long_format(df)

        self.assertIn("time_period", result.columns)
        self.assertIn("value_raw", result.columns)
        self.assertEqual(len(result), 2)

    # Clean_values test
    def test_clean_values(self):
        df = pd.DataFrame({
            "value_raw": ["10", "20 p", ":"]
        })

        result = self.transformer.clean_values(df)

        self.assertEqual(result["metric_value"].iloc[0], 10)
        self.assertEqual(result["metric_value"].iloc[1], 20)
        self.assertTrue(pd.isna(result["metric_value"].iloc[2]))

    # Filters test
    def test_apply_filters(self):
        df = pd.DataFrame({
            "sex": ["T", "M"],
            "age": ["TOTAL", "TOTAL"],
            "geo": ["SE", "SE"],
            "metric_value": [10, 20]
        })

        result = self.transformer.apply_filters(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["sex"], "T")

    # Rename_columns test
    def test_rename_columns(self):
        df = pd.DataFrame({
            "geo": ["SE"],
            "citizen": ["AD"],
            "applicant": ["FRST"],
            "age": ["TOTAL"]
        })

        result = self.transformer.rename_columns(df)

        self.assertIn("country_code", result.columns)
        self.assertIn("nationality_code", result.columns)
        self.assertIn("applicant_type", result.columns)
        self.assertIn("age_group", result.columns)

    # Derived columns test
    def test_add_derived_columns(self):
        df = pd.DataFrame({
            "country_code": ["SE", "EU27_2020"]
        })

        result = self.transformer.add_derived_columns(df)

        self.assertIn("country_name", result.columns)
        self.assertIn("is_aggregate", result.columns)
        self.assertTrue(result[result["country_code"] == "EU27_2020"]["is_aggregate"].iloc[0])

    # Validation success test
    def test_validate_success(self):
        df = pd.DataFrame({
            "country_code": ["SE"],
            "time_period": ["2008"],
            "metric_value": [10]
        })

        self.transformer.validate_transformed_data(df)  # should NOT raise

    # Validation fail (empty) test
    def test_validate_empty(self):
        df = pd.DataFrame()

        with self.assertRaises(ValueError):
            self.transformer.validate_transformed_data(df)

    # Validation fail missing column test
    def test_validate_missing_column(self):
        df = pd.DataFrame({
            "country_code": ["SE"]
        })

        with self.assertRaises(ValueError):
            self.transformer.validate_transformed_data(df)


if __name__ == "__main__":
    unittest.main()