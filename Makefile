include ./VERSION

default: all

all: zip ankiweb

zip: src/version.py src/config_schema.py vendor
	python -m ankiscripts.build --type package --qt all --exclude user_files/**/*

ankiweb: src/version.py src/config_schema.py vendor build/ankiweb-description.md
	python -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**/*

build/ankiweb-description.md: description.md CHANGELOG.md
	cat description.md CHANGELOG.md >$@

src/version.py: ./VERSION
	@echo "__version__ = '$(VERSION)'" >$@

src/config_schema.py: ./src/config-new.schema.json
	datamodel-codegen \
		--input=$< \
		--input-file-type=jsonschema \
		--output-model-type=typing.TypedDict \
		--class-name=ConfigSchema | sed -e "s/    /\t/g" >$@

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
	rm -rf build/ src/version.py src/config_schema.py

.PHONY: all zip ankiweb vendor fix mypy pylint lint test sourcedist clean
