

class EurostatTransformer:
    def __init__(self, dataset_name):

        self.dataset_name = dataset_name
        input_data_file =f"./output/{dataset_name}/.tsv.gz"
        output_data_file =f"./output/{dataset_name}/.tsv.gz"

