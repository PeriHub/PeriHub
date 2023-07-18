# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

PROGRAM_VERSION = $(lastword $(shell poetry version --no-ansi))
ALL_PYTHON_FILES = $(shell find src/gcodereader test doc -type f -name "*.py")


all: audit

clean:
	rm -rf build
	poetry run coverage erase

prepare:
	mkdir -p build

test: prepare
	poetry run pytest --doctest-modules --junit-xml=build/tests.xml

formatting:
	poetry run black .
	poetry run isort .

license-metadata:
	poetry run reuse addheader --copyright="German Aerospace Center (DLR)" --license="MIT" $(ALL_PYTHON_FILES)
	poetry run black .

check-formatting:
	poetry run black . --check
	poetry run isort . --check-only

check-license-metadata:
	poetry run reuse lint

check-code: prepare
	poetry run pflake8 . --exit-zero --output-file=build/flake8.txt

check-coverage: prepare
	poetry run pytest --cov=. --cov-fail-under=30 --cov-report=term-missing --cov-report=html:build/html --cov-report=xml:build/coverage.xml

check-security:
	poetry run bandit -r .
	poetry run bandit -r -ll .

audit: check-code check-coverage check-formatting #check-license-metadata check-security

docs: prepare
	poetry run sphinx-apidoc . --force --output-dir=doc/
	poetry run sphinx-build -w build/sphinxwarn.txt -D version="$(PROGRAM_VERSION)" -D release="$(PROGRAM_VERSION)" -b html doc/ build/html/

doc: docs

run-local:
	PYTHONPATH=src uvicorn app:app --reload

.PHONY: list
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
