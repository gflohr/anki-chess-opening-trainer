#! /usr/bin/env perl

use strict;

my @board_images_2d = glob 'assets/images/2d/board/*.*';
push @board_images_2d, glob 'assets/images/2d/board/svg/*.svg';
my %board_images_2d = map { $_ => 1 } @board_images_2d;

my %snippets_images_2d;

foreach my $img (keys %board_images_2d) {
	next if ($img =~ /\..*\./);

	my $style = $img;
	$style =~ s{.*/}{};
	$style =~ s{\..*$}{};

	my $path = $img;
	$path =~ s/^assets/../;

	my $snippet = <<"EOF";
.is2d.cot-board-$style .cg-wrap {
	background-image: url('$path');
}
EOF

	$snippets_images_2d{$style} = $snippet;
}

my @board_images_3d = glob 'assets/images/3d/board/*.*';
my %board_images_3d = map { $_ => 1 } @board_images_3d;

my %snippets_images_3d;

foreach my $img (keys %board_images_3d) {
	next if ($img =~ /\..*\./);

	my $style = $img;
	$style =~ s{.*/}{};
	$style =~ s{\..*$}{};

	my $path = $img;
	$path =~ s/^assets/../;

	my $snippet = <<"EOF";
.is3d.cot-board-$style .cg-wrap {
	background-image: url('$path');
}
EOF

	$snippets_images_3d{$style} = $snippet;
}

print "// This file is generated! Do NOT edit!\n\n";

print join "\n", map { $snippets_images_2d{$_} } sort keys %snippets_images_2d;
print join "\n", map { $snippets_images_3d{$_} } sort keys %snippets_images_3d;
