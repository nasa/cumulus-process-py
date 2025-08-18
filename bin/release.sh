#!/bin/bash

set -ex
VERSION_TAG=$(awk -F\' '{print $2}' cumulus_process/version.py)
LATEST_TAG=$(curl -H \
  "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/nasa/cumulus-process-py/tags | jq --raw-output '.[0].name')
git config --global user.email "cumulus.bot@gmail.com"
git config --global user.name "Cumulus Bot"
export VERSION_TAG
export LATEST_TAG

if [ "$VERSION_TAG" != "$LATEST_TAG" ]; then
  echo "tag does not exist for version $VERSION_TAG, creating tag"

  # create git tag
  git tag -a "$VERSION_TAG" -m "$VERSION_TAG" || echo "$VERSION_TAG already exists"
  git push origin "$VERSION_TAG"
fi

RELEASE_URL=$(curl -H \
  "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/nasa/cumulus-process-py/releases/tags/$VERSION_TAG | jq --raw-output '.url // ""')
export RELEASE_URL

if [ -z "$RELEASE_URL" ]; then
  echo "release does not exist"

  curl -H \
    "Authorization: token $GITHUB_TOKEN" \
    -d "{\"tag_name\": \"$VERSION_TAG\", \"name\": \"$VERSION_TAG\", \"body\": \"Release $VERSION_TAG\" }"\
    -H "Content-Type: application/json"\
    -X POST \
    https://api.github.com/repos/nasa/cumulus-process-py/releases
fi
