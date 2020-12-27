#!/usr/bin/env bash
echo cleaning up build directories
"$(dirname "$0")"/clean.sh

echo reset all changes made to the repository
git reset --hard HEAD
