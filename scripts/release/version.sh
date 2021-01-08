#!/usr/bin/env bash
set -euo pipefail

# navigate to the current directory
cd "$(dirname "$0")"

# infer the version of the package
VERSION_ARGS=" --infer"
if [[ ${COMMIT_TAG:="false"} == "true" ]]
then
  INFERRED_VERSION=$("${PYTHON:=python}" -m version get --infer --include-alpha)
else
  INFERRED_VERSION=$("${PYTHON:=python}" -m version get --infer)
fi

# tag the version of the package on the current commit
if [[ $INFERRED_VERSION != "" ]]
then
  echo tagging the current commit with version: $INFERRED_VERSION
  "${PYTHON:=python}" -m version tag $INFERRED_VERSION --push
fi
