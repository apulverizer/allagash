# Allagash 

[![build status](https://github.com/apulverizer/allagash/workflows/Build/badge.svg)](https://github.com/apulverizer/allagash/actions)
[![MIT License](https://anaconda.org/conda-forge/allagash/badges/license.svg)](LICENSE)
[![Install with conda](https://anaconda.org/conda-forge/allagash/badges/version.svg)](https://anaconda.org/conda-forge/allagash)

A spatial optimization library for covering problems. Full documentation is available [here](https://apulverizer.github.io/allagash)

----

### Installing with conda

To install with geopandas run:

`conda install -c conda-forge allagash geopandas`

To install with arcgis run:

`conda install -c conda-forge -c esri allagash arcgis`

To install without a spatial library run:

`conda install -c conda-forge allagash`

----

### Installing with pip

To install with geopandas run:

`pip install allagash[geopandas]`

To install with arcgis run:

`pip install allagash[arcgis]`

To install without a spatial library run:

`pip install allagash`

----

### Running Locally
1. Clone the repo `git clone git@github.com:apulverizer/allagash.git`
2. Create the conda environment `conda env create --file environment.yml`
3. Activate the new environment `conda activate allagash`
4. Install pre-commit hooks `pre-commit install`
5. Install allagash locally `pip install -e ./src --no-deps`
6. Launch jupyter notebook `jupyter notebook`

You should now be able to run the example notebooks.

You can choose to install and use another solver that is supported by [Pulp](https://github.com/coin-or/pulp):
- [GLPK](https://www.gnu.org/software/glpk/) (included in conda environment)
- [COIN-OR CBC](https://github.com/coin-or/Cbc)
- [CPLEX](https://www.ibm.com/analytics/cplex-optimizer)
- [Gurobi](https://www.gurobi.com/)

----

### Running Tests Locally
1. Run tests `pytest --nbval`

----

### Building Documentation
1. From the repo directory run `sphinx-build -b html ./src-doc ./docs -a`

This will deploy html documentation to the docs folder.

----

### Running with Docker
You can build the local docker image that includes Allagash, Python, Jupyter, GLPK, and COIN-OR CBC.

1. Builder the docker image `docker build . -t apulverizer/allagash:latest`
2. Launch Jupyter notebook `docker run -i -t --user=allagash -p 8888:8888 apulverizer/allagash:latest /bin/bash -c "jupyter notebook --ip='*' --port=8888 --no-browser"`

You should now be able to run the example notebooks.

You can test the notebooks as well by running `docker run --user=allagash apulverizer/allagash:latest /bin/bash -c "py.test --nbval"`

If you'd like to mount a directory of local data/files into the container, you can add `-v <your-local-dir>:/home/allagash/<dir-name>` when running `docker run`

----

### Running Tests with Docker
You can build a docker container that will run the tests (mounted into the container)

1. `docker build . --file build.Dockerfile --tag apulverizer/allagash:build`
2. `docker run --user=allagash -v $PWD/tests:/home/allagash/tests -v $PWD/src-doc:/home/allagash/src-doc apulverizer/allagash:build /bin/bash -c "py.test --nbval"`
