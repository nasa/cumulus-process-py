# Cumulus project base docker file
FROM developmentseed/geolambda:full

MAINTAINER developmentseed

ENV \
	BUILD=/build \
	HOME=/home/cumulus

WORKDIR $BUILD

# install cumulus package and any scripts
COPY requirements.txt requirements-dev.txt setup.py $BUILD/
COPY cumulus $BUILD/cumulus
COPY bin $BUILD/bin
RUN \
  	pip install -r requirements.txt; \
  	pip install -r requirements-dev.txt; \
  	pip install . -v;  \
  	mv bin/* /usr/local/bin/; \
  	rm -rf $BUILD/*

### create cumulus user - mounted volumes don't change perms TODO - figure this out
#RUN \
#    groupadd -r cumulus -g 299; \
#    useradd -u 299 -r -g cumulus -d $HOME -c "Cumulus processing" cumulus; \
#    chown -R cumulus:cumulus $HOME
#USER cumulus

WORKDIR $HOME

CMD ["/bin/bash"]
