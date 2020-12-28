#!/usr/bin/env bash
COMMIT_MESSAGE="tagging commit: ${2} with version: ${1}"
echo "$COMMIT_MESSAGE"
git tag -a ${1} -m "$COMMIT_MESSAGE"
git push -f origin refs/tags/${1}
