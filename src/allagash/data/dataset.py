import pandas as pd


class Dataset:
    def __init__(self, dataframe: pd.DataFrame, name: str, unique_field: str):
        self.df = dataframe
        self.unique_field = unique_field
        self.name = name
