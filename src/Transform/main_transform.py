import sys
from data_transformer import EurostatTransformer


def main():
    # Check dataset argument
    if len(sys.argv) < 2:
        raise ValueError("You must provide a dataset name as an argument")

    dataset_name = sys.argv[1]

    try:
        print(f" Starting data transformation for dataset: {dataset_name}")

        transformer = EurostatTransformer(dataset_name)
        df = transformer.run()

        print("Transform finished successfully")

    except Exception as e:
        print(f"Transform failed: {e}")


if __name__ == "__main__":
    main()