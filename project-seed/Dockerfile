FROM developmentseed/cumulus:base

COPY ./ /build
RUN \
    pip install .; \
    rm -rf *

ENTRYPOINT ["cumulus-dataname"]
CMD []
