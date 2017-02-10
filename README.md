# cumulus-py

[![CircleCI](https://circleci.com/gh/cumulus-nasa/cumulus-py.svg?style=svg)](https://circleci.com/gh/cumulus-nasa/cumulus-py)

cumulus-py is a collection of python utilities and a base Docker image for the NASA Cumulus project.

The Docker image is automatically built and pushed to Dockerhub when merging into master. To manually build this image for development:

    $ docker-compose build -t

Which will create a local cumulus:base Docker image.

	$ docker-compose run test

This image is tagged as developmentseed/cumulus:base in Dockerhub, which can be retrieved without cloning this repository at all with:

	$ docker pull developmentseed/cumulus:base

## Build a Cumulus Process Docker

The base image can be used to build a new process Docker for processing a new dataset (Collection). Use this template for creating a new Dockerfile:

```
FROM developmentseed/cumulus:base

# install additional packages here
RUN apt-get update; \
	apt-get install <packages>

# copy needed files
WORKDIR /work
COPY ./work

# compile/install custom packages
RUN <commands>

# install Python requirements
RUN pip install -r requirements.txt

# define entrypoint
ENTRYPOINT ["<program-path>"]
# default arguments
CMD ["<arg1>", "<arg2>"]
```

It is easiest to build, test, and interact with the resulting docker image using a docker-compose file:

```
version: '2'

services:
  
  build:
    build: .
    image: cumulus:<tagname>

  bash:
    image: cumulus:<tagname>
    entrypoint: /bin/bash

  test:
    image: cumulus:<tagname>
    entrypoint: bash -c 'pip install -r requirements-dev.txt; nosetests --with-coverage --cover-package cumulus --cover-inclusive --with-timer -v -s;'
    working_dir: /work
    volumes:
      - '.:/work'
```

When running the resulting docker image, the default arguments given by CMD will be used unless they are provided at the command line:

	$ docker run -it cumulus:<tagname> <arg1> <arg2>



