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

print join "\n", map { $snippets_images_2d{$_} } sort keys %snippets_images_2d;

__END__

board_image_2d = glob('assets/images/2d/board/*.*')
board_image_thumbnails = glob('assets/images/2d/board/*.thumbnail.*')
board_image_2d = [img for img in board_image_2d if img not in board_image_thumbnails]
board_image_2d.extend(glob('assets/images/2d/board/svg/*.svg'))
board_image_2d = sorted(board_image_2d)

board_snippets: List[str] = []

for img in board_image_2d:
	if re.match('.*\\..*\\.', img):
		continue


	path = re.sub('^assets', '.', img)
	style = re.sub('.*/', '', img)
	style = re.sub('\..*?$', '', style)
	snippet = f'''chess-wrapper.{style} {{
	background-image: url({path});
}}
'''
	board_snippets.append(snippet)

print('\n'.join(snippets))
