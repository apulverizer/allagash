Backup Coverage Location Problem (BCLP)
=======================================

Description
-----------
This model aims to cover every demand unit at least once, while trying to increase the amount backup/secondary coverage. For example, you want to implement a new bus system and ensure that every neighborhood has access to at least one bus. You also want to maximize the number of neighborhoods that have 2 buses. You could apply the BCLP to solve this problem.

When to use this model:

- You want to cover 100% of the demand and increase the demand units that are covered twice
- You have point (or polygon) demand


Source
------
Hogan, Kathleen, and Charles Revelle. 1986. Concepts and Applications of Backup Coverage. Management Science 32 (11):1434-1444.

Example
-------
The following example show how an BCLP can be created and solved.

.. code-block:: python

    from allagash import Coverage, Problem
    import pulp
    import geopandas

    d = geopandas.read_file("sample_data/demand_point.shp")
    s = geopandas.read_file("sample_data/facility_service_areas.shp")
    s2 = geopandas.read_file("sample_data/facility2_service_areas.shp")
    coverage1 = Coverage.from_geodataframes(d, s, "GEOID10", "ORIG_ID", demand_col="Population")
    coverage2 = Coverage.from_geodataframes(d, s2, "GEOID10", "ORIG_ID", demand_col="Population")
    problem = Problem.bclp([coverage1, coverage2], max_supply={coverage1: 5, coverage2: 19})
    problem.solve(pulp.GLPK())
