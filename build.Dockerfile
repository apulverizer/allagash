# Set the base image to Ubuntu
FROM continuumio/miniconda3:4.11.0

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
COPY --chown=allagash:allagash src LICENSE README.md src/

# Configure conda env
RUN conda env create -f ci-environment.yml \
    && cd src \
    && /opt/conda/envs/allagash/bin/python setup.py sdist bdist_wheel \
    && /opt/conda/envs/allagash/bin/pip install allagash --no-deps --no-index --find-links dist \
    && conda clean -a -f -y
ENV PATH /opt/conda/envs/allagash/bin:$PATH