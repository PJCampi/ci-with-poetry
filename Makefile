SHELL = /bin/sh

prepare: export PYTHON ?= python
version: export COMMIT_TAG ?=
publish: export PUBLISH ?=
publish: export REPOSITORY_USERNAME ?= $$USER
publish: export REPOSITORY_PASSWORD ?=
publish: export REPOSITORY ?=

all: publish

clean:
	@./scripts/release/clean.sh

prepare: clean
	@./scripts/release/prepare.sh

version: prepare
	@./scripts/release/version.sh

test: prepare
	@./scripts/release/test.sh

publish: version test
	@./scripts/release/publish.sh
