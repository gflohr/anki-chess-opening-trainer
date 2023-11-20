#! /bin/sh

. VERSION

ZIP="${ZIP:-zip}"

filename=chess-opening-trainer-$VERSION.ankiaddon
sources=*.py
additional=addon.json manifest.json config.json config.md

rm -f $filename
"$ZIP" $filename $sources $additional -x update-anki-deck.py
