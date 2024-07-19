#! /bin/sh

set -e

rm -rf lila

git clone --depth=1 https://github.com/lichess-org/lila

rm -f assets/css/pieces/*.css
test -e assets/css/pieces || mkdir -p assets/css/pieces
cp -r lila/public/piece-css/*.css assets/css/pieces
rm -f assets/css/pieces/*.external.css

rm -f assets/images/2d/board/*.jpg
rm -f assets/images/2d/board/svg/*.svg
test -e assets/images/2d/board || mkdir -p assets/images/2d/board
cp -r lila/public/images/board/* assets/images/2d/board
rm -f assets/images/2d/board/*.orig.jpg

rm -rf assets/images/3d/*
test -e assets/images/3d || mkdir -p assets/images/3d
cp -r lila/public/images/staunton/* assets/images/3d

rm -rf lila
