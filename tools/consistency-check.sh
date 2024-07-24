#! /bin/sh

ls src/images/*/*/* | sed -e 's/^src.images.//' |
	sed -e 's/\..*//' |
	sort >got.txt

ls assets/css/*/*.css \
	assets/images/2d/board/*.* \
	assets/images/2d/board/svg/*.svg |
	grep -v '\..*\.' |
	sed -e 's/\/svg\//\//' |
	sed -e 's/^assets.images.//' |
	sed -e 's/^assets.css/2d/' |
	sed -e 's/\..*//' |
	sort >wanted.txt

diff -u wanted.txt got.txt || exit 1

rm -f got.txt wanted.txt
