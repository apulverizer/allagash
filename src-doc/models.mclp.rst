Maximum Coverage Location Problem (MCLP)
========================================

Description
-----------
This model is designed to maximize the total amount of demand serviced using a pre-determined number of facilities.
To be considered covered, demand locations must be completely covered.
It is common for polygon demand to be simplified to centroids for this model.
Polygons can also be considered covered however, if the entire polygon covered.
For example, suppose your local town has funding to build 5 new libraries.
Some GIS analysts perform a site suitability analysis and there are 200 possible locations to choose from.
We can use the MCLP to find the 5 locations provide the most service to the population (centroids of Census block groups).

Use this model when:

- You have a pre-determined number of facilities to site
- You do not need to cover 100% of the demand
- You have point or polygon demand units that are either covered or not (no partial coverage)

Source
------
Church, Richard, and Charles R. Velle. "The maximal covering location problem." Papers in regional science 32.1 (1974): 101-118.

Example
-------
The following example show how an LSCP model can be created and solved.

.. code-block:: python

    from allagash import Coverage, Model
    import pulp
    import geopandas

    d = geopandas.read_file("sample_data/demand_point.shp")
    s = geopandas.read_file("sample_data/facility_service_areas.shp")
    s2 = geopandas.read_file("sample_data/facility2_service_areas.shp")
    coverage1 = Coverage.from_geodataframes(d, s, "GEOID10", "ORIG_ID", demand_name="demand")
    coverage2 = Coverage.from_geodataframes(d, s2, "GEOID10", "ORIG_ID", demand_name="demand")
    model = Model.mclp([coverage1, coverage2], max_supply={coverage1: 5, coverage2: 10})
    solution = model.solve(pulp.GLPK())
