from .dataset import Dataset


class SupplyDataset(Dataset):
    def __init__(self, file, unique_field):
        super().__init__(file, unique_field)
