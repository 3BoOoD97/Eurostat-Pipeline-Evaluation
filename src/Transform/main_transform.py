import sys
from data_transformer import EurostatTransformer


def main():
    # Check dataset argument
    if len(sys.argv) < 2:
        print("You must provide a dataset name as an argument!")
        sys.exit(1)

    dataset_name = sys.argv[1]

    print(f" Starting data transformation for dataset: {dataset_name}")

    transformer = EurostatTransformer(dataset_name)
    transformer.run()

    print("Transform finished successfully")

if __name__ == "__main__":
    main()