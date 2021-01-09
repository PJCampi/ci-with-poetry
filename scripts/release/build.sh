#!/usr/bin/env bash
set -euo pipefail

# navigate to the current directory
cd "$(dirname "$0")"

# build python package
"${PYTHON:=python}" -m version add ${1}

echo build package
poetry build --format wheel
