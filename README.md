# Allagash [![build status](https://github.com/apulverizer/allagash/workflows/integration/badge.svg)](https://github.com/apulverizer/allagash/actions)
A spatial optimization library for covering problems

### Running Locally
1. Clone the repo `git clone git@github.com:apulverizer/allagash.git`
2. Create the conda environment `conda env create --file environment.yml`
3. Activate the new environment `conda activate allagash`
4. Install allagash locally `pip install -e ./src --no-deps`
5. Install a solver that is supported by [Pulp](https://github.com/coin-or/pulp)
    1. [GLPK](https://www.gnu.org/software/glpk/)
    2. [COIN-OR CBC](https://github.com/coin-or/Cbc)
    3. [CPLEX](https://www.ibm.com/analytics/cplex-optimizer)
    4. [Gurobi](https://www.gurobi.com/)
6. Launch jupyter notebook `jupyter notebook`

You should now be able to run the example notebooks.

### Running Tests Locally
1. Run tests `pytest --nbval`

### Building Documentation
1. From the repo directory run `sphinx-build -b html ./src-doc ./docs -a`

This will deploy html documentation to the docs folder.

### Running with Docker
You can build the local docker image that includes Allagash, Python, Jupyter, GLPK, and COIN-OR CBC.

1. Builder the docker image `docker build . -t apulverizer/allagash:latest`
2. Launch Jupyter notebook `docker run -i -t --user=allagash-user -p 8888:8888 apulverizer/allagash:latest /bin/bash -c "jupyter notebook --ip='*' --port=8888 --no-browser"`

You should now be able to run the example notebooks.

You can test the notebooks as well by running `docker run --user=allagash-user apulverizer/allagash:latest /bin/bash -c "py.test --nbval"`

### Running Tests with Docker
You can build a docker container that will run the tests based on any local changes

1. `docker build . --file integration.Dockerfile --tag apulverizer/allagash:integration`
2. `docker run --user=allagash-user apulverizer/allagash:integration /bin/bash -c "py.test --nbval"`