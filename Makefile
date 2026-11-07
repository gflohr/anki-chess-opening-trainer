include ./VERSION

UV = uv
DATAMODEL_CODEGEN = $(UV) run datamodel-codegen
YAPF = $(UV) run yapf
ISORT = $(UV) run isort
MYPY = $(UV) run mypy
PYLINT = $(UV) run pylint
PYTEST = $(UV) run pytest
PYTHON = $(UV) run python
PNPM = pnpm

default: all

all: zip ankiweb

generated: src/version.py src/config.py src/schema.py src/basic_names.py

dist:
	$(PNPM) run build

src/web: dist
	rm -rf $@
	$(MAKE) dist
	cp -r dist $@
	rm $@/index.html $@/question.svg $@/answer*.svg

zip: generated vendor src/web
	$(PYTHON) -m ankiscripts.build --type package --qt all --exclude user_files/**/*

ankiweb: generated vendor build/ankiweb-description.md
	$(PYTHON) -m ankiscripts.build --type ankiweb --qt all --exclude user_files/**/*

build/ankiweb-description.md: description.md CHANGELOG.md
	cat description.md CHANGELOG.md >$@

src/version.py: ./VERSION
	@echo "__version__ = '$(VERSION)'" >$@

src/config.py: ./src/config.schema.json
	$(DATAMODEL_CODEGEN) \
		--input=$< \
		--input-file-type=jsonschema \
		--output-model-type=typing.TypedDict \
		| sed -e "s/    /\t/g" >$@

src/schema.py: ./src/config.schema.json
	$(PYTHON) ./tools/json2python.py <$< >$@

src/basic_names.py:
	sh ./tools/get-basic-notetype-names.sh >$@

vendor:
	$(PYTHON) -m ankiscripts.vendor

fix:
	$(PYTHON) -m yapf src --recursive --in-place
	$(PYTHON) -m isort src

mypy:
	# See https://github.com/python/mypy/issues/8727
	-$(PYTHON) -m mypy src --exclude=src/vendor --exclude=src/forms \
		--check-untyped-defs --disable-error-code name-defined

pylint:
	-$(PYTHON) -m pylint src

lint: mypy pylint

test: generated vendor
	$(PYTHON) -m  pytest --cov=src --cov-config=.coveragerc

sourcedist:
	$(PYTHON) -m ankiscripts.sourcedist

clean:
	rm -rf build/ src/version.py src/config.py

.PHONY: all zip ankiweb vendor fix mypy pylint lint test sourcedist clean
