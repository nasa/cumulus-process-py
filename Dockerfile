# Cumulus project base docker file
FROM developmentseed/geolambda:gdal2hdf

MAINTAINER developmentseed

ENV \
	BUILD=/build; \
	HOME=/home/cumulus

WORKDIR $BUILD

# install requirements
COPY requirements.txt $BUILD
COPY requirements-dev.txt $BUILD
RUN \
  	easy_install pip; \
  	pip install numpy wheel; \
  	pip install -r requirements.txt; \
  	pip install -r requirements-dev.txt;

# install package
COPY ./ $BUILD
RUN \
	pip install .; \
  	rm -rf $BUILD

### create cumulus user
RUN \
    mkdir -p $HOME; \
    groupadd -r cumulus -g 299; \
    useradd -u 299 -r -g cumulus -d $HOME -s /sbin/nologin -c "Cumulus processing" cumulus; \
    chown -R cumulus:cumulus $HOME

CMD ["/bin/bash"]
