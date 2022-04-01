install:
	pip install poetry
	poetry install

update:
	poetry update

lint:
	isort --check ynab_import tests
	black --check ynab_import tests
	flake8 ynab_import tests
	#mypy ynab_import tests
	safety check --full-report

fmt:
	isort ynab_import tests
	black ynab_import tests

test:
	python -m pytest