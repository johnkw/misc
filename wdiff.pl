#!/usr/bin/perl -w

# Script to add word-based colors to `diff -u` output.
# Use: `diff -u a b | wdiff.pl` or `wdiff.pl < patch.txt`.

use strict;
use warnings;
use Carp;
use Algorithm::Diff ();
use Data::Dumper;
use Getopt::Std;

my $curcol = -1;
my %args;

sub main();
main();

sub col($$);
sub col($$) {
    my ($msg, $col) = @_;
    return if $msg eq '';

    if ($col != $curcol) {
        $curcol = $col;
        if ($col == 0) {
            print "\x1b[0m";
        } else {
            print "\x1b[7;3".$col."m";
        }
    }
    $msg = " \n" if ($msg eq "\n"); # just to have something visible
    print $msg;
}

sub dbg(@) {
    return if !$args{'d'};
    my (undef, undef, $line) = caller;
    my $foo = Dumper(@_);
    $foo =~ s/',\n\s+/', /g;
    $foo =~ s/\[\n\s+/\[ /g;
    $foo =~ s/\],\n\s+/\], /g;
    $foo =~ s/ {10}/       /g;
    $foo =~ s/\$VAR/$line /g;
    print $foo;
}

sub mysplit($$) {
    my ($reg, $val) = @_;
    my @ret;
    my $i = 0;
    foreach (split(/([$reg])/, $val)) {
            push(@ret, $_);
    }
    #print "split: ".Dumper \@ret;
    return \@ret;
}

sub canonicalize_doubles_blanks($) {
    my ($diffs) = @_;
    # canonicalize double-X's and blank -/+'s
    for (my $i = 0; $i < scalar(@$diffs) - 1; ) {
        if ($$diffs[$i][0] eq $$diffs[$i+1][0]) {
            $$diffs[$i][1] .= $$diffs[$i+1][1];
            splice(@$diffs, $i+1, 1);
        } elsif (($$diffs[$i][0] =~ /d|a/) && ($$diffs[$i][1] eq '')) {
            splice(@$diffs, $i, 1);
        } elsif (($$diffs[$i][0] eq 'a') && ($$diffs[$i+1][0] eq 'd')) {
            my $t = $$diffs[$i];
            splice(@$diffs, $i,   1, $$diffs[$i+1]);
            splice(@$diffs, $i+1, 1, $t);
        } else {
            $i++;
        }
    }
    dbg($diffs);
}

sub diff($$$);
sub diff($$$) {
    my ($del, $add, $inregs) = @_;
    my @regs = @$inregs;
    my $reg = shift(@regs);
    if (@regs) {
        $regs[0] .= $reg;
    }

    dbg($del, $add, $reg);

    # canonicalize the c's into -/+
    my @diffs;
    foreach my $sd (Algorithm::Diff::sdiff(mysplit($reg, $del), mysplit($reg, $add))) {
        if ($$sd[0] eq 'u') {
            if ($$sd[1] ne '') {
                push(@diffs, [ 'u', $$sd[1] ]);
            }
        } elsif ($$sd[0] eq 'c') {
            die if ($$sd[1] eq '' && $$sd[2] eq '');
            push(@diffs, [ 'd', $$sd[1] ]);
            push(@diffs, [ 'a', $$sd[2] ]);
        } elsif ($$sd[0] eq '-') {
            push(@diffs, [ 'd', $$sd[1] ]);
        } elsif ($$sd[0] eq '+') {
            push(@diffs, [ 'a', $$sd[2] ]);
        } else {
            Carp::confess(Dumper $sd);
        }
    }
    dbg(\@diffs);

    for (;;) {
        my $size = scalar(@diffs);

        canonicalize_doubles_blanks(\@diffs);

        # weed out unreadable short u's
        for (my $i = 1; $i < scalar(@diffs) - 1; ) {
            if (
                   ($diffs[$i][0] eq 'u')
                && (($diffs[$i][1] !~ /\n/ && (length($diffs[$i][1]) <= 2)) || $diffs[$i][1] =~ /^\s+$/)
            ) {
                if ($diffs[$i-1][0] ne $diffs[$i+1][0]) {
                    $diffs[$i-1][1] .= $diffs[$i][1];
                    $diffs[$i+1][1] = $diffs[$i][1] . $diffs[$i+1][1];
                    splice(@diffs, $i, 1);
                    dbg(\@diffs);
                    last;
                } elsif (($i > 1) && ($diffs[$i-1][0] eq $diffs[$i+1][0] && ($diffs[$i-2][0]) =~ /a|d/)) {
                    $diffs[$i-2][1] .= $diffs[$i][1];
                    $diffs[$i-1][1] .= $diffs[$i][1];
                    splice(@diffs, $i, 1);
                    dbg(\@diffs, $i);
                    last;
                } elsif (($i + 2 < scalar @diffs) && ($diffs[$i+1][0] ne $diffs[$i+2][0] && ($diffs[$i+2][0]) =~ /a|d/)) {
                    $diffs[$i+1][1] = $diffs[$i][1] . $diffs[$i+1][1];
                    $diffs[$i+2][1] = $diffs[$i][1] . $diffs[$i+2][1];
                    splice(@diffs, $i, 1);
                    dbg(\@diffs, $i);
                    last;
                } else {
                    $i++;
                }
            } else {
                $i++;
            }
        }
        dbg(\@diffs);

        last if $size == scalar(@diffs);
    }

    # output
    {
        my ($adds, $dels) = ('', '');
        foreach my $sd (@diffs) {
            if ($$sd[0] eq 'u') {
                if (@regs) {
                    diff($dels, $adds, \@regs);
                } else {
                    col($dels, 1);
                    col($adds, 2);
                }
                ($adds, $dels) = ('', '');
                col($$sd[1], 0);
            } elsif ($$sd[0] eq 'd') {
                $dels .= $$sd[1];
            } elsif ($$sd[0] eq 'a') {
                $adds .= $$sd[1];
            } else {
                Carp::confess(Dumper $sd);
            }
        }

        if (@regs) {
            diff($dels, $adds, \@regs);
        } else {
            col($dels, 1);
            col($adds, 2);
        }
    }
}

sub main() {
    if (!getopts("d", \%args)) {
        die "-d - debug\n";
    }

    sub showdiffs($$) {
        if ($_[0] || $_[1]) {
            diff($_[1], $_[0], ['|\n \t\"\';\$\%', ',<>\@_:\.\[\]()\'\\\/!{}']);
        }
    }

    my ($alines, $dlines) = ('', '');
    while (my $line = <STDIN>) {
        if ($line =~ /^===================================================================/ .. $line =~ /^\+\+\+/) {
            col($line, 0);
            next;
        }
        $line =~ s/\t/    /g;
        if ($line =~ /^\+([\s\S]*)/) {
            $alines .= ' '.$1;
        } elsif ($line =~ /^\-([\s\S]*)/) {
            $dlines .= ' '.$1;
        } else {
            my $first = 1;
            showdiffs($alines, $dlines);

            ($alines, $dlines) = ('', '');
            col($line, 0);
        }
    }
    showdiffs($alines, $dlines);
}
