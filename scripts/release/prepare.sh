#!/usr/bin/env bash
set -euo pipefail

# install poetry
echo install requirements


# create virtual env and install dependencies
echo create poetry environment
cd "$(dirname "$0")/../.."
poetry install
