PY=poetry run

.PHONY: install test test-ci test-quiet

install:
	poetry install

test:
	$(PY) pytest -q

test-quiet:
	$(PY) pytest -q -k "not slow"

test-ci:
	$(PY) pytest -q --maxfail=1 --disable-warnings
