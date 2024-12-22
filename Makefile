.SILENT:

run:
	poetry run python src/main.py

lint:
	pylint -j$(shell nproc) $(shell git ls-files '*.py')
