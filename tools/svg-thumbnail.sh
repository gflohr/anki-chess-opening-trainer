#! /bin/sh

svg=$1
outdir=$2

if test "x$outdir" = "x"; then
	exec 1>&2
	echo "Usage: SVG OUTDIR"
	exit 1
fi

set -e

outname=`echo "$svg" | sed -e 's/.*\///' -e 's/\.svg$/.thumbnail.png/'`
outfile="$outdir/$outname"

tmpname="temp.png"

rsvg-convert --width=256 --height=256 "$svg" >$tmpname
magick $tmpname -crop 64x32+0+0 $outfile
