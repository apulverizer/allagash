import random
import string
import pandas as pd


class Coverage:
    def __init__(
        self,
        dataframe,
        demand_col=None,
        demand_name=None,
        supply_name=None,
        coverage_type="binary",
    ):
        """
        An object that stores the relationship between a set of demand locations and a set of supply locations.
        Use this initializer if the coverage matrix has already been created, otherwise this can be created from two
        geodataframes using the :meth:`~allagash.coverage.Coverage.from_geodataframes` or
        :meth:`~allagash.coverage.Coverage.from_spatially_enabled_dataframes` factory methods.

        .. code-block:: python

            Coverage.from_geodataframes(df1, df2, "Demand_Id", "Supply_Id")

        :param ~pandas.DataFrame dataframe: A dataframe containing a matrix of demand (rows) and supply (columns).
                                        An additional column containing the demand values can optionally be provided.
        :param str demand_col: (optional) The name of the column storing the demand value.
        :param str demand_name: (optional) The name of the demand to use. If not supplied, a random name is generated.
        :param str supply_name: (optional) The name of the supply to use. If not supplied, a random name is generated.
        :param str coverage_type: (optional) The type of coverage this represents (optional). If not supplied, the default is
                                  "binary". Options are "binary" and "partial".
        """
        self._validate_init(
            coverage_type, dataframe, demand_col, demand_name, supply_name
        )
        self._demand_col = demand_col
        self._dataframe = dataframe
        if not demand_name:
            self._demand_name = "".join(random.choices(string.ascii_uppercase, k=6))
        else:
            self._demand_name = demand_name
        if not supply_name:
            self._supply_name = "".join(random.choices(string.ascii_uppercase, k=6))
        else:
            self._supply_name = supply_name
        self._coverage_type = coverage_type.lower()

    @staticmethod
    def _validate_init(coverage_type, dataframe, demand_col, demand_name, supply_name):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                f"Expected 'Dataframe' type for dataframe, got '{type(dataframe)}'"
            )
        if not isinstance(demand_col, str) and demand_col is not None:
            raise TypeError(
                f"Expected 'str' type for demand_col, got '{type(demand_col)}'"
            )
        if not isinstance(demand_name, str) and demand_name is not None:
            raise TypeError(
                f"Expected 'str' type for demand_name, got '{type(demand_name)}'"
            )
        if not isinstance(supply_name, str) and supply_name is not None:
            raise TypeError(
                f"Expected 'str' type for supply_name, got '{type(supply_name)}'"
            )
        if not isinstance(coverage_type, str):
            raise TypeError(
                f"Expected 'str' type for coverage_type, got '{type(coverage_type)}'"
            )
        if demand_col and demand_col not in dataframe.columns:
            raise ValueError(f"'{demand_col}' not in dataframe")
        if coverage_type.lower() not in ("binary", "partial"):
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        if coverage_type.lower() == "partial" and demand_col is None:
            raise ValueError(
                "'demand_col' is required when generating partial coverage"
            )

    @property
    def df(self):
        """

        :return: The geodataframe the dataset is based on
        :rtype: ~geopandas.GeoDataFrame
        """
        return self._dataframe

    @property
    def demand_name(self):
        """

        :return: The name of the demand
        :rtype: str
        """
        return self._demand_name

    @property
    def supply_name(self):
        """

        :return: The name of the supply
        :rtype: str
        """
        return self._supply_name

    @property
    def coverage_type(self):
        """

        :return: The type of coverage
        :rtype: str
        """
        return self._coverage_type

    @property
    def demand_col(self):
        """

        :return: The name of the demand column in the underlying dataframe
        :rtype: str or None
        """
        return self._demand_col

    @classmethod
    def from_geodataframes(
        cls,
        demand_df,
        supply_df,
        demand_id_col,
        supply_id_col,
        demand_name=None,
        supply_name=None,
        demand_col=None,
        coverage_type="binary",
    ):
        """
        Creates a new Coverage from two GeoDataFrames representing the demand and supply locations. The coverage
        is determined by intersecting the two dataframes.

        :param ~geopandas.GeoDataFrame demand_df: The GeoDataFrame containing the demand locations
        :param ~geopandas.GeoDataFrame supply_df: The GeoDataFrame containing the supply locations
        :param str demand_id_col: The name of the column that has unique identifiers for the demand locations
        :param str supply_id_col: The name of the column that has unique identifiers for the supply locations
        :param str demand_name: (optional) The name of the demand to use. If not supplied, a random name is generated.
        :param str supply_name: (optional) The name of the supply to use. If not supplied, a random name is generated.
        :param str demand_col: (optional) The name of the column that stores the amount of demand for the demand
                                          locations. Required if generating partial coverage.
        :param str coverage_type: (optional) The type of coverage this represents. If not supplied, the default is
                                  "binary". Options are "binary" and "partial".

        :return: The coverage
        :rtype: ~allagash.coverage.Coverage
        """
        cls._validate_from_geodataframes(
            coverage_type,
            demand_col,
            demand_df,
            demand_id_col,
            demand_name,
            supply_df,
            supply_id_col,
        )

        data = []
        if coverage_type.lower() == "binary":
            for index, row in demand_df.iterrows():
                contains = supply_df.geometry.contains(row.geometry).tolist()
                if demand_col:
                    contains.insert(0, row[demand_col])
                data.append(contains)
        elif coverage_type.lower() == "partial":
            for index, row in demand_df.iterrows():
                demand_area = row.geometry.area
                intersection_area = supply_df.geometry.intersection(
                    row.geometry
                ).geometry.area
                partial_coverage = (
                    (intersection_area / demand_area) * row[demand_col]
                ).tolist()
                if demand_col:
                    partial_coverage.insert(0, row[demand_col])
                data.append(partial_coverage)
        else:
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        columns = supply_df[supply_id_col].tolist()
        if demand_col:
            columns.insert(0, demand_col)
        df = pd.DataFrame.from_records(
            data, index=demand_df[demand_id_col], columns=columns
        )
        return Coverage(
            df,
            demand_col=demand_col,
            demand_name=demand_name,
            supply_name=supply_name,
            coverage_type=coverage_type,
        )

    @classmethod
    def from_spatially_enabled_dataframes(
        cls,
        demand_df,
        supply_df,
        demand_id_col,
        supply_id_col,
        demand_name=None,
        supply_name=None,
        demand_col=None,
        coverage_type="binary",
        demand_geometry_col="SHAPE",
        supply_geometry_col="SHAPE",
    ):
        """
        Creates a new Coverage from two spatially enabled (arcgis) dataframes representing the demand and supply locations.
        The coverage is determined by intersecting the two dataframes.

        :param ~pandas.DataFrame demand_df: The spatially enabled dataframe containing the demand locations
        :param ~pandas.DataFrame supply_df: The spatially enavled dataframe containing the supply locations
        :param str demand_id_col: The name of the column that has unique identifiers for the demand locations
        :param str supply_id_col: The name of the column that has unique identifiers for the supply locations
        :param str demand_name: (optional) The name of the demand to use. If not supplied, a random name is generated.
        :param str supply_name: (optional) The name of the supply to use. If not supplied, a random name is generated.
        :param str demand_col: (optional) The name of the column that stores the amount of demand for the demand
                                          locations. Required if generating partial coverage.
        :param str coverage_type: (optional) The type of coverage this represents. If not supplied, the default is
                                  "binary". Options are "binary" and "partial".
        :param str demand_geometry_col: (optional) The name of the field storing the geometry in the demand dataframe.
                                        If not supplied, the default is "SHAPE".
        :param str supply_geometry_col: (optional) The name of the field storing the geometry in the supply dataframe.
                                        If not supplied, the default is "SHAPE".
        :return: The coverage
        :rtype: ~allagash.coverage.Coverage
        """

        cls._validate_from_spatially_enabled_dataframes(
            coverage_type,
            demand_col,
            demand_df,
            demand_id_col,
            demand_name,
            supply_df,
            supply_id_col,
            demand_geometry_col,
            supply_geometry_col,
        )
        data = []
        if coverage_type.lower() == "binary":
            for index, row in demand_df.iterrows():
                contains = (
                    supply_df[supply_geometry_col]
                    .geom.contains(row[demand_geometry_col])
                    .tolist()
                )
                if demand_col:
                    contains.insert(0, row[demand_col])
                data.append(contains)
        elif coverage_type.lower() == "partial":
            for index, row in demand_df.iterrows():
                partial_coverage = []
                demand_area = row[demand_geometry_col].area
                # Cannot vectorize this because if the intersection returns an empty polygon with rings
                # The conversion to shapely fails when trying to get the area
                for _, s_row in supply_df.iterrows():
                    intersection = s_row[supply_geometry_col].intersect(
                        row[demand_geometry_col]
                    )
                    area = intersection.area if not intersection.is_empty else 0
                    partial_coverage.append((area / demand_area) * row[demand_col])
                if demand_col:
                    partial_coverage.insert(0, row[demand_col])
                data.append(partial_coverage)
        else:
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        columns = supply_df[supply_id_col].tolist()
        if demand_col:
            columns.insert(0, demand_col)
        df = pd.DataFrame.from_records(
            data, index=demand_df[demand_id_col], columns=columns
        )
        return Coverage(
            df,
            demand_col=demand_col,
            demand_name=demand_name,
            supply_name=supply_name,
            coverage_type=coverage_type,
        )

    @classmethod
    def _validate_from_geodataframes(
        cls,
        coverage_type,
        demand_col,
        demand_df,
        demand_id_col,
        demand_name,
        supply_df,
        supply_id_col,
    ):
        if not isinstance(demand_df, pd.DataFrame):
            raise TypeError(
                f"Expected 'Dataframe' type for demand_df, got '{type(demand_df)}'"
            )
        if not isinstance(supply_df, pd.DataFrame):
            raise TypeError(
                f"Expected 'Dataframe' type for supply_df, got '{type(supply_df)}'"
            )
        if not isinstance(demand_id_col, str):
            raise TypeError(
                f"Expected 'str' type for demand_id_col, got '{type(demand_id_col)}'"
            )
        if not isinstance(supply_id_col, str):
            raise TypeError(
                f"Expected 'str' type for demand_id_col, got '{type(supply_id_col)}'"
            )
        if not isinstance(demand_name, str) and demand_name is not None:
            raise TypeError(
                f"Expected 'str' type for demand_name, got '{type(demand_name)}'"
            )
        if not isinstance(coverage_type, str):
            raise TypeError(
                f"Expected 'str' type for coverage_type, got '{type(coverage_type)}'"
            )
        if demand_col and demand_col not in demand_df.columns:
            raise ValueError(f"'{demand_col}' not in dataframe")
        if demand_id_col and demand_id_col not in demand_df.columns:
            raise ValueError(f"'{demand_id_col}' not in dataframe")
        if supply_id_col and supply_id_col not in supply_df.columns:
            raise ValueError(f"'{supply_id_col}' not in dataframe")
        if coverage_type.lower() not in ("binary", "partial"):
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        if coverage_type.lower() == "partial" and demand_col is None:
            raise ValueError("demand_col is required when generating partial coverage")

    @classmethod
    def _validate_from_spatially_enabled_dataframes(
        cls,
        coverage_type,
        demand_col,
        demand_df,
        demand_id_col,
        demand_name,
        supply_df,
        supply_id_col,
        demand_geometry_col,
        supply_geometry_col,
    ):
        if not isinstance(demand_df, pd.DataFrame):
            raise TypeError(
                f"Expected 'Dataframe' type for demand_df, got '{type(demand_df)}'"
            )
        if not isinstance(supply_df, pd.DataFrame):
            raise TypeError(
                f"Expected 'Dataframe' type for supply_df, got '{type(supply_df)}'"
            )
        if not isinstance(demand_id_col, str):
            raise TypeError(
                f"Expected 'str' type for demand_id_col, got '{type(demand_id_col)}'"
            )
        if not isinstance(supply_id_col, str):
            raise TypeError(
                f"Expected 'str' type for demand_id_col, got '{type(supply_id_col)}'"
            )
        if not isinstance(demand_name, str) and demand_name is not None:
            raise TypeError(
                f"Expected 'str' type for demand_name, got '{type(demand_name)}'"
            )
        if not isinstance(coverage_type, str):
            raise TypeError(
                f"Expected 'str' type for coverage_type, got '{type(coverage_type)}'"
            )
        if demand_col and demand_col not in demand_df.columns:
            raise ValueError(f"'{demand_col}' not in dataframe")
        if demand_id_col and demand_id_col not in demand_df.columns:
            raise ValueError(f"'{demand_id_col}' not in dataframe")
        if supply_id_col and supply_id_col not in supply_df.columns:
            raise ValueError(f"'{supply_id_col}' not in dataframe")
        if demand_geometry_col and demand_geometry_col not in demand_df.columns:
            raise ValueError(f"'{demand_geometry_col}' not in dataframe")
        if supply_geometry_col and supply_geometry_col not in supply_df.columns:
            raise ValueError(f"'{supply_geometry_col}' not in dataframe")
        if coverage_type.lower() not in ("binary", "partial"):
            raise ValueError(f"Invalid coverage type '{coverage_type}'")
        if coverage_type.lower() == "partial" and demand_col is None:
            raise ValueError("demand_col is required when generating partial coverage")
