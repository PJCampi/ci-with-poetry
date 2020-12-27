#!/usr/bin/env bash
set -euo pipefail

# get the short hash of the current commit
COMMIT_HASH=$(git rev-parse --short HEAD)
echo the current commit short hash is: $COMMIT_HASH

# get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref --symbolic-full-name HEAD)
if [[ "$CURRENT_BRANCH" == "HEAD" ]]
then
  echo it is not possible to infer the version of a detached commit. commit short hash: $COMMIT_HASH
  exit 1
else
  echo the current branch name is: $CURRENT_BRANCH
fi

# get the highest version tag of the current commit
CURRENT_TAG=$("$(dirname "$0")"/get_version_tag.sh $COMMIT_HASH)
echo the current commit version tag is: $CURRENT_TAG

# get the highest version tag of the latest tag
LATEST_TAG=$("$(dirname "$0")"/get_version_tag.sh "")
echo the highest version tag is: $LATEST_TAG

# determine the inferred version
INFERRED_VERSION=$(poetry run python "$(dirname "$0")"/infer_version_tag.py $CURRENT_BRANCH $COMMIT_HASH $CURRENT_TAG $LATEST_TAG)
echo the inferred version is: $INFERRED_VERSION

# tag the repository with the inferred version
COMMIT_TAG=${COMMIT_TAG:-$(if [[ $CURRENT_BRANCH =~ master|(release/v*) ]] ; then echo true; else echo false; fi)}
echo COMMIT_TAG was resolved to $COMMIT_TAG

if [[ $INFERRED_VERSION != "" ]] && [[ $INFERRED_VERSION != $CURRENT_TAG ]] && [[ $COMMIT_TAG == "true" ]]
then
  COMMIT_MESSAGE="tagging commit: $COMMIT_HASH with version: $INFERRED_VERSION"
  echo "$COMMIT_MESSAGE"
  git tag -a $INFERRED_VERSION -m "$COMMIT_MESSAGE"
  git push -f origin refs/tags/$INFERRED_VERSION
else
  echo "commit: $COMMIT_HASH is already tagged with version: $INFERRED_VERSION or COMMIT_TAG was resolved to false."
fi

