from allagash.dataset import DemandDataset, SupplyDataset, Dataset
import os
import pytest


class TestDataset:
    dir_name = os.path.dirname(__file__)

    def test_init(self, demand_points_dataframe):
        d = Dataset(demand_points_dataframe, "GEOID10")
        assert(isinstance(d, Dataset))

    def test_init_invalid_df(self):
        with pytest.raises(TypeError) as e:
            Dataset(None, "GEOID10")
        assert(e.value.args[0] == "Expected 'Dataframe' type for dataaframe, got '<class 'NoneType'>'")

    def test_init_invalid_unique_field(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            Dataset(demand_points_dataframe, None)
        assert(e.value.args[0] == "Expected 'str' type for unique_field, got '<class 'NoneType'>'")

    def test_init_unique_field_not_in_df(self, demand_points_dataframe):
        with pytest.raises(ValueError) as e:
            Dataset(demand_points_dataframe, "invalid")
        assert(e.value.args[0] == "'invalid' not in dataframe")

    def test_df_property(self, demand_points_dataframe):
        d = Dataset(demand_points_dataframe, "GEOID10")
        assert(d.df.equals(demand_points_dataframe))

    def test_unique_field_property(self, demand_points_dataframe):
        d = Dataset(demand_points_dataframe, "GEOID10")
        assert(d.unique_field == "GEOID10")

    def test_unique_name_property(self, demand_points_dataframe):
        d = Dataset(demand_points_dataframe, "GEOID10", "a_name")
        assert(d.name == "a_name")

    def test_unique_name_default_property(self, demand_points_dataframe):
        d = Dataset(demand_points_dataframe, "GEOID10")
        assert(isinstance(d.name, str))
        assert(len(d.name) == 6)


class TestDemandDataset:
    dir_name = os.path.dirname(__file__)

    def test_init(self, demand_points_dataframe):
        d = DemandDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(isinstance(d, Dataset))

    def test_init_invalid_df(self):
        with pytest.raises(TypeError) as e:
            DemandDataset(None, "GEOID10", "Population")
        assert(e.value.args[0] == "Expected 'Dataframe' type for dataaframe, got '<class 'NoneType'>'")

    def test_init_invalid_unique_field(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            DemandDataset(demand_points_dataframe, None, "Population")
        assert(e.value.args[0] == "Expected 'str' type for unique_field, got '<class 'NoneType'>'")

    def test_init_invalid_demand_field(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            DemandDataset(demand_points_dataframe, "GEOID10", None)
        assert(e.value.args[0] == "Expected 'str' type for demand_field, got '<class 'NoneType'>'")

    def test_init_invalid_demand_field_type(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            DemandDataset(demand_points_dataframe, "GEOID10", "GEOID10")
        assert(e.value.args[0] == "'GEOID10' is not a numeric field in dataframe")

    def test_init_unique_field_not_in_df(self, demand_points_dataframe):
        with pytest.raises(ValueError) as e:
            DemandDataset(demand_points_dataframe, "invalid", "Population")
        assert(e.value.args[0] == "'invalid' not in dataframe")

    def test_init_demand_field_not_in_df(self, demand_points_dataframe):
        with pytest.raises(ValueError) as e:
            DemandDataset(demand_points_dataframe, "GEOID10", "invalid")
        assert(e.value.args[0] == "'invalid' not in dataframe")

    def test_df_property(self, demand_points_dataframe):
        d = DemandDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(d.df.equals(demand_points_dataframe))

    def test_unique_field_property(self, demand_points_dataframe):
        d = DemandDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(d.unique_field == "GEOID10")

    def test_unique_name_property(self, demand_points_dataframe):
        d = DemandDataset(demand_points_dataframe, "GEOID10", "Population", "a_name")
        assert(d.name == "a_name")

    def test_unique_name_default_property(self, demand_points_dataframe):
        d = DemandDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(isinstance(d.name, str))
        assert(len(d.name) == 6)

    def test_demand_field_property(self, demand_points_dataframe):
        d = DemandDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(d.demand_field == "Population")


class TestSupplyDataset:
    dir_name = os.path.dirname(__file__)

    def test_init(self, demand_points_dataframe):
        d = SupplyDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(isinstance(d, Dataset))

    def test_init_invalid_df(self):
        with pytest.raises(TypeError) as e:
            SupplyDataset(None, "GEOID10", "Population")
        assert(e.value.args[0] == "Expected 'Dataframe' type for dataaframe, got '<class 'NoneType'>'")

    def test_init_invalid_unique_field(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            SupplyDataset(demand_points_dataframe, None, "Population")
        assert(e.value.args[0] == "Expected 'str' type for unique_field, got '<class 'NoneType'>'")

    def test_init_unique_field_not_in_df(self, demand_points_dataframe):
        with pytest.raises(ValueError) as e:
            SupplyDataset(demand_points_dataframe, "invalid", "Population")
        assert(e.value.args[0] == "'invalid' not in dataframe")

    def test_df_property(self, demand_points_dataframe):
        d = SupplyDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(d.df.equals(demand_points_dataframe))

    def test_unique_field_property(self, demand_points_dataframe):
        d = SupplyDataset(demand_points_dataframe, "GEOID10", "Population")
        assert(d.unique_field == "GEOID10")

    def test_unique_name_property(self, demand_points_dataframe):
        d = SupplyDataset(demand_points_dataframe, "GEOID10", "a_name")
        assert(d.name == "a_name")

    def test_unique_name_default_property(self, demand_points_dataframe):
        d = SupplyDataset(demand_points_dataframe, "GEOID10")
        assert(isinstance(d.name, str))
        assert(len(d.name) == 6)
