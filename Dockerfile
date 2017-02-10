# Cumulus project base docker file
FROM debian:jessie

# install system dependencies, dev tools, and NetCDF libs
RUN apt-get update; \
    apt-get install -y gcc g++ awscli vim python python-setuptools git make wget; \
    apt-get install -y tree locate; \
    apt-get install -y libnetcdf-dev netcdf-bin; \
    apt-get install -y libhdf4-dev libhdfeos-dev libhdf5-dev libhe5-hdfeos-dev libgctp-dev bash-completion

ENV \
	GDAL_VERSION="2.1.3" \
	LD_LIBRARY_PATH="/usr/local/lib"

RUN \
	wget http://download.osgeo.org/gdal/$GDAL_VERSION/gdal-$GDAL_VERSION.tar.gz; \
	tar -xzvf gdal-$GDAL_VERSION.tar.gz; \
	cd gdal-$GDAL_VERSION; \
	./configure \
    	#--with-hdf4=$HOME/local \
    	#--with-hdf5=$HOME/local \
    	#--with-geos=$HOME/local/bin/geos-config \
    	#--with-proj4=$HOME/local \
        CFLAGS="-O3" CXXFLAGS="-O3"; \
	make; make install; cd ..; \
	rm -rf gdal-$GDAL_VERSION*

WORKDIR /build
COPY ./ /build/
RUN \
	easy_install pip; \
	pip install .

# default to bash entrypoint
ENTRYPOINT ['/bin/bash']
