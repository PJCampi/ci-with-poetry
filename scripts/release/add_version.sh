#!/usr/bin/env bash
PACKAGE=$(echo "$(poetry version | cut -d " " -f 1)" | sed 's/-/_/g')
VERSION_FILE="$(dirname "$0")/../../$PACKAGE/__init__.py"
poetry version ${1} -q
sed -i.bak "s/0.0.0/${1}/" "$VERSION_FILE" && rm "$VERSION_FILE.bak"
