Location Set Covering Problem (LSCP)
====================================

Description
-----------
This is one of the earliest spatial optimization problems. It aims to minimize the total number of facilities while ensuring that every demand location is covered at least once.
For example, you want to implement a new bus system and ensure that every neighborhood has access to at least one bus.

Use this problem when:

- You need to cover every demand location
- You have demand that is covered or not (binary)

Source
------
Toregas, Constantine, et al. "The location of emergency service facilities." Operations Research 19.6 (1971): 1363-1373.

Example
-------
The following example show how an LSCP can be created and solved.

.. code-block:: python

    from allagash import Coverage, Problem
    import pulp
    import geopandas

    d = geopandas.read_file("sample_data/demand_point.shp")
    s = geopandas.read_file("sample_data/facility_service_areas.shp")
    s2 = geopandas.read_file("sample_data/facility2_service_areas.shp")
    coverage1 = Coverage.from_geodataframes(d, s, "GEOID10", "ORIG_ID")
    coverage2 = Coverage.from_geodataframes(d, s2, "GEOID10", "ORIG_ID")
    problem = Problem.lscp([coverage1, coverage2])
    problem.solve(pulp.GLPK())
