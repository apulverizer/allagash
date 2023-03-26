Installation
============

Installing with Conda
------------------------------

To install with geopandas run:

.. code-block:: console

    conda install -c conda-forge allagash geopandas

To install with arcgis run:

.. code-block:: console

    conda install -c conda-forge -c esri allagash arcgis

To install without a spatial library run:

.. code-block:: console

    conda install -c conda-forge allagash

Installing with Pip
------------------------------

To install with geopandas run:

.. code-block:: console

    pip install allagash[geopandas]

To install with arcgis run:

.. code-block:: console

    pip install allagash[arcgis]

To install without a spatial library run:

.. code-block:: console

    pip install allagash

Installing with Docker
----------------------

A docker image has been provided which contains the GLPK solver, COIN OR CBC solver, Python, Allagash and any other required dependencies.
You can launch a Jupyter notebook by running:

.. code-block:: console

    docker pull apulverizer/allagash:latest
    docker run -i -t --user=allagash -p 8888:8888 apulverizer/allagash:latest /bin/bash -c "jupyter notebook --ip='*' --port=8888 --no-browser"

Installing locally
------------------

1. Clone the repo

.. code-block:: console

    git clone git@github.com:apulverizer/allagash.git

2. Create the conda environment

.. code-block:: console

    conda env create --file environment.yml

3. Activate the new environment

.. code-block:: console

    conda activate allagash

4. Install allagash locally

.. code-block:: console

    pip install -e ./src --no-deps

5. Install a solver that is supported by `Pulp <https://github.com/coin-or/pulp>`_

    - `GLPK <https://www.gnu.org/software/glpk/>`_
    - `COIN-OR CBC <https://github.com/coin-or/Cbc>`_
    - `CPLEX <https://www.ibm.com/analytics/cplex-optimizer>`_
    - `Gurobi <https://www.gurobi.com/>`_

6. Launch jupyter notebook

.. code-block:: console

    jupyter notebook