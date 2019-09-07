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

# Configure conda env
RUN conda create -n allagash python=3.7 \
    && conda install --name allagash -y geopandas=0.4.1 jupyter=1.0.0 matplotlib=3.1.1 pytest=5.0.1 \
    && /opt/conda/envs/allagash/bin/pip install pulp==1.6.10 nbval==0.9.2 \
    && /opt/conda/envs/allagash/bin/pip install -i https://test.pypi.org/simple/ Allagash --no-deps \
    && conda clean -a -f -y

COPY --chown=allagash:allagash src-doc/examples examples
ENV PATH /opt/conda/envs/allagash/bin:$PATH