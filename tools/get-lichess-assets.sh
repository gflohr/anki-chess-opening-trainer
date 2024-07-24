#! /bin/sh

set -e

rm -rf lila

git clone --depth=1 https://github.com/lichess-org/lila

rm -f assets/css/piece/*.css
test -e assets/css/piece || mkdir -p assets/css/piece
cp -r lila/public/piece-css/*.css assets/css/piece
rm -f assets/css/piece/*.external.css

rm -f assets/images/2d/board/*.jpg
rm -f assets/images/2d/board/svg/*.svg
test -e assets/images/2d/board || mkdir -p assets/images/2d/board
cp -r lila/public/images/board/* assets/images/2d/board
rm -f assets/images/2d/board/*.orig.jpg

rm -rf assets/images/3d/*
test -e assets/images/3d || mkdir -p assets/images/3d
cp -r lila/public/images/staunton/* assets/images/3d

# Thumbnails for settings dialogue.
rm -f src/images/2d/piece/*
for dir in lila/public/piece/*; do
	piece=`basename $dir`
	test $piece != mono && cp $dir/bN.svg src/images/2d/piece/$piece.svg
done
rm -f src/images/2d/piece/mono.svg

rm -f src/images/2d/board/*
for thumb in assets/images/2d/board/*.thumbnail.*; do
	cp $thumb src/images/2d/board
done

rm -f src/images/3d/piece/*
for dir in assets/images/3d/piece/*; do
	piece=`basename $dir`
	cp $dir/Black-Knight.png src/images/3d/piece/$piece.png
done

rm -f src/images/3d/board/*
for thumb in assets/images/3d/board/*.thumbnail.*; do
	cp $thumb src/images/3d/board
done

rm -rf lila
