# Cumulus project base docker file
FROM developmentseed/geolambda:full

MAINTAINER developmentseed

ENV \
	BUILD=/build \
	HOME=/home/cumulus

WORKDIR $BUILD

# install cumulus package and any scripts
COPY requirements.txt requirements-dev.txt setup.py $BUILD/cumulus-py/
COPY cumulus $BUILD/cumulus-py/cumulus
COPY test $BUILD/cumulus-py/test
COPY bin $BUILD/cumulus-py/bin
RUN \
	cd cumulus-py; \
  	pip install -r requirements.txt; \
  	pip install -r requirements-dev.txt; \
  	pip install . -v;  \
  	mv bin/* /usr/local/bin/;

WORKDIR $HOME

CMD ["/bin/bash"]
