# Set the base image to Ubuntu
FROM continuumio/miniconda3:4.10.3

# File Author / Maintainer
MAINTAINER Aaron Pulver <apulverizer@gmail.com>

# Switch to root for install
USER root
ENV HOME /home/allagash

# Install COINOR CBC and GLPK
# Create the user
RUN apt-get update -y && apt-get install -y \
	--no-install-recommends \
	coinor-cbc \
	glpk-utils \
	&& rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --home-dir $HOME allagash \
    && chmod -R u+rwx $HOME \
    && chown -R allagash:allagash $HOME \
    && chown -R allagash:allagash /opt/conda

# switch back to user
USER allagash
WORKDIR $HOME

COPY --chown=allagash:allagash ci-environment.yml ci-environment.yml

# Copy the license and readme file into the source so it will be included in the built package
COPY --chown=allagash:allagash src LICENSE README.md pyproject.toml src/

# Configure conda env
RUN conda env create -f ci-environment.yml \
    && cd src \
    && /opt/conda/envs/allagash/bin/python -m pip install build \
    && /opt/conda/envs/allagash/bin/python -m build \
    && /opt/conda/envs/allagash/bin/python -m pip install allagash --no-deps --no-index --find-links dist \
    && conda clean -a -f -y
ENV PATH /opt/conda/envs/allagash/bin:$PATH