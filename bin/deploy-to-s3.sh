#!/bin/bash

lambda-package.sh

S3_BUCKET=$1

# location of this script
#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# location of cumulus package
PACKAGEDIR=$(find cumulus_* -type d | head -n 1)
PACKAGENAME=$(basename $PACKAGEDIR)
DATANAME=${PACKAGENAME:8}
S3_PATH=deploy/cumulus-process/$DATANAME

# get package version
source $PACKAGEDIR/version.py

CMD="aws s3 cp lambda-deploy.zip s3://$S3_BUCKET/$S3_PATH/$__version__.zip"
echo $CMD
$CMD