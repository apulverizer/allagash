# Set the base image to Ubuntu
FROM continuumio/miniconda3:4.7.10

# File Author / Maintainer
MAINTAINER Aaron Pulver <apulverizer@gmail.com>

# Switch to root for install
USER root

# Install dependencies including COINOR CBC
RUN apt-get update -y && apt-get install -y \
	wget \
	build-essential \
	--no-install-recommends \
	coinor-cbc \
	&& rm -rf /var/lib/apt/lists/*

# Install GLPK
WORKDIR /user/local/
RUN wget http://ftp.gnu.org/gnu/glpk/glpk-4.65.tar.gz \
	&& tar -zxvf glpk-4.65.tar.gz

WORKDIR /user/local/glpk-4.65
RUN ./configure \
	&& make \
	&& make check \
	&& make install \
	&& make distclean \
	&& ldconfig \
	&& rm -rf /user/local/glpk-4.65.tar.gz \
	&& apt-get clean

# create a allagash user
ENV HOME /home/allagash
RUN useradd --create-home --home-dir $HOME allagash\
    && chmod -R u+rwx $HOME\
    && chown -R allagash:allagash $HOME\
    && chown -R allagash:allagash /opt/conda

# switch back to user
USER allagash
WORKDIR $HOME

COPY --chown=allagash:allagash environment.yml environment.yml
COPY --chown=allagash:allagash src src

# Configure conda env
RUN conda env create -f environment.yml \
    && cd src \
    && /opt/conda/envs/allagash/bin/python setup.py sdist bdist_wheel \
    && /opt/conda/envs/allagash/bin/pip install allagash --no-deps --find-links dist \
    && conda clean -a -f -y
ENV PATH /opt/conda/envs/allagash/bin:$PATH