# Cumulus project base docker file
FROM debian:jessie

# install system dependencies, dev tools, and NetCDF libs
RUN apt-get update; \
    apt-get install -y gcc g++ awscli vim python-dev python-setuptools git make wget swig; \
    apt-get install -y tree locate; \
    #apt-get install -y libnetcdf-dev netcdf-bin; \
    apt-get install -y libhdf4-dev libhdfeos-dev libhdf5-dev libhe5-hdfeos-dev libgctp-dev bash-completion

WORKDIR /build

ENV \
	GDAL_VERSION="2.1.3"

RUN \
	wget http://download.osgeo.org/gdal/$GDAL_VERSION/gdal-$GDAL_VERSION.tar.gz; \
	tar -xzvf gdal-$GDAL_VERSION.tar.gz; \
	cd gdal-$GDAL_VERSION; \
	./configure \
        --with-python=yes \
    	#--with-hdf4=yes \
    	--with-hdf5=/usr/lib/x86_64-linux-gnu/hdf5/serial \
    	#--with-geos=$HOME/local/bin/geos-config \
    	#--with-proj4=$HOME/local \
        CFLAGS="-O3" CXXFLAGS="-O3"; \
	make; make install; cd ..; \
	rm -rf gdal-$GDAL_VERSION*

ENV \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"

COPY ./ /build/
RUN \
	easy_install pip; \
    pip install numpy wheel; \
    pip install -r requirements.txt; \
	pip install .; \
    rm -rf /build

# default to bash entrypoint
ENTRYPOINT ['/bin/bash']
