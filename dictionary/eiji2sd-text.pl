#!/usr/bin/perl

use strict;
use utf8;
use feature qw(fc);
use bytes ();

use File::Basename;
use Encode qw(find_encoding);

my $file = $ARGV[0];
my %data;
my ($ifo, $idx, $dict) = map {'stardict.' . $_} qw(ifo idx dict);

open my $input, '<:encoding(cp932)', $file or die $!;

$|++;

my $word_count1 = 0;

while ( my $line = <$input> ) {

    chomp $line;

    my ($word, $content) = split /\ :\ /, $line, 2;
    $word =~ s/^■//;

    my $part = undef;
    my $order = 0;

    if ($word =~ s/\s*{(.+?)}\s*//) {
        $part = $1;
        $part =~ s/^(\d+)\-//;
        $part =~ s/\-\d+$//;
        if ($part =~ /^\d+$/) {
            $part = undef;
        }
    }

    next if length($word) == 1;
    next if bytes::length($word) > 255; # StarDictの制限

    my ($meaning, @extra) = split /(?=◆|■・)/, $content;
    $meaning =~ s/｛.+?｝//g;

    my (@note, @example);

    foreach my $text (@extra) {
        if ($text =~ s/^◆//) {
            push @note, $text;
        }
        elsif ($text =~ s/^■・//) {
            push @example, $text;
        }
    }

    my $data = {
        part    => $part,
        meaning => $meaning,
        note    => \@note,
        example => \@example,
        next    => []
    };

    if ( exists $data{$word} ) {
        push @{ $data{$word}->{'next'} }, $data;
    }
    else {
        $data{$word} = $data;
        $word_count1++;
    }

    if ( ($word_count1 % 10000) == 0 ) {
        printf "Now reading: %20s\r", pack('A20', $word);
    }

}

my $offset = 0;
my $utf8_enc = find_encoding('UTF-8');

open my $idx_out,  '>:raw', $idx  or die $!;
open my $dict_out, '>:raw', $dict or die $!;

my $buffer;

sub append { $buffer .= join '', @_; }

sub append_part {
    my ($data, $word) = @_;
    if ( defined $data->{'part'} ) {
        append( '【', $data->{'part'}, "】" );
    }
    append($word, "\n");
}

sub append_extra {
    my $data = shift;
    if ( 0 != @{$data->{'note'}} or 0 != @{$data->{'example'}} ) {
        append( map { "\t" . $_ . "\n" } @{$data->{'note'}}, @{$data->{'example'}} );
    }
}

my $word_count2 = 0;

print "\nSorting...\n";

foreach my $word (sort { fc($a) cmp fc($b) } keys %data) {

    $word_count2++;
    my $data = $data{$word};

    $buffer = '';
    append_part($data, $word);
    my $current_part = $data->{'part'};
    append( $data->{meaning}, "\n" );
    append_extra($data);

    foreach my $next ( @{$data->{'next'}} ) {
        if ( $current_part ne $next->{'part'} ) {
            append_part($next, $word);
            $current_part = $next->{'part'};
        }
        append( $next->{meaning}, "\n" );
        append_extra($next);
    }

    my $text = $utf8_enc->encode($buffer);
    my $len = bytes::length($text);

    print $idx_out pack 'Z*NN', $utf8_enc->encode($word), $offset, $len;
    print $dict_out $text;
    $offset += $len;

    if ( ($word_count2 % 5000) == 0 ) {
        printf "Writing dictionary: %3u%% %20s\r", ($word_count2 / $word_count1 * 100), pack('A20', $word);
    }
}

close $idx_out;
close $dict_out;

my $idx_fsize = -s $idx;
open my $ifo_out, '>:raw', $ifo or die $!;

print $ifo_out $utf8_enc->encode(<<"IFO");
StarDict's dict ifo file
version=2.4.2
bookname=英辞郎
wordcount=$word_count1
idxfilesize=$idx_fsize
sametypesequence=m
IFO

close $ifo_out;
print "\nDone.\n";
