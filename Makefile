include ./VERSION

default: all

all: zip ankiweb

zip: src/version.py vendor
	python -m ankiscripts.build --type package --qt all --exclude user_files/**/*

ankiweb: src/version.py vendor build/ankiweb-description.md
	python -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**/*

build/ankiweb-description.md: description.md CHANGELOG.md
	cat description.md CHANGELOG.md >$@

src/version.py: ./VERSION
	@echo "__version__ = '$(VERSION)'" >$@

vendor:
	python -m ankiscripts.vendor

fix:
	python -m yapf src tests *.py --recursive --in-place
	python -m isort src tests *.py

mypy:
	# See https://github.com/python/mypy/issues/8727
	-python -m mypy src tests *.py --exclude=src/vendor --exclude=src/forms \
		--check-untyped-defs --disable-error-code name-defined

pylint:
	-python -m pylint src tests *.py

lint: mypy pylint

test:
	python -m  pytest --cov=src --cov-config=.coveragerc

sourcedist:
	python -m ankiscripts.sourcedist

clean:
	rm -rf build/

.PHONY: all zip ankiweb vendor fix mypy pylint lint test sourcedist clean
