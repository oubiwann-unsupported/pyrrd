# CUFlow.pm - A (hopefully) slightly faster implementation of some of the 
# functionality of SubnetIO.pm, in a slightly more configurable fashion
# Owes *VERY* heavily to Dave Plonka's SubnetIO.pm and CampusIO.pm
# Thanks, Dave :) <plonka@doit.wisc.edu>

# To Add:
# ICMP type handling as a Service, ie 6/icmp Echo
# Make Networks record services? How, while still being fast?
# Traffic with the same source and destination port can mess up Services
# Also traffic whose source port is in one service and whose destination is
# 	another. Hmmm...

use strict;

package CUFlow;

require 5;
require Exporter;

@CUFlow::ISA=qw(FlowScan Exporter);

# convert the RCS revision to a reasonable Exporter VERSION:
'$Revision: 1.55 $ ' =~ m/(\d+)\.(\d+)/ && (( $CUFlow::VERSION ) = sprintf("%d.%03d", $1, $2));

=head1 NAME

CUFlow - flowscan module that is a little more configurable than
SubnetIO.pm in return for sacrificing some modularity.

=head1 SYNOPSIS

   $ flowscan CUFlow

or in F<flowscan.cf>:

   ReportClasses CUFlow

=head1 DESCRIPTION

CUFlow.pm creates rrds matching the configuration given in CUFlow.cf. It 
(by default) creates a 'total.rrd' file, representing the total in and 
out-bound traffic it receives. It also creates 2 rrd files for every 
B<Service> directive in CUFlow.cf, service_servicename_src.rrd and 
service_servicename_dst.rrd.

It makes some assumptions about the nature of the flows exported to it:
basically that they are either inbound to your network or outbount from
it. It is designed to be run on a border router, and is not written to
handle traffic exported to it about flows that source and end in your
network, or outside it. It should be used to monitor the traffic being sent
out by networks contained in B<Subnet> statements.

=head1 CONFIGURATION

CUFlow's configuration file is F<CUFlow.cf>. This configuration file is
located in the directory in which the F<flowscan> script resides.

In this file, blank lines, and any data after a pound sign (#) are ignored.
Directives that can be put in this file include:

=over 4

=item B<Router>

By default, CUFlow does not care from which router the flow records it is
processing are from. Unless you specify a Router statement, it just
aggregates all the traffic it gets and produces rrd files based on the
total. But, if you put

	# Separate out traffic from foorouter
	# Router <Ip Address> <optional alias>
	Router 127.0.0.5 foorouter

In addition to generating the totals rrd files it normally does in
OutputDir, it will create a directory whose name is the IP address specified
(or the alias, if one is provided), and create all the same service_*,
protocol_*, and total.rrd files in it, except only for traffic passed from
the router whose address is <Ip Address>.

Note that it does not make any sense to have Router statements in your
config unless you have more than one router feeding flow records to flowscan
(with one router, the results in the per-router directory will be identical
to the total records in OutputDir)

=item B<SampleRate>

If you are using sampled netflow (mandatory on Juniper) the router will 
export only 1/n samples. Specify the sample rate in the 
configfile by using

        # Sample rate pr. exporter in case we're using sampled netflow
        # SampleRate <Ip Address> <rate>
        SampleRate 127.0.0.5 96

This will effectively multiply all data from that router by 96.

=item B<Subnet>

Each B<Subnet> entry in the file is an IP/length pair that represents a local
subnet. E.g.:

	# Subnet for main campus
	Subnet 128.59.0.0/16

Add as many of these as is necessary. CUFlow does not generate additional
reports per subnet, as does CampusIO, it simply treats any packet destined
to an address *not* in any of its Subnet statements as an outbound packet.
The Subnet statements are solely to determine if a given IP address is "in" 
your network or not. For subnet-specific reporting, see the Network item
below.

=item B<Network>

Each B<Network> statement in the cf file is used to generate an rrd file
describing the bytes, packets, and flows in and out of a group of IP 
addresses within your larger Subnet blocks. E.g.:

	# Watson Hall traffic
	Network 128.59.39.0/24,128.59.31.0/24 watson

It consists of a comma separated list of 1 or more CIDR blocks, followed by
a label to apply to traffic into/out of those blocks. It creates rrd files
named 'network_label.rrd'. Note that these are total traffic seen only,
unfortunately, and not per-exporter as Service and Protocol are. Note also
that a Network must be subset of your defined Subnet's.

=item B<Service>

Each B<Service> entry in the file is a port/protocol name that we are
interested in, followed by a label. E.g.:

	# Usenet news
	Service nntp/tcp news

In this case, we are interested in traffic to or from port 119 on TCP, and
wish to refer to such traffic as 'news'. The rrd files that will be created
to track this traffic will be named 'service_news_src.rrd' (tracking traffic
whose source port is 119) and 'service_news_dst.rrd' (for traffic with dst
port 119).  Each B<Service> entry will produce these 2 service files. 

The port and protocol can either be symbolic (nntp, tcp), or absolute
numeric (119, 6). If a name is symbolic, we either getservbyname or
getprotobyname as appropriate.

B<Service> tags may also define a range or group of services that should 
be aggregated together. E.g:

	# RealServer traffic
	Service 7070/tcp,554/tcp,6970-7170/udp realmedia

This means that we will produce a 'service_realmedia_dst.rrd' and 
'service_realmedia_src.rrd' files, which will contain traffic data for
the sum of the port/protocol pairs given above. Do not put spaces in the
comma-separated list.

The label that follows the set of port/protocol pairs must be unique, as it
is used to create the rrd file for the matching data. CUFlow will not start
if there is a duplicate label name.

=item B<ASNumber>

Each B<ASNumber> entry in the configuration file specifies a foreign Autonomous 
System number we are interested in. Specify these in the config file as:

	# Track our traffic to as 23517
	ASNumber 23517 FooNET

where the first argument is the AS number (as reported in the netflow
records), and the second is a label describing that AS. (Do not use spaces
or characters that have meaning to the filesystem/shell in these labels!) An
rrd file is created for every exporting Router (given by a B<Router>
entry). You may specify multiple AS numbers to graph together by providing a
comma-separated list as the first argument, as in the B<Service> tag above.

Also as in B<Service> tags, do not put spaces in the comma-separated list, and 
use unique labels for each ASNumber statement.

=item B<Multicast>

Add B<Multicast> to your CUFlow.cf file to enable our cheap multicast hack.
E.g. :
	# Log multicast traffic
	Multicast

Unfortunately, in cflow records, multicast traffic always has a nexthop
address of 0.0.0.0 and an output interface of 0, meaning by default CUFlow
drops it (but counts for purposes of total.rrd). If you enable this option,
CUFlow will create protocol_multicast.rrd in OutputDir (and
exporter-specific rrd's for any Router statements you have)

=item B<Protocol>

Each B<Protocol> entry means you are interested in gathering summary
statistics for the protocol named in the entry. E.g.:

	# TCP
	Protocol 6 tcp

Each protocol entry creates an rrd file named protocol_<protocol>.rrd in
B<OutputDir> The protocol may be specified either numerically (6), or
symbolically (tcp). It may be followed by an optional alias name. If
symbolic, it will be resolved via getprotobyname. The rrd file will be named
according to the alias, or if one is not present, the name/number supplied.

=item B<TOS>

Each B<TOS> entry means you are interested in gathering summary statistics
for traffic whose TOS flag is contained in the range of the entry. E.g.:

	# Normal
	TOS 0 normal

Each TOS entry creates an rrd file named tos_<tos>.rrd in B<OutputDir>. The
TOS value must be specified numerically. The rrd file will be named
according to the alias.

Similar to Service tags, you may define ranges or groups of TOS values to
record together. E.g.:

	# first 8 values
	TOS 0-7 normal  

This will graph data about all flows with the matching TOS data. TOS values
are between 0 and 255 inclusive.

=item B<OutputDir>

This is the directory where the output rrd files will be written.
E.g.:

	# Output to rrds
	OutputDir rrds

=item B<Scoreboard>

The Scoreboard directive is used to keep a running total of the top
consumers of resources. It produces an html reports showing the top N (where
N is specified in the directive) source addresses that sent the most (bytes,
packets, flows) out, and the top N destination addresses that received the
most (bytes, packets, flows) from the outside. Its syntax is

	# Scoreboard <NumberResults> <RootDir> <CurrentLink>
	Scoreboard 10 /html/reports /html/current.html

The above indicates that each table should show the top 10 of its category,
to keep past reports in the /html/reports directory, and the latest report
should be pointed to by current.html.

Within RootDir, we create a directory per day, and within that, a directory
per hour of the day. In each of these directories, we write the scoreboard
reports. 

Scoreboarding measures all traffic we get flows for, it is unaffected by any
Router statements in your config.

=item B<AggregateScore>

The AggregateScore directive indicates that CUFlow should keep running totals
for the various Scoreboard categories, and generate an overall report based 
on them, updating it every time it creates a new Scoreboard file. E.g.:

	# AggregateScore <NumberToPrint> <Data File> <OutFile>
	AggregateScore 10 /html/reports/totals.dat /html/topten.html

If you configure this option, you must also turn on
Scoreboard. /html/reports/totals.dat is a data file containing an easily
machine-readable form of the last several ScoreBoard reports. It then takes
each entries average values for every time it has appeared in a
ScoreBoard. Then it prints the top NumberToPrint of those. Every 100
samples, it drops all entries that have only appeared once, and divides all
the others by 2 (including the number of times they have appeared). So, if a
given host were always in the regular ScoreBoard, its appearance count
would slowly grow from 50 to 100, then get cut in half, and repeat.

This is usefull for trend analysis, as it enables you to see which hosts are
*always* using bandwidth, as opposed to outliers and occasional users.

AggregateScoreboarding measures all traffic we get flows for, it is
unaffected by any Router statements in your config.

=back

=cut

use Cflow qw(:flowvars 1.015);  # for use in wanted sub
use RRDs;			# To actually produce results
use Socket;			# We need inet_aton
use Net::Patricia;		# Fast IP/mask lookups
use POSIX;			# We need floor()
use FindBin;			# To find our executable

my(%ROUTERS);			# A hash mapping exporter IP's to the name
				# we want them to be called, e.g.
				# $ROUTER{"127.0.0.1"} = 'localhost';
my($SUBNETS);			# A trie of the subnets that are 'inside'
my(%SERVICES);			# A hashtable containing services we are
				# interested in. E.g.:
				# $SERVICES{'www'} = { 80 => { 6 } }
				# means that we are interested in www/tcp
				# and that it has label 'www'
my(%PROTOCOLS);			# A hashtable containing protocols we are
				# interested in. E.g.: 
				# $PROTOCOLS{6} = 'tcp';
				# means we are interested in protocol 6, and
				# wish to call the rrd ourput file tcp.rrd
my($OUTDIR) = '.';		# The directory we will stow rrd files in

my($scorekeep) = 0;	        # The top N addresses to report on. By default
				# don't keep scoreboards.
my($scoredir)  = undef;		# The directory to put the tree of reports in
my($scorepage) = undef;		# The link to the current page

my($aggscorekeep) = 0;		# Do not create an overall rankings file

$CUFlow::NUMKEEP = 50;		# How many aggregates to keep

$CUFlow::multicast = 0;		# Do multicast? Default no.

# Multicast address spec's, taken from CampusIO
$CUFlow::MCAST_NET  = unpack('N', inet_aton('224.0.0.0'));
$CUFlow::MCAST_MASK = unpack('N', inet_aton('240.0.0.0'));

$CUFlow::SUBNETS = new Net::Patricia || die "Could not create a trie ($!)\n";
&parseConfig("${FindBin::Bin}/CUFlow.cf");	# Read our config file

sub parseConfig {
    my $file = shift;
    my($ip,$mask,$srv,$proto,$label,$tmp,$txt);
    my($num,$dir,$current,$start,$end,$hr,$i);

    open(FH,$file) || die "Could not open $file ($!)\n";

    while(<FH>) {
	s/\#.*$//;		# Strip out everything after a #
	next if /^\s*$/;	# Skip blank lines

	if (/^\s*Subnet (\d+\.\d+\.\d+\.\d+\/\d+)\s*$/) {
	    # Stick this entry into our trie
	    $CUFlow::SUBNETS->add_string($1);
	} elsif (/^\s*Router\s+(\d+\.\d+\.\d+\.\d+)\s*(\S+)?\s*$/) {
	    if (defined $2) {
		$CUFlow::ROUTERS{$1} = $2;
	    } else {
		$CUFlow::ROUTERS{$1} = $1;
	    }
	} elsif (/^\s*SampleRate\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s*$/) {
	    $CUFlow::SAMPLERATE{$1} = $2;
	} elsif (/\s*Network\s+(\S+)\s+(\S+)\s*$/) {
	    $ip    = $1;
	    $label = $2;
	    $CUFlow::NETWORKS{$label} = new Net::Patricia ||
		die "Could not create a trie ($!)\n";

	    foreach $current (split(/,/,$ip)) {
		# Parse each item
		$CUFlow::NETWORKS{$label}->add_string($current);
	    }
	} elsif (/^\s*Multicast\s*$/) {
	    $CUFlow::multicast = 1;
	} elsif (/^\s*Service\s+(\S+)\s+(\S+)\s*$/) {
	    $txt   = $1;
	    $label = $2;

	    die "Service $label redefined at $.\n" 
		if (defined $CUFlow::SERVICES{$label});

	    $hr = { };		# New hashref

	    # A Service is one or more port/proto ranges, separated by ,'s
	    foreach $current (split(/,/,$txt)) {
		# Parse each item
		if ($current =~ /(\S+)\s*\/\s*(\S+)/) {
		    $srv   = $1;
		    $proto = $2;

		    if ($proto !~ /^\d+$/) { # Not an integer! Try getprotobyname
			$tmp = getprotobyname($proto) || 
			    die "Unknown protocol $proto on line $.\n";
			$proto = $tmp;
		    }

		    if ($srv =~ /(\d+)-?(\d+)?/) { # Numeric or range
			$start = $1;
			$end = (defined($2)) ? $2 :$start;

			die "Bad range $start - $end on line $.\n" if
			    ($end < $start);

			for($i=$start;$i<=$end;$i++) {
			    $hr->{$proto}{$i} = 1; # Save all these ports
			}
		    } else {	# Symbolic or bad?
			if ($srv !~ /^\d+$/) { # Not an integer? 
			    # Try getservbyname
			    $tmp = getservbyname($srv,
						 getprotobynumber($proto)) ||
			     die "Unknown service $srv on line $.\n";

			    $srv = $tmp;
			}
			$hr->{$proto}{$srv} = 1;
		    }
		} else {
		    die "Bad Service item $current on line $.\n";
		}
	    }
	    $CUFlow::SERVICES{$label} = $hr;
	} elsif (/^\s*ASNumber\s+(\S+)\s+(\S+)\s*$/) {
	    $txt   = $1;
	    $label = $2;

	    die "ASNumber $label redefined at $." 
		if (defined $CUFlow::ASNUMBERS{$label});

	    $hr = { };

	    # An ASNumber statement is 1 or more AS numbers, separated by ,'s
	    foreach $current (split(/,/,$txt)) {

		die "Bad AS number $current on line $.\n" 
		    if ($current !~ /^\d+$/);

		$hr->{$current} = 1;
	    }
	    $CUFlow::ASNUMBERS{$label} = $hr;

	} elsif (/^\s*TOS\s+(\S+)\s+(\S+)\s*$/) {
	    $txt   = $1;
	    $label = $2;

	    $hr = { };		# New hashref
	    
	    # a TOS value can be one or more ranges of ints, separated by ,'s
	    foreach $current (split(/,/,$txt)) {
		# parse each item
		if ($current =~ /(\d+)-?(\d+)?/) {	# A range
		    $start = $1;
		    $end = (defined($2)) ? $2 :$start;

		    die "Bad range $start - $end on line $.\n" if
			($end < $start);

		    die "Bad TOS value $start on line $.\n" if
			(($start < 0) || ($start > 255));

		    die "Bad TOS value $end on line $.\n" if
			(($end < 0) || ($end > 255));

		    for($i=$start;$i<=$end;$i++) {
			$hr->{$i} = 1; # Save all these ports
		    }		    
		} else {
		    die  "Bad TOS item $current on line $.\n";
		}
	    }
	    $CUFlow::TOS{$label} = $hr;
	} elsif (/^\s*Scoreboard\s+(\d+)\s+(\S+)\s+(\S+)\s*$/) {
	    $num = $1;
	    $dir = $2;
	    $current = $3;
	    
	    eval "use HTML::Table";
	    die "$@" if $@;

	    $CUFlow::scorekeep = $num;
	    $CUFlow::scoredir  = $dir;
	    $CUFlow::scorepage = $current;
	} elsif (/^\s*AggregateScore\s+(\d+)\s+(\S+)\s+(\S+)\s*$/) {
	    $num = $1;
	    $dir = $2;
	    $current = $3;
	    
	    $CUFlow::aggscorekeep = $num;
	    $CUFlow::aggscorefile  = $dir;
	    $CUFlow::aggscoreout = $current;
	} elsif (/^\s*Protocol\s+(\S+)\s*(\S+)?\s*$/) {
	    $proto = $1;
	    $label = $2;

	    if ($proto !~ /\d+/) { # non-numeric protocol name
		# Try resolving
		$tmp = getprotobyname($proto) || 
		    die "Unknown protocol $proto on line $.\n";
		if (defined($label)) {
		    $CUFlow::PROTOCOLS{$tmp} = $label;
		} else {
		    $CUFlow::PROTOCOLS{$tmp} = $proto;
		}
	    } else {
		if (defined($label)) {
		    $CUFlow::PROTOCOLS{$proto} = $label;
		} else {
		    $CUFlow::PROTOCOLS{$proto} = $proto;
		}
	    }

	} elsif (/^\s*OutputDir\s+(\S+)\s*$/) {
	    $CUFlow::OUTDIR = $1;
	} else {
	    die "Invalid line $. in $file\n\t$_\n";
	}
    }

    close(FH);
}

sub new {
   my $self = {};
   my $class = shift;

   return bless _init($self), $class
}

sub _init {
   my $self = shift;
   
   $self->{iniplog} = new Net::Patricia || 
       die "Could not create a trie ($!)\n";
   $self->{outiplog} = new Net::Patricia || 
       die "Could not create a trie ($!)\n";

   return $self
}

# This is called once per flow record, more than 800k times per file. It
# needs to be as fast and as short as possible.
sub wanted {
    my $self = shift;
    my $which = '';
    my $hr;
    my $samplerate = 1;
    my $asn;

    # If this router is set up as a sampled source, normalize its data
    if (defined($CUFlow::SAMPLERATE{$exporterip})) {
	$samplerate = $CUFlow::SAMPLERATE{$exporterip};
	$bytes *= $samplerate;
	$pkts  *= $samplerate;
    }

    # Multicast handling here, it seems to have nexthop and
    # outputIf of zero
    if (($dstaddr & $CUFlow::MCAST_MASK) == $CUFlow::MCAST_NET) {
	# it is a multicast packet!
	
	# First, are we inbound or outbound?
	if ($CUFlow::SUBNETS->match_integer($srcaddr)) {
	    $which = 'out';
	    $asn = $dst_as
	} else {
	    $which = 'in';
	    $asn = $src_as
	}

	$hr = $self->{exporters}{$exporterip};
	
	# Save stats for every protocol, sort out which to log in sub report()
	$hr->{'multicast'}{$which}{'flows'} += $samplerate;
	$hr->{'multicast'}{$which}{'bytes'} += $bytes;
	$hr->{'multicast'}{$which}{'pkts'}  += $pkts;

	# Also update the totals...
	$hr->{'total'}{$which}{'flows'} += $samplerate;
	$hr->{'total'}{$which}{'bytes'} += $bytes;
	$hr->{'total'}{$which}{'pkts'}  += $pkts;

	# Now update TOS counters
	$hr->{'tos'}{$which}{$tos}{'flows'} += $samplerate;
	$hr->{'tos'}{$which}{$tos}{'bytes'} += $bytes;
	$hr->{'tos'}{$which}{$tos}{'pkts'}  += $pkts;

	# AS statistics
	$hr->{'as'}{$which}{$asn}{'flows'} += $samplerate;
	$hr->{'as'}{$which}{$asn}{'bytes'} += $bytes;
	$hr->{'as'}{$which}{$asn}{'pkts'}  += $pkts;

	$self->{exporters}{$exporterip} = $hr;
	return 1;	
    } 

    # Had to rmeove this because too many cisco's don't fill out these
    # fields
    #return 0 if ($nexthop == 0);   # Non-routable traffic is dumped.
    #return 0 if ($output_if == 0); # Dump traffic routed to nowhere

    # First, are we inbound or outbound?
    if ($CUFlow::SUBNETS->match_integer($dstaddr)) {
	# If the destination is in inside, this is an inbound flow
	# unless the source is also inside, in which case, return silently
	return 0 if ($CUFlow::SUBNETS->match_integer($srcaddr));
	
	$which = 'in';
	$asn = $src_as;			# Inbound, which AS is it coming from?

	# Save stats for scoreboarding
	if (!($hr = $self->{iniplog}->match_integer($dstaddr))) {
	    $hr = $self->{iniplog}->add_string($dstip, { addr => $dstip,
							 bytes => 0,
							 pkts => 0,
							 flows => 0});
	}
    } elsif ($CUFlow::SUBNETS->match_integer($srcaddr)) {
	# The source for this flow is in SUBNETS; it is outbound
	# unless the destination is also inside, in which case, return silently
	return 0 if ($CUFlow::SUBNETS->match_integer($dstaddr));

	$which = 'out';
	$asn = $dst_as;			# outbound, which AS is it going to?

	# Save stats for scoreboarding
	if (!($hr = $self->{outiplog}->match_integer($srcaddr))) {
	    $hr = $self->{outiplog}->add_string($srcip, { addr => $srcip,
							  bytes => 0,
							  pkts => 0,
							  flows => 0});
	}
    } else {
	# Neither source nor destination is inside, return silently
	return 0;
    }

    $hr->{bytes} += $bytes;
    $hr->{pkts}  += $pkts;
    $hr->{flows} += $samplerate;

    $hr = $self->{exporters}{$exporterip};

    # First update the total counters
    $hr->{'total'}{$which}{'flows'} += $samplerate;
    $hr->{'total'}{$which}{'bytes'} += $bytes;
    $hr->{'total'}{$which}{'pkts'}  += $pkts;

    # Now update TOS counters
    $hr->{'tos'}{$which}{$tos}{'flows'} += $samplerate;
    $hr->{'tos'}{$which}{$tos}{'bytes'} += $bytes;
    $hr->{'tos'}{$which}{$tos}{'pkts'}  += $pkts;

    # Save stats for every protocol, sort out which to log in sub report()
    $hr->{$protocol}{'total'}{$which}{'flows'} += $samplerate;
    $hr->{$protocol}{'total'}{$which}{'bytes'} += $bytes;
    $hr->{$protocol}{'total'}{$which}{'pkts'}  += $pkts;

    # Next update service counters in the same fashion
    $hr->{$protocol}{'src'}{$srcport}{$which}{'flows'} += $samplerate;
    $hr->{$protocol}{'src'}{$srcport}{$which}{'bytes'} += $bytes;
    $hr->{$protocol}{'src'}{$srcport}{$which}{'pkts'}  += $pkts;

    $hr->{$protocol}{'dst'}{$dstport}{$which}{'flows'} += $samplerate;
    $hr->{$protocol}{'dst'}{$dstport}{$which}{'bytes'} += $bytes;
    $hr->{$protocol}{'dst'}{$dstport}{$which}{'pkts'}  += $pkts;

    # Save Data on a per-AS basis
    $hr->{'as'}{$which}{$asn}{'flows'} += $samplerate;
    $hr->{'as'}{$which}{$asn}{'bytes'} += $bytes;
    $hr->{'as'}{$which}{$asn}{'pkts'}  += $pkts;
    
    $self->{exporters}{$exporterip} = $hr;
    return 1;
}

sub perfile {
    # Only do this, so we get the filetime from our super-class
    my $self = shift;

    $CUFlow::totals = ();	# Clear this out

    $self->SUPER::perfile(@_);
}

sub report {
    my $self = shift;
    my($file) = $CUFlow::OUTDIR . "/total.rrd";
    my($routerfile);
    my(@values) = ();
    my(@array);
    my($hr,$count, $i, $tmp);

    # Zeroth, this takes a lot of time. So let's fork and return
    if (fork()) {		# We are the parent, wait
	wait;			# This wait will finish quit, as our immediate
				# child just forks and dies. It's kid does the
				# work. Saves us fiddling with signals.
	return;			# Then go back!!!
    } else {			# We are the child, fork again
	exit if (fork());
    }

    # Make sure directories exist
    foreach my $k (keys %CUFlow::ROUTERS) {
	
	if (! -d "$CUFlow::OUTDIR/" . $CUFlow::ROUTERS{$k} ) {
	    mkdir("$CUFlow::OUTDIR/" . $CUFlow::ROUTERS{$k},0755);
	}
    }

    # Compute total values
    for my $dir ('in','out') {
	for my $type ('pkts','bytes','flows') {
	    $i = 0;
	    for my $exporter (keys %{$self->{exporters}}) {
		$i += $self->{exporters}{$exporter}{'total'}{$dir}{$type};
	    }
	    $CUFlow::totals{$dir}{$type} = $i;
	}
    }
    
    # First, always generate a totals report
    # createGeneralRRD we get from our parent, FlowScan
    # Create a new rrd if one doesn't exist
    $self->createGeneralRRD($file,
			    qw(
			       ABSOLUTE in_bytes
			       ABSOLUTE out_bytes
			       ABSOLUTE in_pkts
			       ABSOLUTE out_pkts
			       ABSOLUTE in_flows
			       ABSOLUTE out_flows
			       )
			    ) unless -f $file; 

    foreach my $i ('bytes','pkts','flows') {
	foreach my $j ('in','out') {
	    push(@values, $CUFlow::totals{$j}{$i});
	}
    }
    $self->updateRRD($file, @values);

    # Now do totals per-exporter
    foreach my $exporter (keys %CUFlow::ROUTERS) {
	@values = ();
	$routerfile = $CUFlow::OUTDIR . "/" . 
	    $CUFlow::ROUTERS{$exporter} . "/total.rrd";
	$self->createGeneralRRD($routerfile,
				qw(
				   ABSOLUTE in_bytes
				   ABSOLUTE out_bytes
				   ABSOLUTE in_pkts
				   ABSOLUTE out_pkts
				   ABSOLUTE in_flows
				   ABSOLUTE out_flows
				   )
				) unless -f $routerfile; 
	
	foreach my $i ('bytes','pkts','flows') {
	    foreach my $j ('in','out') {
		$hr = $self->{exporters}{$exporter};
		push(@values, 0 + $hr->{'total'}{$j}{$i});
	    }
	}
	$self->updateRRD($routerfile, @values);
    }

    # Second, Multicast?
    # createGeneralRRD we get from our parent, FlowScan
    # Create a new rrd if one doesn't exist
    if ($CUFlow::multicast == 1) {
	$file = $CUFlow::OUTDIR . "/protocol_multicast.rrd";
	$self->createGeneralRRD($file,
				qw(
				   ABSOLUTE in_bytes
				   ABSOLUTE out_bytes
				   ABSOLUTE in_pkts
				   ABSOLUTE out_pkts
				   ABSOLUTE in_flows
				   ABSOLUTE out_flows
				   )
				) unless -f $file; 
	
	@values = ();
	foreach my $i ('bytes','pkts','flows') {
	    foreach my $j ('in','out') {
		$count = 0;
		foreach my $k (keys %{$self->{exporters}}) {
		    $count += $self->{exporters}{$k}{'multicast'}{$j}{$i};
		}
		push(@values,$count);
	    }
	}
	$self->updateRRD($file, @values);

	# Now do totals per-exporter
	foreach my $exporter (keys %CUFlow::ROUTERS) {
	    @values = ();
	    $routerfile = $CUFlow::OUTDIR . "/" . 
		$CUFlow::ROUTERS{$exporter} . "/protocol_multicast.rrd";
	    $self->createGeneralRRD($routerfile,
				    qw(
				       ABSOLUTE in_bytes
				       ABSOLUTE out_bytes
				       ABSOLUTE in_pkts
				       ABSOLUTE out_pkts
				       ABSOLUTE in_flows
				       ABSOLUTE out_flows
				       )
				    ) unless -f $routerfile; 
	    
	    foreach my $i ('bytes','pkts','flows') {
		foreach my $j ('in','out') {
		    $hr = $self->{exporters}{$exporter};
		    push(@values, 0 + $hr->{'multicast'}{$j}{$i});
		}
	    }
	    $self->updateRRD($routerfile, @values);
	}
    }

    # Now do an AS report for each AS we are interested in for each exporter
    foreach my $label (keys %CUFlow::ASNUMBERS) {
	@values = ();			# Initialize values to insert
	$hr = $CUFlow::ASNUMBERS{$label};
	
	# First, total values
	$file = $CUFlow::OUTDIR . "/as_" . $label . ".rrd";

	$self->createGeneralRRD($file,
				qw(
				   ABSOLUTE in_bytes
				   ABSOLUTE out_bytes
				   ABSOLUTE in_pkts
				   ABSOLUTE out_pkts
				   ABSOLUTE in_flows
				   ABSOLUTE out_flows
				   )
				) unless -f $file; 

	foreach my $type ('bytes','pkts','flows') {
	    foreach my $dir ('in','out') {
		# Sum all the AS values here
		$tmp = 0;
		foreach my $exporter (keys %{$self->{exporters}}) {
		    foreach my $current (keys %$hr) {
			$tmp +=
		    $self->{exporters}{$exporter}{as}{$dir}{$current}{$type};
			
		    }
		}		
		push(@values,$tmp);
	    }
	}
        $self->updateRRD($file, @values);

	# Next, per-exporter totals
	foreach my $exporter (keys %CUFlow::ROUTERS) {
	    @values = ();
	    $routerfile = $CUFlow::OUTDIR . "/" . 
		$CUFlow::ROUTERS{$exporter} . 
		"/as_" . $label . ".rrd";

	    $self->createGeneralRRD($routerfile,
				    qw(
				       ABSOLUTE in_bytes
				       ABSOLUTE out_bytes
				       ABSOLUTE in_pkts
				       ABSOLUTE out_pkts
				       ABSOLUTE in_flows
				       ABSOLUTE out_flows
				       )
				    ) unless -f $routerfile; 
	    
	    foreach my $type ('bytes','pkts','flows') {
		foreach my $dir ('in','out') {
		    # Sum counter for all AS'es in this label
		    $tmp = 0;

		    foreach my $current (keys %$hr) {
			$tmp += 
	    $self->{exporters}{$exporter}{as}{$dir}{$current}{$type};
		    }
		    push(@values,$tmp);
		}
	    }
	    $self->updateRRD($routerfile, @values);
	}	
    }

    # Next, generate TOS reports. Each label gets one rrd.
    foreach my $tos (keys %CUFlow::TOS) {
	@values = ();
	$file = $CUFlow::OUTDIR . "/tos_" . $tos . ".rrd";

	$hr = $CUFlow::TOS{$tos};

	$self->createGeneralRRD($file,
				qw(
				   ABSOLUTE in_bytes
				   ABSOLUTE out_bytes
				   ABSOLUTE in_pkts
				   ABSOLUTE out_pkts
				   ABSOLUTE in_flows
				   ABSOLUTE out_flows
				   )
				) unless -f $file; 

	foreach my $type ('bytes','pkts','flows') {
	    foreach my $dir ('in','out') {
		    
		# Sum counter for all TOS values in this label
		$tmp = 0;
		foreach my $exporter (keys %{$self->{exporters}}) {
		    foreach my $current (keys %$hr) {

			$tmp +=
		    $self->{exporters}{$exporter}{tos}{$dir}{$current}{$type};
			
		    }
		}		
		push(@values,$tmp);
	    }
	}
        $self->updateRRD($file, @values);
    
	# Now do the same thing for each exporter.
	foreach my $exporter (keys %CUFlow::ROUTERS) {
	    @values = ();
	    $routerfile = $CUFlow::OUTDIR . "/" . 
		$CUFlow::ROUTERS{$exporter} . 
		    "/tos_" . $tos . ".rrd";

	    $self->createGeneralRRD($routerfile,
				    qw(
				       ABSOLUTE in_bytes
				       ABSOLUTE out_bytes
				       ABSOLUTE in_pkts
				       ABSOLUTE out_pkts
				       ABSOLUTE in_flows
				       ABSOLUTE out_flows
				       )
				    ) unless -f $routerfile; 

	    foreach my $type ('bytes','pkts','flows') {
		foreach my $dir ('in','out') {
		    # Sum counter for all services in this label
		    $tmp = 0;

		    foreach my $current (keys %$hr) {
			$tmp += 
	    $self->{exporters}{$exporter}{tos}{$dir}{$current}{$type};
		    }
		    push(@values,$tmp);
		}
	    }
	    $self->updateRRD($routerfile, @values);
	}	
    }

    # Next, see if we need to generate any per-protocol reports
    # Each protocol gets one rrd.
    foreach my $proto (keys %CUFlow::PROTOCOLS) {	
	@values = ();
	$file = $CUFlow::OUTDIR . "/protocol_" . 
	    $CUFlow::PROTOCOLS{$proto} . ".rrd";

	$self->createGeneralRRD($file,
				qw(
				   ABSOLUTE in_bytes
				   ABSOLUTE out_bytes
				   ABSOLUTE in_pkts
				   ABSOLUTE out_pkts
				   ABSOLUTE in_flows
				   ABSOLUTE out_flows
				   )
				) unless -f $file; 
	
	foreach my $i ('bytes','pkts','flows') {
	    foreach my $j ('in','out') {
		$count = 0;
		foreach my $k (keys %{$self->{exporters}}) {
		    $hr = $self->{exporters}{$k};
		    $count += $hr->{$proto}{'total'}{$j}{$i};
		}
		push(@values, $count);
	    }
	}
	$self->updateRRD($file, @values);

	# Now do totals per-exporter
	foreach my $exporter (keys %CUFlow::ROUTERS) {
	    @values = ();
	    $routerfile = $CUFlow::OUTDIR . "/" . 
		$CUFlow::ROUTERS{$exporter} . "/protocol_" . 
		    $CUFlow::PROTOCOLS{$proto} . ".rrd";
	    $self->createGeneralRRD($routerfile,
				    qw(
				       ABSOLUTE in_bytes
				       ABSOLUTE out_bytes
				       ABSOLUTE in_pkts
				       ABSOLUTE out_pkts
				       ABSOLUTE in_flows
				       ABSOLUTE out_flows
				       )
				    ) unless -f $routerfile; 
	    
	    foreach my $i ('bytes','pkts','flows') {
		foreach my $j ('in','out') {
		    $hr = $self->{exporters}{$exporter};
		    push(@values, 0 + $hr->{$proto}{'total'}{$j}{$i});
		}
	    }
	    $self->updateRRD($routerfile, @values);
	}
    }

    # Next, see which services require rrd files. Each one gets 2 files,
    # one for src port traffic, one for dst port traffic
    foreach my $label (keys %CUFlow::SERVICES) {
	$hr = $CUFlow::SERVICES{$label};
	foreach my $direction ('src','dst') {
	    @values = ();

	    $file = $CUFlow::OUTDIR . "/service_$label" .  "_$direction.rrd";

	    # createGeneralRRD we get from our parent, FlowScan
	    # Create a new rrd if one doesn't exist
	    $self->createGeneralRRD($file,
				    qw(
				       ABSOLUTE in_bytes
				       ABSOLUTE out_bytes
				       ABSOLUTE in_pkts
				       ABSOLUTE out_pkts
				       ABSOLUTE in_flows
				       ABSOLUTE out_flows
				       )
				    ) unless -f $file; 
	    foreach my $type ('bytes','pkts','flows') {
		foreach my $dir ('in','out') {
		    
		    # Sum counter for all services in this label
		    $tmp = 0;
		    foreach my $exporter (keys %{$self->{exporters}}) {
			
			foreach my $proto (keys %$hr) {
			    foreach my $service (keys %{ $hr->{$proto} }) {
				
				# This is the worst thing ever.
				$tmp += 
    $self->{exporters}{$exporter}{$proto}{$direction}{$service}{$dir}{$type};
			    }
			}
		    }
		    push(@values,$tmp);
		}
	    }

	    $self->updateRRD($file, @values);

	    # Now do the same thing for each exporter.
	    foreach my $exporter (keys %CUFlow::ROUTERS) {
		@values = ();
		$routerfile = $CUFlow::OUTDIR . "/" . 
		    $CUFlow::ROUTERS{$exporter} . 
			"/service_$label" .
			    "_$direction.rrd";
		$self->createGeneralRRD($routerfile,
					qw(
					   ABSOLUTE in_bytes
					   ABSOLUTE out_bytes
					   ABSOLUTE in_pkts
					   ABSOLUTE out_pkts
					   ABSOLUTE in_flows
					   ABSOLUTE out_flows
					   )
					) unless -f $routerfile; 
		foreach my $type ('bytes','pkts','flows') {
		    foreach my $dir ('in','out') {
			# Sum counter for all services in this label
			$tmp = 0;
			foreach my $proto (keys %$hr) {
			    foreach my $service (keys %{ $hr->{$proto} }) {
				
				# This is the worst thing ever also.
				$tmp += 
   $self->{exporters}{$exporter}{$proto}{$direction}{$service}{$dir}{$type};
			    }
			}
			push(@values,$tmp);
		    }
		}
		$self->updateRRD($routerfile, @values);
	    }
	}
    }
	
    # Should we do scoreboarding?
    if ($CUFlow::scorekeep > 0) {
	# Yes.
	$self->scoreboard();
    }

    # Per-network reporting?
    #
    # You need to iterate over all the IP's for each Network group because
    # You may have some IP's that match more than 1 network statement
    foreach my $label (keys %CUFlow::NETWORKS) {
	@values = ();
	$tmp = $CUFlow::NETWORKS{$label};
	$file = $CUFlow::OUTDIR . "/network_" . "$label.rrd";

	$self->createGeneralRRD($file,
				qw(
				   ABSOLUTE in_bytes
				   ABSOLUTE in_pkts
				   ABSOLUTE in_flows
				   ABSOLUTE out_bytes
				   ABSOLUTE out_pkts
				   ABSOLUTE out_flows
				   )
				) unless -f $file; 
	
	foreach my $dir ('in','out') {
	    @array = ();
	    $self->{$dir . "iplog"}->climb(sub {push(@array, $_[0]) if
						    $tmp->match_string(
							       $_[0]->{addr}) 
						    } );
	    foreach my $type ('bytes','pkts','flows') {
		$i = 0;
		foreach my $ip (@array) {
		    $i += $ip->{$type};
		}
		push(@values,$i);
	    }
	}
	
	$self->updateRRD($file, @values);	
    }

    exit 0;			# We forked, no returning.
}

# Lifted totally and shamelessly from CampusIO.pm
# I think perhaps this goes into FlowScan.pm, but...
sub updateRRD {
   my $self = shift;
   my $file = shift;
   my @values = @_;

   RRDs::update($file, $self->{filetime} . ':' . join(':', @values));
   my $err=RRDs::error;
   warn "ERROR updating $file: $err\n" if ($err);
}

# Function to read in the current aggregate data
# Returns a hash of ip to (count of times in top ten, ttl bytes in, 
#			   ttl pkts in, ttl flows in, ttl bytes out, 
#			   ttl pkts out, ttl flows out
sub readAggFile 
{
    my($ip,$cnt,$bin,$pin,$fin,$bout,$pout,$fout);
    my(%ret) = ();

    if (-f $CUFlow::aggscorefile) {	# Exists, try reading it in
	open(AGG,$CUFlow::aggscorefile) ||
	    die "Cannot open $CUFlow::aggscorefile ($!)\n";
	$ret{'numresults'} = <AGG>;
	chomp($ret{'numresults'});
	while(<AGG>) {
	    if (
		($ip,$cnt,$bin,$pin,$fin,$bout,$pout,$fout) =
	(/(\d+\.\d+\.\d+\.\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)/))
	    {
		# Skip any data that has rolled over
		if (($cnt < 0) || ($bin < 0) || ($bout < 0) ||
		    ($pin < 0) || ($pout < 0) || ($fin < 0) ||
		    ($fout < 0)) {
		    print STDERR "Rollover for $ip\n";
		    next;	# Skip it
		}
			 
		$ret{$ip} = { 'count'    => $cnt, 
			      'bytesin'  => $bin, 
			      'bytesout' => $bout,
			      'pktsin'   => $pin, 
			      'pktsout'  => $pout,
			      'flowsin'  => $fin, 
			      'flowsout' => $fout };
	    }
	}
	close AGG;
    }
    return %ret;
}

# Function to write the aggregate data out to a file
sub writeAggFile (\%)
{
    my %data = %{(shift)};
    
    open(OUT,">$CUFlow::aggscorefile") ||
	die "Cannot open $CUFlow::aggscorefile for write ($!)\n";

    print OUT $data{'numresults'} . "\n";
    foreach my $ip (keys %data) {
	next if ($ip =~ /numresults/);
	printf OUT "%s %d %d %d %d %d %d %d\n",
			$ip,
			$data{$ip}->{'count'},
			$data{$ip}->{'bytesin'},
			$data{$ip}->{'pktsin'},
			$data{$ip}->{'flowsin'},
			$data{$ip}->{'bytesout'},
			$data{$ip}->{'pktsout'},
			$data{$ip}->{'flowsout'};   
    }

    close OUT;
}

# Function to print the pretty table of over-all winners
sub writeAggScoreboard (\%)
{
    my %data = %{(shift)};
    my($dir,$key, $i);
    my(@sorted);
    my(%dnscache);
    my($tmp) = $data{'numresults'};

    delete $data{'numresults'};

    open(OUT,">$CUFlow::aggscoreout") ||
	die "Cannot open $CUFlow::aggscoreout for write ($!)\n";

    print OUT "<html>\n<body bgcolor=\"\#ffffff\">\n\n<center>\n";
    print OUT "<h3> Average rankings for the last $tmp topN reports\n<hr>\n";
    print OUT "</center>\n";

    # Now, print out our 6 topN tables
    my %columns = ('bytes' => 3, 'pkts' => 5, 'flows' => 7);

    foreach my $dir ('in','out') {
	foreach my $key ('bytes','pkts','flows') {
	    @sorted = sort { ($data{$b}->{"$key$dir"} / 
			      $data{$b}->{'count'}) 
				 <=> 
			     ($data{$a}->{"$key$dir"} / 
			      $data{$a}->{'count'}) }
	    	(keys %data);

	    my $table = new 'HTML::Table';
	    die unless ref($table);    

	    $table->setBorder(1);
	    $table->setCellSpacing(0);
	    $table->setCellPadding(3);

	    $table->setCaption("Top $CUFlow::aggscorekeep by " .
			       "<b>$key $dir</b><br>\n" .
			       "built on aggregated topN " .
			       "5 minute average samples to date",
			       'TOP');

	    my $row = 1;
	    $table->addRow('<b>rank</b>',
			   "<b>$dir Address</b>",
			   '<b>bits/sec in</b>',
			   '<b>bits/sec out</b>',
			   '<b>pkts/sec in</b>',
			   '<b>pkts/sec out</b>',
			   '<b>flows/sec in</b>',
			   '<b>flows/sec out</b>');
	    $table->setRowBGColor($row, '#FFFFCC'); # pale yellow

	    # Highlight the current column (out is 1 off from in)
	    $table->setCellBGColor($row, $columns{$key} + ('out' eq $dir),
				   '#90ee90'); # light green
	    $row++;	    
	    for($i=0;$i < @sorted; $i++) {
		last unless $i < $CUFlow::aggscorekeep;
		my $ip = $sorted[$i];

		if (!(defined($dnscache{$ip}))) { # No name here?
		    if ($dnscache{$ip} = gethostbyaddr(pack("C4", 
							split(/\./, $ip)),
						       AF_INET)) {
			$dnscache{$ip} .= "<br>$ip (" . 
			    $data{$ip}->{'count'} . " samples)";
		    } else {
			$dnscache{$ip} = $ip . " (" .
			    $data{$ip}->{'count'} . " samples)";
		    }
		}		

		my $div = 300 * $data{$ip}->{'count'};
		$table->addRow( sprintf("#%d",$i+1),
				$dnscache{$ip},      # IP Name/Address
				
				# Bits/sec in
				scale("%.1f", ($data{$ip}->{'bytesin'}*8) /
				                $div),
				
				# Bits/sec out
				scale("%.1f", ($data{$ip}->{'bytesout'}*8) /
				                $div),

				# Pkts/sec in
				scale("%.1f", ($data{$ip}->{'pktsin'}/$div)),
				
				# Pkts/sec out
				scale("%.1f", ($data{$ip}->{'pktsout'}/$div)),
				
				# Flows/sec in
				scale("%.1f", ($data{$ip}->{'flowsin'}/$div)),
				
				# Flows/sec out
				scale("%.1f", 
				      ($data{$ip}->{'flowsout'}/$div)));

		
		$table->setRowAlign($row, 'RIGHT');
		$table->setCellBGColor($row,
				       $columns{$key} + ('out' eq $dir),
				       '#add8e6'); # light blue
		$row++;
	    }
	    print OUT "<p>\n$table</p>\n\n";	    
	}
    }
    
    close OUT;
    $data{'numresults'} = $tmp;
}

# Handle writing our HTML scoreboard reports
sub scoreboard {    
    my $self = shift;
    my($i,$file,$ip,$hr);
    my (@values, @sorted);
    my(%dnscache) = ();
    my(%aggdata, %newaggdata);

    # First, should we read in the aggregate data?
    if ($CUFlow::aggscorekeep > 0) {
	%aggdata = &readAggFile();
    }

    # Next, open the file, making any necessary directories
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
	localtime($self->{filetime});  

    $mon++; $year += 1900;

    $file=sprintf("%s/%4.4d-%2.2d-%2.2d",$CUFlow::scoredir,$year,$mon,$mday);

    if (! -d $file) {
	mkdir($file,0755) || die "Cannot mkdir $file ($!)\n";
    }

    $file = sprintf("%s/%2.2d",$file,$hour);
    if (! -d $file) {
	mkdir($file,0755) || die "Cannot mkdir $file ($!)\n";
    }
    
    $file = sprintf("%s/%2.2d:%2.2d:%2.2d.html",$file,$hour,$min,$sec);
    open(HTML,">$file") || die "Could not write to $file ($!)\n";

    # Now, print out our header stuff into the file
    print HTML "<html>\n<body bgcolor=\"\#ffffff\">\n<center>\n\n";

    # Now, print out our 6 topN tables
    my %columns = ('bytes' => 3, 'pkts' => 5, 'flows' => 7);

    foreach my $dir ('in','out') {
	@values = ();
    
	# fill values with hashrefs
	$self->{$dir . "iplog"}->climb(sub {push(@values, $_[0]) });

	foreach my $key ('bytes','pkts','flows') {
	    @sorted = sort { $b->{$key} <=> $a->{$key} } @values;

	    # This part lifted totally from CampusIO.pm. Thanks, dave!

	    my $table = new 'HTML::Table';
	    die unless ref($table);
	    $table->setBorder(1);
	    $table->setCellSpacing(0);
	    $table->setCellPadding(3);

	    $table->setCaption("Top $CUFlow::scorekeep by " .
			       "<b>$key $dir</b><br>\n" .
			       "for five minute flow sample ending " .
			       scalar(localtime($self->{filetime})),
			       'TOP');

	    my $row = 1;
	    $table->addRow('<b>rank</b>',
			   "<b>$dir Address</b>",
			   '<b>bits/sec in</b>',
			   '<b>bits/sec out</b>',
			   '<b>pkts/sec in</b>',
			   '<b>pkts/sec out</b>',
			   '<b>flows/sec in</b>',
			   '<b>flows/sec out</b>');
	    $table->setRowBGColor($row, '#FFFFCC'); # pale yellow

	    # Highlight the current column (out is 1 off from in)
	    $table->setCellBGColor($row, $columns{$key} + ('out' eq $dir),
				   '#90ee90'); # light green
	    $row++;	    

	    # Get the in and out hr's for ease of use
	    my ($in, $out);

	    for($i=0;$i < @sorted; $i++) {
		last unless $i < $CUFlow::scorekeep;
		$ip = $sorted[$i]->{addr};

		$in  = $self->{"iniplog"}->match_string($ip);
		$out = $self->{"outiplog"}->match_string($ip);

		if (!(defined($newaggdata{$ip}))) { # Add this to aggdata 1x
		    $newaggdata{$ip} = { 'bytesin'  => $in->{bytes},
					 'bytesout' => $out->{bytes},
					 'pktsin'   => $in->{pkts},
					 'pktsout'  => $out->{pkts},
					 'flowsin'  => $in->{flows},
					 'flowsout' => $out->{flows} };
		}
		
		if (!(defined($dnscache{$ip}))) { # No name here?
		    if ($dnscache{$ip} = gethostbyaddr(pack("C4", 
							split(/\./, $ip)),
						       AF_INET)) {
			$dnscache{$ip} .= "<br>$ip";
		    } else {
			$dnscache{$ip} = $ip;
		    }
		}
		
		$table->addRow( sprintf("#%d",$i+1),
				$dnscache{$ip},      # IP Name/Address
				
				# Bits/sec in
				scale("%.1f", ($in->{bytes}*8)/300) .
				    sprintf(" (%.1f%%)",
                                            percent($in->{bytes}, 
                                                 $CUFlow::totals{in}{bytes})),

				# Bits/sec out
				scale("%.1f", ($out->{bytes}*8)/300) .
				    sprintf(" (%.1f%%)",
					    percent($out->{bytes}, 
                                                $CUFlow::totals{out}{bytes})),
				
				# Pkts/sec in
				scale("%.1f", ($in->{pkts}/300)) .
				    sprintf(" (%.1f%%)",
                                            percent($in->{pkts}, 
                                                 $CUFlow::totals{in}{pkts})),
				
				# Pkts/sec out
				scale("%.1f", ($out->{pkts}/300)) .
				    sprintf(" (%.1f%%)",
                                            percent($out->{pkts}, 
                                                 $CUFlow::totals{out}{pkts})),
				
				# Flows/sec in
				scale("%.1f", ($in->{flows}/300)) .
				    sprintf(" (%.1f%%)",
					    percent($in->{flows}, 
                                                 $CUFlow::totals{in}{flows})),
				
				# Flows/sec out
				scale("%.1f", ($out->{flows}/300)) .
				    sprintf(" (%.1f%%)",
                                            percent($out->{flows}, 
                                                $CUFlow::totals{out}{flows})));


		$table->setRowAlign($row, 'RIGHT');
		$table->setCellBGColor($row,
				       $columns{$key} + ('out' eq $dir),
				       '#add8e6'); # light blue
		$row++;
	    }
	    print HTML "<p>\n$table</p>\n\n";
	}
    }    

    # Print footers
    print HTML "\n</center>\n</body>\n</html>\n";

    # Close the file, and make $scorepage point at this page
    close HTML;
    unlink $CUFlow::scorepage || 
	die "Could not remove $CUFlow::scorepage ($!)\n";
    symlink $file, $CUFlow::scorepage ||
	die "Could not create symlink to $CUFlow::scorepage ($!)\n";

    if ($CUFlow::aggscorekeep > 0) {
	# Merge newaggdata and aggdata
	foreach $ip (keys %newaggdata) {
	    $aggdata{$ip}->{'count'}++;
	    $aggdata{$ip}->{'bytesin'}  += $newaggdata{$ip}->{'bytesin'};
	    $aggdata{$ip}->{'bytesout'} += $newaggdata{$ip}->{'bytesout'};
	    $aggdata{$ip}->{'pktsin'}   += $newaggdata{$ip}->{'pktsin'};
	    $aggdata{$ip}->{'pktsout'}  += $newaggdata{$ip}->{'pktsout'};
	    $aggdata{$ip}->{'flowsin'}  += $newaggdata{$ip}->{'flowsin'};
	    $aggdata{$ip}->{'flowsout'} += $newaggdata{$ip}->{'flowsout'};
	}

	# Increment counter
	$aggdata{'numresults'}++;
	
	if ($aggdata{'numresults'} > $CUFlow::NUMKEEP) {
	    # Prune this shit
	    $aggdata{'numresults'} >>= 1;
	    foreach $ip (keys %aggdata) {
		next if ($ip =~ /numresults/);           # Skip this, not a ref
		if ($aggdata{$ip}->{'count'} == 1) {     # Delete singletons
		    delete $aggdata{$ip};
		} else {
		    $aggdata{$ip}->{'count'}    >>= 1;   # Divide by 2
		    $aggdata{$ip}->{'bytesin'}  >>= 1;
		    $aggdata{$ip}->{'bytesout'} >>= 1;
		    $aggdata{$ip}->{'pktsin'}   >>= 1;
		    $aggdata{$ip}->{'pktsout'}  >>= 1;
		    $aggdata{$ip}->{'flowsin'}  >>= 1;
		    $aggdata{$ip}->{'flowsout'} >>= 1;
		}
	    }
	}

	# Write the aggregate table
	&writeAggScoreboard(\%aggdata);
	
	# Save the aggregation data
	&writeAggFile(\%aggdata);
    }
    return;
}

# Simple percentifier, usage percent(1,10) returns 10
# Also stolen from CampusIO.pm
sub percent($$) {
   my $num = shift;
   my $denom = shift;
   return(0) if (0 == $denom);
   return 100*($num/$denom)
}

# Print a large number in sensible units. 
# Arg1 = sprintf format string
# Arg2 = value to put in it.
# Also stolen from CampusIO.pm, where Dave Plonka says...
# This is based somewhat on Tobi Oetiker's code in rrd_graph.c: 
sub scale($$) { 
   my $fmt = shift;
   my $value = shift;
   my @symbols = ("a", # 10e-18 Ato
                  "f", # 10e-15 Femto
                  "p", # 10e-12 Pico
                  "n", # 10e-9  Nano
                  "u", # 10e-6  Micro
                  "m", # 10e-3  Milli
                  " ", # Base
                  "k", # 10e3   Kilo
                  "M", # 10e6   Mega
                  "G", # 10e9   Giga
                  "T", # 10e12  Terra
                  "P", # 10e15  Peta
                  "E");# 10e18  Exa

   my $symbcenter = 6;
   my $digits = (0 == $value)? 0 : floor(log($value)/log(1000));
   return sprintf(${fmt} . " %s", $value/pow(1000, $digits),
                  $symbols[$symbcenter+$digits])
}

sub DESTROY {
   my $self = shift;

   $self->SUPER::DESTROY
}

=head1 BUGS

Some.

Majorly, flows that have the same source and destination port will end up
being counted twice (in either the inbound or outbound direction) for the
purposes of measuring the percentages in CUGrapher. The total traffic is
correct, but the assumptions CUGrapher makes lead to a negative percentage
of "other traffic".

This may just be a cosmetic bug with CUGrapher. If an inside host transfers
5megs to an outside host from port 80 to port 80, we need to update both
counters. The bug is in assuming that the sum of all the services totals
will be less than the total traffic, which may not be the case if some
traffic belongs to more than 1 service. More stuff for 2.0...

scoreboard() assumes our flowfile is 300 seconds worth of data. It should
figure out over how many seconds the records run, and divide by that instead.

report and its subroutines need to do locking

=head1 AUTHOR

Johan Andersen <johan@columbia.edu>

=head1 CONTRIBUTORS

Matt Selsky <selsky@columbia.edu>    - CUGrapher and co-developer
Terje Krogdahl <terje@krogdahl.net>  - Sampled netflow support and AS graphing
Joerg Borchain <jd@europeonline.net> - CUGrapher menu on displayed graphs page

=head1 REPORT PROBLEMS

Please contact <cuflow-users@columbia.edu> to get help with CUFlow.

=cut

1
