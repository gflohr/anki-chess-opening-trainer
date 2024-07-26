#! /usr/bin/env perl

use strict;

my @board_images_2d = glob 'assets/images/2d/board/*.*';
push @board_images_2d, glob 'assets/images/2d/board/svg/*.svg';
my %snippets_images_2d;

foreach my $img (@board_images_2d) {
	next if ($img =~ /\..*\./);

	my $style = $img;
	$style =~ s{.*/}{};
	$style =~ s{\..*$}{};
	next if $style eq 'ncf-board';

	my $path = $img;
	$path =~ s/^assets/../;

	my $snippet = <<"EOF";
.is2d.cot-board-$style .cg-wrap {
	background-image: url($path);
}
EOF

	$snippets_images_2d{$style} = $snippet;
}

my @board_images_3d = glob 'assets/images/3d/board/*.*';
my %snippets_images_3d;

foreach my $img (@board_images_3d) {
	next if ($img =~ /\..*\./);

	my $style = $img;
	$style =~ s{.*/}{};
	$style =~ s{\..*$}{};

	my $path = $img;
	$path =~ s/^assets/../;

	my $snippet = <<"EOF";
.is3d.cot-board-$style .cg-wrap {
	background-image: url($path);
}
EOF

	$snippets_images_3d{$style} = $snippet;
}

my @pieces_styles_3d = glob 'assets/images/3d/piece/*';
my %snippets_pieces_3d;

foreach my $styledir (@pieces_styles_3d) {
	my $style = $styledir;
	$style =~ s{.*/}{};

	my @pieces_files = glob "$styledir/*.*";
	my %pieces = map { s{.*/}{}; $_ => 1 } @pieces_files;
	foreach my $img (glob "$styledir/*.*") {
		next if ($img =~ /-Preview/);
		next if ($img =~ /-Flipped/);

		$img =~ s{.*/}{};

		my ($Colour, $Piece, $ext) = split /[-.]/, $img;
		my $colour = lc $Colour;
		my $piece = lc $Piece;

		if (exists $pieces{"$Colour-$Piece-Flipped.$ext"}) {
			my $selector = ".is3d.pieces-$style .cg-wrap.orientation-white .$colour.$piece";
			my $flipped = $colour eq 'black' ? '-Flipped' : '';
			my $snippet = <<"EOF";
$selector {
	background-image: url(/assets/images/3d/piece/$style/$Colour-$Piece$flipped.$ext);
}
EOF
			$snippets_pieces_3d{$selector} = $snippet;

			$selector = ".is3d.pieces-$style .cg-wrap.orientation-black .$colour.$piece";
			$flipped = $colour eq 'white' ? '-Flipped' : '';
			$snippet = <<"EOF";
$selector {
	background-image: url(/assets/images/3d/piece/$style/$Colour-$Piece$flipped.$ext);
}
EOF
			$snippets_pieces_3d{$selector} = $snippet;
		} else {
			my $selector = ".is3d.pieces-$style .cg-wrap .$colour.$piece";
			my $snippet = <<"EOF";
$selector {
	background-image: url(/assets/images/3d/piece/$style/$Colour-$Piece.$ext);
}
EOF
			$snippets_pieces_3d{$selector} = $snippet;
		}
	}
}

print "// This file is generated! Do NOT edit!\n\n";

print join "\n", map { $snippets_images_2d{$_} } sort keys %snippets_images_2d;
print join "\n", map { $snippets_images_3d{$_} } sort keys %snippets_images_3d;
print join "\n", map { $snippets_pieces_3d{$_} } sort keys %snippets_pieces_3d;
