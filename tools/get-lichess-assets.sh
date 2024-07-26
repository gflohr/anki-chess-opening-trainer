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

echo '# This file is generated! Do not edit!' >src/image_paths.py
echo "import os" >src/image_paths.py
echo "from typing import List, Tuple" >>src/image_paths.py
echo >>src/image_paths.py
echo "_script_dir = os.path.dirname(os.path.abspath(__file__))" >>src/image_paths.py
echo "_images_dir = os.path.abspath(os.path.join(_script_dir, 'images'))" >>src/image_paths.py
echo >>src/image_paths.py

# Thumbnails for settings dialogue.
rm -f src/images/2d/piece/*
echo "directory = os.path.join(_images_dir, '2d', 'piece')" >>src/image_paths.py
echo "piece_images_2d: List[Tuple[str, str]] = [" >>src/image_paths.py
for dir in lila/public/piece/*; do
	piece=`basename $dir`
	if test $piece != mono; then
		cp $dir/bN.svg src/images/2d/piece/$piece.svg
		echo "	(os.path.join(directory, '$piece.svg'), '$piece')," >>src/image_paths.py
	fi
done
rm -f src/images/2d/piece/mono.svg
echo "]" >>src/image_paths.py

echo >>src/image_paths.py
rm -f src/images/2d/board/*
echo "directory = os.path.join(_images_dir, '2d', 'board')" >>src/image_paths.py
echo "board_images_2d: List[Tuple[str, str]] = [" >>src/image_paths.py
for thumb in assets/images/2d/board/*.thumbnail.*; do
	cp $thumb src/images/2d/board
	filename=`echo $thumb | sed -e 's/.*\///'`
	name=`echo $filename | sed -e 's/\..*//'`
	echo "	(os.path.join(directory, '$filename'), '$name')," >>src/image_paths.py
done
echo "]" >>src/image_paths.py

echo >>src/image_paths.py
rm -f src/images/3d/piece/*
echo "directory = os.path.join(_images_dir, '3d', 'piece')" >>src/image_paths.py
echo "piece_images_3d: List[Tuple[str, str]] = [" >>src/image_paths.py
for dir in assets/images/3d/piece/*; do
	piece=`basename $dir`
	cp $dir/Black-Knight.png src/images/3d/piece/$piece.png
	echo "	(os.path.join(directory, '$piece.png'), '$piece')," >>src/image_paths.py
done
echo "]" >>src/image_paths.py

echo >>src/image_paths.py
rm -f src/images/3d/board/*
echo "directory = os.path.join(_images_dir, '3d', 'board')" >>src/image_paths.py
echo "board_images_3d: List[Tuple[str, str]] = [" >>src/image_paths.py
for thumb in assets/images/3d/board/*.thumbnail.*; do
	cp $thumb src/images/3d/board
	filename=`echo $thumb | sed -e 's/.*\///'`
	name=`echo $filename | sed -e 's/\..*//'`
	echo "	(os.path.join(directory, '$filename'), '$name')," >>src/image_paths.py
done
echo "]" >>src/image_paths.py

cat <<EOF >>src/image_paths.py
print(piece_images_2d)
print(board_images_2d)
print(piece_images_3d)
print(board_images_3d)
EOF

sh tools/consistency-check.sh || exit 1

rm -rf lila
