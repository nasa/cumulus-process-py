# cumulus-py

[![CircleCI](https://circleci.com/gh/cumulus-nasa/cumulus-process-py.svg?style=svg&circle-token=6564d296f06c4d8d2925e220c4a213267dc70c00)](https://circleci.com/gh/cumulus-nasa/cumulus-process-py)

cumulus-py is a collection of python utilities and a base Docker image for the NASA Cumulus project. The base Docker image (developmentseed/cumulus:base) contains all of the system libraries needed as well as the Python 'cumulus' library. This repository also contains a templtae directory, called project-seed containing basic files needed to create a new Cumulus Docker image for processing data of a new collection.

## Cumulus Process Images

Docker images made for Cumulus are for processing input data into various output files. This could be simply the extraction of metadata from an input file, or could include the creation of thumbnails, or even consist of more compliex processing, running custom science code to create higher level products from an input file.

The base Cumulus docker image does not do any processing on it's own. It is only useful when used as the base image for a specific dataset. 


## Using a Cumulus Process Image


When running the resulting docker image, the default arguments given by CMD will be used unless they are provided at the command line:

  $ docker run -it cumulus:<tagname> <arg1> <arg2>

The default entrypoint for the base docker image (and thus any child image) is the Cumulus Granule API. Call with the -h to see a list of options.

  $ docker run -it cumulus:<tagname> -h

To mount a directory, such as one with datafiles in it to process, use the -v option.

  $ docker run -it cumulus:<tagname> -v .:/work process <datafile1> <datafile2>

There are two commands, one to run a Cumulus recipe, and one just to process files directly (useful for processing local files for testing).

### cumulus process

  $ docker run -it cumulus:<tagname> process -h

```
usage: cumulus-modis process [-h] [--version] [--path PATH]
                             [--loglevel LOGLEVEL]
                             origin-hdf5 origin-thumbnail meta-odl

positional arguments:
  origin-hdf5
  origin-thumbnail
  meta-odl

optional arguments:
  -h, --help           show this help message and exit
  --version            Print version and exit
  --path PATH          Local working path (default: )
  --loglevel LOGLEVEL  0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical
                       (default: 2)
```


### cumulus recipe

  $ docker run -it cumulus:<tagname> recipe -h

```
usage: cumulus-modis recipe [-h] [--version] [--path PATH]
                            [--loglevel LOGLEVEL] [--s3path S3PATH]
                            [--noclean] [--dispatcher DISPATCHER] [--sqs SQS]
                            recipe

positional arguments:
  recipe                Granule recipe (JSON, S3 address, or local file)

optional arguments:
  -h, --help            show this help message and exit
  --version             Print version and exit
  --path PATH           Local working path (default: )
  --loglevel LOGLEVEL   0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical
                        (default: 2)
  --s3path S3PATH       S3 prefix to save output (default: None)
  --noclean             Do not remove local files when done (default: False)
  --dispatcher DISPATCHER
                        Name of Dispatcher Lambda (default: None)
  --sqs SQS             Receipt of SQS message to delete when done (default:
                        None)
```


Which will mount the current directory at /work and process datafiles. The help command will indicate which specific datafiles are needed in which order.

### Environment Variables

Some environment variables are used in the library and should be defined on the system (or passed into the Docker image when run as an environment file.)

  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - dispatcher: Name of Dispatcher Lambda function
  - internal: s3 bucket + prefix for staging processed files
  - ProcessingQueue: The SQS queue to delete from when processing is completed. The receipt handler to be deleted is passed in at the command line.

The project-seed docker-compose file as written expects these files to be contained in a .env file.

```
AWS_ACCESS_KEY_ID=blah_blah_access_key
AWS_SECRET_ACCESS_KEY=blah_blah_secret_key
dispatcher=dispatcher_lambda_name
internal=cumulus-internal/testing_folder
ProcessingQueue=cumulus_processing_queue_name
```


## Building a Cumulus Process Image

The base image can be used to build a new process image for processing a specific dataset (Collection). The 'project-seed' directory contains a set of files that can be used to create an initial project. Copy all the files into a new directory to create a new repository. Then edit each of the files to refer to the specific dataset name where it says 'dataname' (or 'DATANAME'), and then add other code as needed.

For example, edit the Dockerfile to compile code specific to this dataset:

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


### cumulus-py Development

# nosetests -v -s --with-coverage --cover-package cumulus --cover-inclusive --with-timer -v -s

The base docker image is automatically built and pushed to Dockerhub when merging into master. To manually build this image for development:

    $ docker-compose build

Which will create a local cumulus:base Docker image.

  $ docker-compose run test

This image is tagged as developmentseed/cumulus:base in Dockerhub, which can be retrieved without cloning this repository with:

  $ docker pull developmentseed/cumulus:base



