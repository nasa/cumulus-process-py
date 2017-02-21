# cumulus-py

[![CircleCI](https://circleci.com/gh/cumulus-nasa/cumulus-py.svg?style=svg)](https://circleci.com/gh/cumulus-nasa/cumulus-py)

cumulus-py is a collection of python utilities and a base Docker image for the NASA Cumulus project.

The Docker image is automatically built and pushed to Dockerhub when merging into master. To manually build this image for development:

    $ docker-compose build

Which will create a local cumulus:base Docker image.

	$ docker-compose run test

This image is tagged as developmentseed/cumulus:base in Dockerhub, which can be retrieved without cloning this repository with:

	$ docker pull developmentseed/cumulus:base

## Build a Cumulus Process Image

The base image can be used to build a new process image for processing a specific dataset (Collection). Use this template for creating a new Dockerfile:

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

The default entrypoint for the base docker image (and thus any child image) is the Cumulus Granule API. Call with the -h to see a list of options.

  $ docker run -it cumulus:<tagname> -h

To mount a directory, such as one with datafiles in it to process, use the -v option.

  $ docker run -it cumulus:<tagname> -v .:/work <datafile1> <datafile2>

Which will mount the current directory at /work and process datafiles. The help command will indicate which specific datafiles are needed in which order.


## Environment Variables

Some environment variables are used in the library and should be defined on the system.

  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - dispatcher
  - SPLUNK_HOST
  - SPLUNK_USERNAME
  - SPLUNK_PASSWORD



