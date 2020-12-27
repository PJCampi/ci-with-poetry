# Build and release with Poetry
This project is an example of my build and release setup.

It leverages on the python package `poetry` and `git` for the heavy lifting..

## Features
The framework relies on auto-generated `git` tags to control the version of package being 
published. A version is never committed to the repository.

The versioning framework follows git-flow with `master`, `develop`, `release/v*` and `hotfix` branches. We also 
follow semantic versioning. Versions on release and master branches are automatically incremented
(as `M.m.p` and `M.m.p-rc{i}`). Versions on `develop` and `hotfix` branches are tagged by setting the environment variable: 
`COMMIT_TAG` (as `M.m.p-alpha+{commit hash}` and `M.m.p-post+{commit hash}`).

If the commit is tagged with a version, a package is built. It is published using the environment variable `PUBLISH`. 

## How to setup
Your continuous integration setup just needs to run the command `make` on the root of the directory. It is important to 
start with a clean repository (clean `git` directory).