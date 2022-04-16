install: # Install dependencies
	pip install poetry
	poetry install

activate: # Activate python enviroment
	poetry shell

lint: # Check code quality
	isort --check ynab_import tests
	black --check ynab_import tests
	flake8 ynab_import tests
	#mypy ynab_import tests
	safety check --full-report

fmt: # Format code
	isort ynab_import tests
	black ynab_import tests

test: # Run tests
	python -m pytest