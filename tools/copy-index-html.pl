#! /usr/bin/env perl

use strict;

open my $fh, '<', 'dist/index.html' or die;

my $contents = join '', <$fh>;

$contents =~ m{(<script .*?/assets/index-.*?</script>)} or die;
my $script = $1;
$script =~ s{/assets/index-}{/_addons/{{addon}}/assets/index-};

$contents =~ m{(<link rel="stylesheet".*?/assets/index-.*?>)} or die;
my $stylesheet = $1;
$stylesheet =~ s{/assets/index-}{/_addons/{{addon}}/assets/index-};

$contents =~ s/.*<!-- BEGIN_PAGE -->\n//s or die;
$contents =~ s/[ \t]*<!-- END_PAGE -->.*//s or die;

$contents = join "\n", $stylesheet, $contents, $script;

mkdir 'src/assets/html' or die;

open my $fh, '>', 'src/assets/html/page.html' or die;
$fh->print($contents);

unlink 'src/index.html';
