# Cumulus project base docker file
FROM developmentseed/geolambda:gdal2hdf

WORKDIR /work

# install requirements
COPY requirements.txt /work/
COPY requirements-dev.txt /work/
RUN \
  	easy_install pip; \
  	pip install numpy wheel; \
  	pip install -r requirements.txt; \
  	pip install -r requirements-dev.txt; \
  	rm -rf /work

# install package
COPY ./ /work/
RUN \
	pip install .; \
  	rm -rf /work

# default to bash entrypoint
ENTRYPOINT /bin/bash
CMD []
