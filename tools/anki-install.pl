#! /usr/bin/env perl

use strict;

use JSON qw(decode_json);

sub copy_index_html;
sub get_addon_id;
sub patch_stylesheet;

my $id = get_addon_id;

copy_index_html $id;
patch_stylesheet $id;

sub copy_index_html {
	my ($id) = @_;

	open my $fh, '<', 'dist/index.html' or die;

	my $contents = join '', <$fh>;

	$contents =~ m{(<script .*?/assets/index-.*?</script>)} or die;
	my $script = $1;
	$script =~ s{/assets/index-}{/_addons/$id/assets/index-};

	$contents =~ m{(<link rel="stylesheet".*?/assets/index-.*?>)} or die;
	my $stylesheet = $1;
	$stylesheet =~ s{/assets/index-}{/_addons/$id/assets/index-};

	$contents =~ s{<link rel="stylesheet".*?/assets/css/pieces/.*?>}{} or die;
	$contents =~ s{/assets/}{/_addons/$id/assets/}g;

	$contents =~ s{(\n[ \t]*)const prefix = .*?\n}{$1const prefix='/_addons/$id';\n};

	mkdir 'src/assets/html';

	# Save index.html as is.
	open my $fh_index, '>', 'src/assets/html/index.html' or die;
	$fh_index->print($contents);

	$contents =~ s/(\n[ \t]*)const line = .*?\n([ \t]*const)/$1const line = {{ Line }};\n$2/s;

	# Extract snippet from index.html.
	$contents =~ s/.*<!-- BEGIN_PAGE -->\n//s or die;
	$contents =~ s/[ \t]*<!-- END_PAGE -->.*//s or die;
	$contents = join "\n", $stylesheet, $contents, $script;

	open my $fh_page, '>', 'src/assets/html/page.html' or die;
	$fh_page->print($contents);

	unlink 'src/index.html';

	return 1;
}

sub patch_stylesheet {
	my ($id) = @_;

	my @stylesheets = <src/assets/index-*.css>;

	die if @stylesheets != 1;

	open my $fh, '<', $stylesheets[0];
	my $style = join '', <$fh>;

	return 1 if $style =~ m{/_addons/$id/assets/};

	$style =~ s{/assets/}{/_addons/$id/assets/}g;

	open my $fh, '>', $stylesheets[0] or die;
	$fh->print($style);

	return 1;
}

sub get_addon_id {
	open my $fh, '<', 'addon.json' or die;

	my $json = join '', <$fh>;
	my $data = decode_json $json;

	return $data->{ankiweb_id};
}
