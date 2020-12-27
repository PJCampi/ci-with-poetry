#!/usr/bin/env bash
set -euo pipefail

# install poetry
echo install requirements
"${PYTHON:=python}" -m pip install -r "$(dirname "$0")"/requirements.txt

# create virtual env and install dependencies
echo create poetry environment
cd "$(dirname "$0")/../.."
poetry install
