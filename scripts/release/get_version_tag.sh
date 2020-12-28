#!/usr/bin/env bash
set -euo pipefail

VERSION_PATTERN="v[0-9]*.[0-9]*.[0-9]*"
MAX_CANDIDATE_TAGS=25

HASHES=${1:-"$(git log --simplify-by-decoration --format=format:%h --max-count=$MAX_CANDIDATE_TAGS)"}
TAGS=$(echo "$HASHES" | xargs -L1 git tag --list $VERSION_PATTERN --points-at | xargs | sed "s/ /,/g")
TAG=$(poetry run python "$(dirname "$0")"/version.py latest ${TAGS})

echo $TAG
