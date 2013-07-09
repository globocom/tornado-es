all: help

help:
	@echo "Usage: make test -- Runs tests."

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

test: clean
	@python run_tests.py
