Location Set Covering Problem (LSCP)
====================================

Description
-----------
This is one of the earliest spatial optimization models. It aims to minimize the total number of facilities while ensuring that every demand location is covered at least once.
For example, you want to implement a new bus system and ensure that every neighborhood has access to at least one bus.

Use this model when:

- You need to cover every demand location
- You have demand that is covered or not (binary)

Source
------
Toregas, Constantine, et al. "The location of emergency service facilities." Operations Research 19.6 (1971): 1363-1373.

Example
-------
The following example show how an LSCP model can be created and solved.

.. code-block:: python

    from allagash import DemandDataset, SupplyDataset, Coverage
    import pulp
    import geopandas

    d = DemandDataset(geopandas.read_file(r"../sample_data/demand_point.shp")), "GEOID10", "Population")
    s = SupplyDataset(geopandas.read_file(r"../sample_data/facility_service_areas.shp")), "ORIG_ID")
    s2 = SupplyDataset(geopandas.read_file(r"../sample_data/facility2_service_areas.shp")), "ORIG_ID")
    coverage = Coverage(d, [s, s2], 'binary')
    model = coverage.create_model('lscp')
    solution = model.solve(pulp.GLPK())
