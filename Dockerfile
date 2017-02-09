# Cumulus project base docker file
FROM debian:jessie

# install system dependencies, dev tools, and NetCDF libs
RUN apt-get update; \
    apt-get install -y gcc g++ awscli vim python python-setuptools git make wget; \
    apt-get install -y tree locate; \
    apt-get install -y libnetcdf-dev netcdf-bin

# install python libs
RUN easy_install pip
RUN pip install git+git://github.com/cumulus-nasa/py-cumulus.git@develop

# default to bash entrypoint
ENTRYPOINT ['/bin/bash']
