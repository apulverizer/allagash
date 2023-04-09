import pytest
from allagash.coverage import Coverage


class TestCoverage:
    def test_init(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value")
        assert isinstance(c, Coverage)

    def test_init_invalid_demand(self):
        with pytest.raises(TypeError) as e:
            Coverage(None, "Value")
        assert (
            e.value.args[0]
            == "Expected 'Dataframe' type for dataframe, got '<class 'NoneType'>'"
        )

    def test_init_invalid_demand_col(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            Coverage(binary_coverage_dataframe, demand_col=[], coverage_type="partial")
        assert (
            e.value.args[0]
            == "Expected 'str' type for demand_col, got '<class 'list'>'"
        )

    def test_init_invalid_supply_name(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            Coverage(binary_coverage_dataframe, supply_name=[])
        assert (
            e.value.args[0]
            == "Expected 'str' type for supply_name, got '<class 'list'>'"
        )

    def test_init_invalid_demand_col2(self, binary_coverage_dataframe):
        with pytest.raises(ValueError) as e:
            Coverage(
                binary_coverage_dataframe, demand_col="Test", coverage_type="partial"
            )
        assert e.value.args[0] == "'Test' not in dataframe"

    def test_init_invalid_demand_col3(self, binary_coverage_dataframe):
        with pytest.raises(ValueError) as e:
            Coverage(
                binary_coverage_dataframe, demand_col=None, coverage_type="partial"
            )
        assert (
            e.value.args[0]
            == "'demand_col' is required when generating partial coverage"
        )

    def test_init_invalid_demand_name(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            Coverage(binary_coverage_dataframe, demand_name=[])
        assert (
            e.value.args[0]
            == "Expected 'str' type for demand_name, got '<class 'list'>'"
        )

    def test_init_invalid_coverage_type(self, binary_coverage_dataframe):
        with pytest.raises(TypeError) as e:
            Coverage(binary_coverage_dataframe, coverage_type=[])
        assert (
            e.value.args[0]
            == "Expected 'str' type for coverage_type, got '<class 'list'>'"
        )

    def test_init_invalid_coverage_type2(self, binary_coverage_dataframe):
        with pytest.raises(ValueError) as e:
            Coverage(binary_coverage_dataframe, coverage_type="test")
        assert e.value.args[0] == "Invalid coverage type 'test'"

    def test_from_coverage_dataframe(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        c = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            "DemandIdentifier",
            "SupplyIdentifier",
        )
        assert isinstance(c, Coverage)

    def test_from_coverage_dataframe_partial(
        self, demand_polygon_dataframe, facility_service_areas_dataframe
    ):
        c = Coverage.from_geodataframes(
            demand_polygon_dataframe,
            facility_service_areas_dataframe,
            "DemandIdentifier",
            "SupplyIdentifier",
            coverage_type="partial",
            demand_col="Value",
        )
        assert isinstance(c, Coverage)
        assert c.coverage_type == "partial"

    def test_from_spatially_enabled_dataframe(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        c = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility_service_areas_sedf,
            "DemandIdentifier",
            "SupplyIdentifier",
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        assert isinstance(c, Coverage)

    def test_from_spatially_enabled_dataframe_partial(
        self, demand_polygon_sedf, facility_service_areas_sedf
    ):
        c = Coverage.from_spatially_enabled_dataframes(
            demand_polygon_sedf,
            facility_service_areas_sedf,
            "DemandIdentifier",
            "SupplyIdentifier",
            coverage_type="partial",
            demand_col="Value",
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        assert isinstance(c, Coverage)
        assert c.coverage_type == "partial"

    def test_from_coverage_dataframe_demand_name(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        c = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            "DemandIdentifier",
            "SupplyIdentifier",
            demand_name="test",
        )
        assert isinstance(c, Coverage)
        assert c.demand_name == "test"

    def test_from_coverage_sedf_demand_name(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        c = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility_service_areas_sedf,
            "DemandIdentifier",
            "SupplyIdentifier",
            demand_name="test",
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        assert isinstance(c, Coverage)
        assert c.demand_name == "test"

    def test_from_coverage_dataframe_supply_name(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        c = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            "DemandIdentifier",
            "SupplyIdentifier",
            supply_name="test",
        )
        assert isinstance(c, Coverage)
        assert c.supply_name == "test"

    def test_from_coverage_sedf_supply_name(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        c = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility_service_areas_sedf,
            "DemandIdentifier",
            "SupplyIdentifier",
            supply_name="test",
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        assert isinstance(c, Coverage)
        assert c.supply_name == "test"

    def test_from_coverage_dataframe_demand_col(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        c = Coverage.from_geodataframes(
            demand_points_dataframe,
            facility_service_areas_dataframe,
            "DemandIdentifier",
            "SupplyIdentifier",
            demand_col="Value",
        )
        assert isinstance(c, Coverage)
        assert c.demand_col == "Value"

    def test_from_coverage_sedf_demand_col(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        c = Coverage.from_spatially_enabled_dataframes(
            demand_points_sedf,
            facility_service_areas_sedf,
            "DemandIdentifier",
            "SupplyIdentifier",
            demand_col="Value",
            demand_geometry_col="geometry",
            supply_geometry_col="geometry",
        )
        assert isinstance(c, Coverage)
        assert c.demand_col == "Value"

    def test_from_coverage_dataframe_invalid_demand_col(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                "DemandIdentifier",
                "SupplyIdentifier",
                demand_col="test",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_sedf_invalid_demand_col(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "SupplyIdentifier",
                demand_col="test",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_dataframe_invalid_coverage_type(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                "DemandIdentifier",
                "SupplyIdentifier",
                coverage_type="test",
            )
        assert e.value.args[0] == "Invalid coverage type 'test'"

    def test_from_coverage_sedf_invalid_coverage_type(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "SupplyIdentifier",
                coverage_type="test",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert e.value.args[0] == "Invalid coverage type 'test'"

    def test_from_coverage_dataframe_demand_col_required(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                "DemandIdentifier",
                "SupplyIdentifier",
                coverage_type="partial",
            )
        assert (
            e.value.args[0] == "demand_col is required when generating partial coverage"
        )

    def test_from_coverage_sedf_demand_col_required(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "SupplyIdentifier",
                coverage_type="partial",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert (
            e.value.args[0] == "demand_col is required when generating partial coverage"
        )

    def test_from_coverage_dataframe_invalid_demand_df(
        self, facility_service_areas_dataframe
    ):
        with pytest.raises(TypeError) as e:
            Coverage.from_geodataframes(
                None,
                facility_service_areas_dataframe,
                "DemandIdentifier",
                "SupplyIdentifier",
            )
        assert (
            e.value.args[0]
            == "Expected 'Dataframe' type for demand_df, got '<class 'NoneType'>'"
        )

    def test_from_coverage_sedf_invalid_demand_df(self, facility_service_areas_sedf):
        with pytest.raises(TypeError) as e:
            Coverage.from_spatially_enabled_dataframes(
                None,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "SupplyIdentifier",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert (
            e.value.args[0]
            == "Expected 'Dataframe' type for demand_df, got '<class 'NoneType'>'"
        )

    def test_from_coverage_dataframe_invalid_supply_df(self, demand_points_dataframe):
        with pytest.raises(TypeError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe, None, "DemandIdentifier", "SupplyIdentifier"
            )
        assert (
            e.value.args[0]
            == "Expected 'Dataframe' type for supply_df, got '<class 'NoneType'>'"
        )

    def test_from_coverage_sedf_invalid_supply_df(self, demand_points_sedf):
        with pytest.raises(TypeError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                None,
                "DemandIdentifier",
                "SupplyIdentifier",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert (
            e.value.args[0]
            == "Expected 'Dataframe' type for supply_df, got '<class 'NoneType'>'"
        )

    def test_from_coverage_dataframe_invalid_demand_id_col(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(TypeError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                None,
                "SupplyIdentifier",
            )
        assert (
            e.value.args[0]
            == "Expected 'str' type for demand_id_col, got '<class 'NoneType'>'"
        )

    def test_from_coverage_sedf_invalid_demand_id_col(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(TypeError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                None,
                "SupplyIdentifier",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert (
            e.value.args[0]
            == "Expected 'str' type for demand_id_col, got '<class 'NoneType'>'"
        )

    def test_from_coverage_dataframe_invalid_supply_id_col(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(TypeError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                "DemandIdentifier",
                None,
            )
        assert (
            e.value.args[0]
            == "Expected 'str' type for demand_id_col, got '<class 'NoneType'>'"
        )

    def test_from_coverage_sedf_invalid_supply_id_col(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(TypeError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                None,
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert (
            e.value.args[0]
            == "Expected 'str' type for demand_id_col, got '<class 'NoneType'>'"
        )

    def test_from_coverage_dataframe_invalid_supply_id_col2(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                "DemandIdentifier",
                "test",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_sedf_invalid_supply_id_col2(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "test",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_dataframe_invalid_demand_id_col2(
        self, demand_points_dataframe, facility_service_areas_dataframe
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_geodataframes(
                demand_points_dataframe,
                facility_service_areas_dataframe,
                "test",
                "SupplyIdentifier",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_sedf_invalid_demand_id_col2(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "test",
                "SupplyIdentifier",
                demand_geometry_col="geometry",
                supply_geometry_col="geometry",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_sedf_invalid_demand_geom_col(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "SupplyIdentifier",
                demand_geometry_col="test",
                supply_geometry_col="geometry",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_from_coverage_sedf_invalid_supply_geom_col(
        self, demand_points_sedf, facility_service_areas_sedf
    ):
        with pytest.raises(ValueError) as e:
            Coverage.from_spatially_enabled_dataframes(
                demand_points_sedf,
                facility_service_areas_sedf,
                "DemandIdentifier",
                "SupplyIdentifier",
                demand_geometry_col="geometry",
                supply_geometry_col="test",
            )
        assert e.value.args[0] == "'test' not in dataframe"

    def test_df_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value")
        assert c.df is binary_coverage_dataframe

    def test_demand_name_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value", demand_name="test")
        assert c.demand_name == "test"

    def test_demand_name_property_default(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value")
        assert isinstance(c.demand_name, str)

    def test_supply_name_property_default(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value")
        assert isinstance(c.supply_name, str)

    def test_supply_name_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value", supply_name="test")
        assert c.supply_name == "test"

    def test_coverage_type_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value", coverage_type="binary")
        assert c.coverage_type == "binary"

    def test_coverage_type_property2(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value", coverage_type="partial")
        assert c.coverage_type == "partial"

    def test_demand_col_property(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe, "Value")
        assert c.demand_col == "Value"

    def test_demand_col_property2(self, binary_coverage_dataframe):
        c = Coverage(binary_coverage_dataframe)
        assert c.demand_col is None
