#!/usr/bin/env bash
set -euo pipefail

REPOSITORY=${REPOSITORY:-""}
PUBLISH=${PUBLISH:-"false"}

# get current commit tag
COMMIT_HASH=$(git rev-parse --short HEAD)
CURRENT_TAG=$("$(dirname "$0")"/get_version_tag.sh $COMMIT_HASH)

# build and publish if the commit was tagged with a version
if [[ "$CURRENT_TAG" != "" ]]
then

  echo adding version: $CURRENT_TAG to package
  "$(dirname "$0")"/add_version.sh $CURRENT_TAG

  echo build package
  poetry build --format wheel

  echo publish package "$(if [[ "$PUBLISH" != "true" ]]; then echo "in dry-run mode"; fi)"
  PUBLISH_ARGS=" --username $REPOSITORY_USERNAME --password $REPOSITORY_PASSWORD"
  if [[ "$REPOSITORY" != "" ]]; then PUBLISH_ARGS+=" --repository $REPOSITORY"; fi
  if [[ "$PUBLISH" != "true" ]]; then PUBLISH_ARGS+=" --dry-run"; fi
  poetry publish $PUBLISH_ARGS

else
  echo the package will not be published because no version was provided.
fi
