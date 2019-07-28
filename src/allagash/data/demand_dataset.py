from .dataset import Dataset


class DemandDataset(Dataset):
    def __init__(self, file, unique_field, demand_field):
        super().__init__(file, unique_field)
        self._demand_field = demand_field
