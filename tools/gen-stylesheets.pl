#! /usr/bin/env perl

use strict;

my @board_images_2d = glob 'assets/images/2d/board/*.*';
push @board_images_2d, glob 'assets/images/2d/board/svg/*.svg';
my %board_images_2d = map { $_ => 1 } @board_images_2d;

my %snippets_images_2d;
my %snippets_last_move;

foreach my $img (keys %board_images_2d) {
	next if ($img =~ /\..*\./);

	my $style = $img;
	$style =~ s{.*/}{};
	$style =~ s{\..*$}{};

	my $path = $img;
	$path =~ s/^assets/./;

	my $snippet = <<"EOF";
chess-wrapper.$style cg-wrap {
	background-image: url('$path');
}
EOF

	$snippets_images_2d{$style} = $snippet;
}

print "// This file is generated! Do NOT edit!\n\n";

print join "\n", map { $snippets_images_2d{$_} } sort keys %snippets_images_2d;
