#! /bin/sh

set -e
#set -x

test -e anki-core-i18n || \
	git clone --depth=1 https://github.com/ankitects/anki-core-i18n

echo "basic_names = {"
grep '^notetypes-basic-name =' anki-core-i18n/core/*/*.ftl \
	| sed -e "s/^anki-core-i18n.core.//" \
	| sed -e "s/^/\t'/" \
	| sed -e "s/\/.*notetypes-basic-name = /': '/" \
	| sed -e "s/\$/',/"
echo "}"

rm -rf anki-core-i18n
