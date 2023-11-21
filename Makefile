default: all

all: zip ankiweb

zip: vendor
	python -m ankiscripts.build --type package --qt all --exclude user_files/**/*

ankiweb: vendor
	python -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**/*

vendor:
	python -m ankiscripts.vendor

fix:
	python -m yapf src tests --recursive --exclude="forms|vendor"
	python -m isort src tests

mypy:
	-python -m mypy src tests

pylint:
	-python -m pylint src tests

lint: mypy pylint

test:
	python -m  pytest --cov=src --cov-config=.coveragerc

sourcedist:
	python -m ankiscripts.sourcedist

clean:
	rm -rf build/

.PHONY: all zip ankiweb vendor fix mypy pylint lint test sourcedist clean
