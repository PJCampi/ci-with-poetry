#!/usr/bin/env bash
set -euo pipefail

# navigate to project directory
cd "$(dirname "$0")/../.."

# remove temporary files
rm -rf build dist .eggs *.egg-info
find . -type d -name '.mypy_cache' -exec rm -rf {} +
find . -type d -name '__pycache__' -exec rm -rf {} +
find . -type d -name '*pytest_cache*' -exec rm -rf {} +
find . -type f -name "*.py[co]" -exec rm -rf {} +
