#!/usr/bin/env bash
set -euo pipefail

# we assume that the project has been initialized using poetry's init function
PACKAGE=$(echo "$(poetry version | cut -d " " -f 1)" | sed 's/-/_/g')
TEST_PACKAGE=tests

# navigate to project dir
cd "$(dirname "$0")/../.."

# run linters
echo run linters
poetry run mypy $PACKAGE $TEST_PACKAGE
poetry run flake8 $PACKAGE $TEST_PACKAGE

# run unit-tests
echo run tests in $TEST_PACKAGE directory
poetry run pytest $TEST_PACKAGE -q ${PYTEST_ARGS:=""}
