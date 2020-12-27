#!/usr/bin/env bash
echo cleaning up build directories
"$(dirname "$0")"/clean.sh

echo reset version to 0.0.0
"$(dirname "$0")"/add_version.sh "0.0.0"
