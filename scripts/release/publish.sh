#!/usr/bin/env bash
set -euo pipefail

DISALLOW_LOCAL_VERSIONS=${DISALLOW_LOCAL_VERSIONS:-"true"}
REPOSITORY=${REPOSITORY:-""}
PUBLISH=${PUBLISH:-"false"}

# get current commit tag
COMMIT_HASH=$(git rev-parse --short HEAD)
CURRENT_TAG=$("$(dirname "$0")"/get_version_tag.sh $COMMIT_HASH)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref --symbolic-full-name HEAD)

# build and publish if the commit was tagged with a version
if [[ "$CURRENT_TAG" != "" ]]
then
    CURRENT_VERSION=${CURRENT_TAG:1}
    echo adding version: $CURRENT_VERSION to package
    "$(dirname "$0")"/add_version.sh $CURRENT_VERSION

    echo build package
    poetry build --format wheel

  if [[ "$CURRENT_TAG" =~ "+" ]] && [[ "$DISALLOW_LOCAL_VERSIONS" == "true" ]]
  then
    echo "version: $CURRENT_VERSION cannot be uploaded to $REPOSITORY because local versions f.ex. alpha and post releases are not allowed."
  else
    echo publish package "$(if [[ "$PUBLISH" != "true" ]]; then echo "in dry-run mode"; fi)"
    PUBLISH_ARGS=" --username $REPOSITORY_USERNAME --password $REPOSITORY_PASSWORD"
    if [[ "$REPOSITORY" != "" ]]; then PUBLISH_ARGS+=" --repository $REPOSITORY"; fi
    if [[ "$PUBLISH" != "true" ]]; then PUBLISH_ARGS+=" --dry-run"; fi
    poetry publish $PUBLISH_ARGS
  fi

else
  echo the package will not be published because no version was provided.
fi
