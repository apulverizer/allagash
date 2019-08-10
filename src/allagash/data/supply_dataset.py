from .dataset import Dataset
import pandas as pd


class SupplyDataset(Dataset):
    def __init__(self, dataframe: pd.DataFrame, name: str, unique_field: str):
        super().__init__(dataframe, name, unique_field)
