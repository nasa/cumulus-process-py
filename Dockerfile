# Cumulus project base docker file
FROM developmentseed/geolambda:full

MAINTAINER developmentseed

ENV \
	BUILD=/build \
	HOME=/home/cumulus

WORKDIR $BUILD

# install requirements
COPY requirements.txt $BUILD
COPY requirements-dev.txt $BUILD
RUN \
  	easy_install pip; \
  	pip install numpy wheel awscli; \
  	pip install -r requirements.txt; \
  	pip install -r requirements-dev.txt;

# install package
COPY ./ $BUILD
RUN \
    mv bin/deploy-to-s3.sh /usr/local/bin; \
	  pip install .; \
  	rm -rf $BUILD

### create cumulus user
RUN \
    groupadd -r cumulus -g 299; \
    useradd -u 299 -r -g cumulus -d $HOME -c "Cumulus processing" cumulus; \
    #mkdir -p $HOME; \
    chown -R cumulus:cumulus $HOME

#USER cumulus
WORKDIR $HOME/work

CMD ["/bin/bash"]
