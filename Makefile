default: all

all: zip ankiweb

generated: \
	src/version.py \
	src/config_schema.py \
	src/config.py \
	src/importer_config_schema.py \
	src/importer_config.py

zip: generated vendor
	python -m ankiscripts.build --type package --qt all --exclude user_files/**/*

ankiweb: generated vendor build/ankiweb-description.md
	python -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**/*

build/ankiweb-description.md: description.md CHANGELOG.md
	cat description.md CHANGELOG.md >$@ || (rm $@; exit 1)

src/version.py: ./package.json
	python3 ./tools/get-version.py >$@ || (rm $@; exit 1)

src/config.py: ./src/config.schema.json
	datamodel-codegen \
		--input=$< \
		--input-file-type=jsonschema \
		--output-model-type=typing.TypedDict \
		| sed -e "s/    /\t/g" >$@ || (rm $@; exit 1)

src/importer_config.py: ./src/importer_config.schema.json
	datamodel-codegen \
		--input=$< \
		--input-file-type=jsonschema \
		--output-model-type=typing.TypedDict \
		| sed -e "s/    /\t/g" >$@ || (rm $@; exit 1)

src/importer_config_schema.py: ./src/importer_config.schema.json
	python3 ./tools/json2python.py importer_config_schema <$< >$@ || (rm $@; exit 1)

src/config_schema.py: ./src/config.schema.json
	python3 ./tools/json2python.py config_schema <$< >$@ || (rm $@; exit 1)

vendor:
	python -m ankiscripts.vendor

fix:
	python -m yapf src --recursive --in-place
	python -m isort src

mypy:
	# See https://github.com/python/mypy/issues/8727
	-python -m mypy src --exclude=src/vendor --exclude=src/forms \
		--check-untyped-defs --disable-error-code name-defined

pylint:
	-python -m pylint src

lint: mypy pylint

test:
	python -m  pytest --cov=src --cov-config=.coveragerc

sourcedist:
	python -m ankiscripts.sourcedist

update-assets:
	sh ./tools/get-lichess-assets.sh

clean:
	rm -rf \
		build/ src/version.py \
		src/config.py src/config_schema.py \
		src/importer_config.py src/importer_config_schema.py

.PHONY: all zip ankiweb vendor fix mypy pylint lint test sourcedist \
	update-assets clean
