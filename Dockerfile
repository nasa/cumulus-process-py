# Cumulus project base docker file
FROM developmentseed/geolambda:gdal2hdf

# install system dependencies, dev tools, and NetCDF libs
#RUN apt-get update; \
    #apt-get install -y gcc g++ awscli vim python-dev python-setuptools git make wget swig; \
    #apt-get install -y tree locate; \
    #apt-get install -y libnetcdf-dev netcdf-bin; \
    #apt-get install -y libhdf4-dev libhdfeos-dev libhdf5-dev libhe5-hdfeos-dev libgctp-dev bash-completion

WORKDIR /build

COPY requirements.txt /build/

RUN \
	easy_install pip; \
  pip install numpy wheel; \
  pip install -r requirements.txt; \
  rm -rf /build


COPY ./ /build/
RUN \
	pip install .; \
  rm -rf /build

# default to bash entrypoint
ENTRYPOINT /bin/bash
CMD []