# Set the base image to Ubuntu
FROM continuumio/miniconda3:23.9.0-0
ARG VERSION

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

# Copy in environment file
COPY --chown=allagash:allagash ci-environment.yml ci-environment.yml

# Configure conda env
RUN conda env create -f ci-environment.yml \
    && /opt/conda/envs/allagash/bin/pip install allagash==${VERSION} --no-deps \
    && conda clean -a -f -y

COPY --chown=allagash:allagash src-doc/examples examples
ENV PATH /opt/conda/envs/allagash/bin:$PATH