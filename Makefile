.PHONY: clean lint blacken test docs help  release
.DEFAULT_GOAL := help

SHELL := /bin/bash

VERSION := 0.1.22

define HELP_MESSAGE
make clean: clean up build files
make lint: run flake8 checks
make test: to run tests
endef

help:
	$(info $(HELP_MESSAGE))

clean: clean-build clean-pyc  ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

blacken: ## use black to reformat files
	( \
		source .venv/bin/activate; \
		pip install -e .[dev]; \
		nox -s blacken; \
	)

lint: ## check style with flake8
	( \
		source .venv/bin/activate; \
		pip install -e .[dev]; \
		nox -s lint; \
	)

test: ## run tests quickly with the default Python
	rm -rf .venv
	python3 -m venv .venv
	( \
		source .venv/bin/activate; \
		pip install -e .[dev]; \
		nox -s test; \
	)

coverage: ## check code coverage quickly with the default Python
	coverage run --source treecrawl -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/treecrawl.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ treecrawl
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

dist: clean ## builds source and wheel package
	rm -rf .venv
	python3 -m venv .venv
	( \
		source .venv/bin/activate; \
		pip install -e .[dev]; \
		python setup.py sdist bdist_wheel; \
	)


release: dist ## package and upload a release
	twine upload --repository testpypi dist/*
