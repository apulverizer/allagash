# Set the base image to Ubuntu
FROM continuumio/miniconda3

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
ENV HOME /home/allagash-user
RUN useradd --create-home --home-dir $HOME allagash-user\
    && chmod -R u+rwx $HOME\
    && chown -R allagash-user:allagash-user $HOME

# switch back to user
WORKDIR $HOME
USER allagash-user

RUN mkdir $HOME/allagash
WORKDIR $HOME/allagash

# Configure conda env
COPY --chown=allagash-user:allagash-user environment.yml environment.yml
RUN conda env create -f environment.yml\
    && rm -rf environment.yml
COPY --chown=allagash-user:allagash-user examples examples
COPY --chown=allagash-user:allagash-user src src
RUN $HOME/.conda/envs/allagash/bin/pip install ./src --no-deps\
    && rm -rf src
ENV PATH $HOME/.conda/envs/allagash/bin:$PATH