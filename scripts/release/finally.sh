#!/usr/bin/env bash
cd "$(dirname "$0")"

echo cleaning up build directories
clean.sh

echo reset version to 0.0.0
"${PYTHON:=python}" -m version add "0.0.0"
