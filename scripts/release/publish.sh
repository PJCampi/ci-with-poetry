#!/usr/bin/env bash
set -euo pipefail

DISALLOW_LOCAL_VERSIONS=${DISALLOW_LOCAL_VERSIONS:-"true"}
REPOSITORY=${REPOSITORY:-""}
PUBLISH=${PUBLISH:-"false"}

# navigate to the current directory
cd "$(dirname "$0")"

# get current version
CURRENT_VERSION=$("${PYTHON:=python}" -m version get --include-alpha)

# build and publish if a version is available
if [[ "$CURRENT_VERSION" != "" ]]
then
  ./build.sh $CURRENT_VERSION
fi

# publish the package if the version is available
if [[ "$DISALLOW_LOCAL_VERSIONS" == "true" ]]
then
  CURRENT_VERSION=$("${PYTHON:=python}" -m version get)
fi

if [[ "$CURRENT_VERSION" != "" ]]
then
  echo publish package "$(if [[ "$PUBLISH" != "true" ]]; then echo "in dry-run mode"; fi)"
  PUBLISH_ARGS=" --username $REPOSITORY_USERNAME --password $REPOSITORY_PASSWORD"
  if [[ "$REPOSITORY" != "" ]]; then PUBLISH_ARGS+=" --repository $REPOSITORY"; fi
  if [[ "$PUBLISH" != "true" ]]; then PUBLISH_ARGS+=" --dry-run"; fi

  poetry publish $PUBLISH_ARGS

else
  echo the package will not be published because no version was provided.
fi
