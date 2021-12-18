install:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	venv/bin/py.test -vv --cov-report term-missing:skip-covered --cov=gongish

.PHONY: install test
