import pytest
from allagash.coverage import Coverage


class TestCoverage:

    def test_init(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population")
        assert(isinstance(c, Coverage))

    def test_init_invalid_demand(self):
        with pytest.raises(TypeError) as e:
            c = Coverage(None, "Population")
        assert(e.value.args[0] == "Expected 'Dataframe' type for dataframe, got '<class 'NoneType'>'")

    def test_init_invalid_demand_col(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage(binary_coverage_dataframe, demand_col=[], coverage_type="partial")
        assert(e.value.args[0] == "Expected 'str' type for demand_col, got '<class 'list'>'")

    def test_init_invalid_supply_name(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage(binary_coverage_dataframe, supply_name=[])
        assert (e.value.args[0] == "Expected 'str' type for supply_name, got '<class 'list'>'")

    def test_init_invalid_demand_col2(self, binary_coverage_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage(binary_coverage_dataframe, demand_col="Test", coverage_type="partial")
        assert(e.value.args[0] == "'Test' not in dataframe")

    def test_init_invalid_demand_col3(self, binary_coverage_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage(binary_coverage_dataframe, demand_col=None, coverage_type="partial")
        assert(e.value.args[0] == "'demand_col' is required when generating partial coverage")

    def test_init_invalid_demand_name(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage(binary_coverage_dataframe, demand_name=[])
        assert(e.value.args[0] == "Expected 'str' type for demand_name, got '<class 'list'>'")

    def test_init_invalid_coverage_type(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage(binary_coverage_dataframe, coverage_type=[])
        assert(e.value.args[0] == "Expected 'str' type for coverage_type, got '<class 'list'>'")

    def test_init_invalid_coverage_type2(self, binary_coverage_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage(binary_coverage_dataframe, coverage_type="test")
        assert(e.value.args[0] == "Invalid coverage type 'test'")

    def test_from_coverage_dataframe(self, demand_points_dataframe, facility_service_areas_dataframe):
        c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                        "GEOID10", "ORIG_ID")
        assert(isinstance(c, Coverage))

    def test_from_coverage_dataframe_demand_name(self, demand_points_dataframe, facility_service_areas_dataframe):
        c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                        "GEOID10", "ORIG_ID", demand_name="test")
        assert(isinstance(c, Coverage))
        assert c.demand_name == "test"

    def test_from_coverage_dataframe_supply_name(self, demand_points_dataframe, facility_service_areas_dataframe):
        c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                        "GEOID10", "ORIG_ID", supply_name="test")
        assert(isinstance(c, Coverage))
        assert c.supply_name == "test"

    def test_from_coverage_dataframe_demand_col(self, demand_points_dataframe, facility_service_areas_dataframe):
        c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                        "GEOID10", "ORIG_ID", demand_col="Population")
        assert(isinstance(c, Coverage))
        assert c.demand_col == "Population"

    def test_from_coverage_dataframe_invalid_demand_col(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            "GEOID10", "ORIG_ID", demand_col="test")
        assert(e.value.args[0] == "'test' not in dataframe")

    def test_from_coverage_dataframe_invalid_coverage_type(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            "GEOID10", "ORIG_ID", coverage_type="test")
        assert(e.value.args[0] == "Invalid coverage type 'test'")

    def test_from_coverage_dataframe_demand_col_required(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            "GEOID10", "ORIG_ID", coverage_type="partial")
        assert(e.value.args[0] == "demand_col is required when generating partial coverage")

    def test_from_coverage_dataframe_invalid_demand_df(self, facility_service_areas_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage.from_geodataframes(None, facility_service_areas_dataframe,
                                            "GEOID10", "ORIG_ID")
        assert(e.value.args[0] == "Expected 'Dataframe' type for demand_df, got '<class 'NoneType'>'")

    def test_from_coverage_dataframe_invalid_supply_df(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, None,
                                            "GEOID10", "ORIG_ID")
        assert(e.value.args[0] == "Expected 'Dataframe' type for supply_df, got '<class 'NoneType'>'")

    def test_from_coverage_dataframe_invalid_demand_id_col(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            None, "ORIG_ID")
        assert(e.value.args[0] == "Expected 'str' type for demand_id_col, got '<class 'NoneType'>'")

    def test_from_coverage_dataframe_invalid_supply_id_col(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(TypeError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            "GEOID10", None)
        assert(e.value.args[0] == "Expected 'str' type for demand_id_col, got '<class 'NoneType'>'")

    def test_from_coverage_dataframe_invalid_supply_id_col2(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            "GEOID10", "test")
        assert(e.value.args[0] == f"'test' not in dataframe")

    def test_from_coverage_dataframe_invalid_demand_id_col2(self, demand_points_dataframe, facility_service_areas_dataframe):
        with pytest.raises(ValueError) as e:
            c = Coverage.from_geodataframes(demand_points_dataframe, facility_service_areas_dataframe,
                                            "test", "ORIG_ID")
        assert(e.value.args[0] == f"'test' not in dataframe")

    def test_df_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population")
        assert(c.df is binary_coverage_dataframe)

    def test_demand_name_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population", demand_name="test")
        assert(c.demand_name == "test")

    def test_demand_name_property_default(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population")
        assert(isinstance(c.demand_name, str))

    def test_supply_name_property_default(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population")
        assert(isinstance(c.supply_name, str))

    def test_supply_name_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population", supply_name="test")
        assert(c.supply_name == "test")

    def test_coverage_type_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population", coverage_type="binary")
        assert(c.coverage_type == "binary")

    def test_coverage_type_property2(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population", coverage_type="partial")
        assert(c.coverage_type == "partial")

    def test_demand_col_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Population")
        assert(c.demand_col == "Population")

    def test_demand_col_property2(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe)
        assert(c.demand_col is None)
