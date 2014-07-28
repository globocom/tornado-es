all: help

help:
	@echo "Usage: make test -- Runs tests."

setup:
	pip install -r test-requirements.txt

clean:
	@echo "Cleaning up build and *.pyc files..."
	@find . -name '*.pyc' -exec rm -rf {} \;
	@rm -rf .coverage
	@rm -rf ./build
	@rm -rf ./dist
	@rm -rf ./MANIFEST
	@echo "Done!"

bulk:
	# creates test data
	@./run bulk

test: clean unit

unit:
	@coverage run --branch `which nosetests` -vv --with-yanc -s tornadoes/tests/
	@coverage report -m --fail-under=80

coverage-html: unit
	@coverage html -d cover

tox:
	@tox
