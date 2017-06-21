# Cumulus project base docker file
FROM developmentseed/geolambda:gdal2hdf

WORKDIR /build

# install requirements
COPY requirements.txt /build/
RUN \
  easy_install pip; \
  pip install numpy wheel; \
  pip install -r requirements.txt; \
  rm -rf /build

# install package
COPY ./ /build/
RUN \
	pip install .; \
  rm -rf /build

# default to bash entrypoint
ENTRYPOINT /bin/bash
CMD []
