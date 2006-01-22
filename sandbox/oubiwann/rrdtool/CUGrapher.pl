#! /usr/bin/perl -w

# CUGrapher.pl
# $Revision: 1.45 $
# Author: Matt Selsky <selsky@columbia.edu>
# Contact for help: <cuflow-users@columbia.edu>

use strict;
use CGI::Pretty qw(-nosticky :standard);
use RRDs;
use Digest::MD5 qw(md5_hex);

### Local settings ###

# directory with rrd files
my $rrddir = "/cflow/reports/rrds";
# default number of hours to go back
my $hours = 48;
# duration of graph, starting from $hours ago
my $duration;
# organization name
my $organization = "Estimated Columbia University Campus";
# default graph width
my $width = 640;
# default graph height
my $height = 320;
# default image type (png/gif)
my $imageType = 'png';

### End local settings ###

# auto-flush STDOUT
$| = 1;

# report -> proper name
my %reportName = ( 'bits' => 'bits',
		   'pkts' => 'packets',
		   'flows' => 'flows' );

unless( param() ) {
    &showMenu();
}

if (param('showmenu')) {
    Delete('showmenu');
    &showMenu(self_url());
}

# protocol/service -> filename
my %filename;
# lists of networks/protocols/services/routers
my (%network, %as, %protocol, %service, %tos, @router);
# should we show totals also?
my %total;
# hash for colors/CDEFs
my (%color, %cdef);
# are we in debug mode?
my $debug;

&getRouter();
&getProtocols();
&getServices();
&getTOS();
&getNetworks();
&getASs();
&getImageType();
&setColors();
&getHours();
&getDuration();
&getWidth();
&getHeight();
&getTotal();
&getDebug();

&doReport();

################################################################

# Image generation and display

sub generateImage {
    my @args = @_;
    my ($err1, $err2);

    unless( $debug ) {
	print header( -type => "image/${imageType}", -expires => 'now' );
        RRDs::graph( '-', @args);
	$err1 = RRDs::error;
	if( $err1 ) { # log & attempt to create image w/ error message in it
	    warn $err1, "\n";
	    RRDs::graph( '-', "--width=".$width,
		       "COMMENT:graph failed ($err1)\\n");
	    $err2 = RRDs::error;
	    if( $err2 ) { # log to stderr since we are totally broken
		warn "graph failed ($err1) and warning failed ($err2)\n";
	    }
	}
    }
    else {
	print header, '<pre>', join(" \\\n", @args), "\n"; exit;
    }
}

sub showMenu {
    my ($imgurl) = @_;
    my $q = new CGI::Pretty(""); # Avoid inheriting the parameter list
    

    print $q->header, $q->start_html( -title => 'Generate FlowScan graphs on the fly',
				      -bgcolor => 'ffffff' );

    print $q->center( $q->img({ -src => $imgurl, -align => 'center', 
				-alt => 'The Graph you requested'})) if ($imgurl);
    
    print $q->start_form( -action => $q->url(), -method => 'get' ); # Just the url, without query string

    print $q->start_table( { -align => 'center',
			     -cellspacing => '10' } );

    print $q->start_Tr( { -align => 'center',
			  -valign => 'top' } );

    print $q->td( { -rowspan => '2' },
		  "Report: ",
		  $q->popup_menu( -name => 'report',
				  -values => [sort keys %reportName],
				  -default => '' ) );
    
    my %hours = ( 24 => '24 hours',
		  36 => '36 hours',
		  48 => '48 hours',
		  168 => '1 week',
		  720 => '1 month' );

    print $q->td( { -align => 'right' },
		  "Time period: ",
		  $q->popup_menu( -name => 'hours',
				  -values => [sort {$a <=> $b} keys %hours],
				  -default => $hours,
				  -labels => \%hours ) );
    
    print $q->td( { -rowspan => '2' },
		  "Image type: ",
		  $q->popup_menu( -name => 'imageType',
				  -values => ['png', 'gif'],
				  -default => 'png' ) );
    
    print $q->td( { -rowspan => '2' },
		  "Width:",
		  $q->textfield( -name => "width",
				 -default => $width,
				 -size => 7 ) );
    
    print $q->td( { -rowspan => '2' },
		  "Height:",
		  $q->textfield( -name => "height",
				 -default => $height,
				 -size => 7 ) );

    print $q->end_Tr();

    print $q->start_Tr( { -align => 'center' } );

    print $q->td( { -align => 'right' },
		  "Duration: ",
		  $q->popup_menu( -name => 'duration',
				  -values => ['', sort {$a <=> $b} keys %hours],
				  -labels => \%hours ) );

    print $q->end_Tr();

    print $q->end_table();

    print $q->start_table( { align => 'center',
			     -border => '1' } );
    print $q->Tr( { -align => 'center' },
		  $q->td( i('Router') ),
		  $q->td( i('Protocol') ), $q->td( i('All Protos') ),
		  $q->td( i('Service') ), $q->td( i('All Svcs') ),
		  $q->td( i('TOS') ), $q->td( i('All TOS') ),
		  $q->td( i('AS') ),
		  $q->td( i('Network') ),
		  $q->td( i('Total') ) );    
    foreach my $router ( 'all', sort &getRouterList() ) {
	print $q->start_Tr;

	print $q->td( { -align => 'center' }, $q->b($router),
		      $q->hidden( -name => 'router', -default => $router ) );

	print $q->td( $q->scrolling_list( -name => "${router}_protocol",
					  -values => [sort &getProtocolList()],
					  -size => 5,
					  -multiple => 'true' ) );

	print $q->td( $q->checkbox( -name => "${router}_all_protocols",
				    -value => '1',
				    -label => 'Yes' ) );
	
	print $q->td( $q->scrolling_list( -name => "${router}_service",
					  -values => [sort &getServiceList()],
					  -size => 5,
					  -multiple => 'true' ) );

	print $q->td( $q->checkbox( -name => "${router}_all_services",
				    -value => '1',
				    -label => 'Yes' ) );

	print $q->td( $q->scrolling_list( -name => "${router}_tos",
					  -values => [sort &getTOSList()],
					  -size => 5,
					  -multiple => 'true' ) );

	print $q->td( $q->checkbox( -name => "${router}_all_tos",
				    -value => '1',
				    -label => 'Yes' ) );

	print $q->td( $q->scrolling_list( -name => "${router}_as",
					  -values => [sort &getASList()],
					  -size => 5,
					  -multiple => 'true' ) );

	if ($router eq 'all') {
	    print $q->td( $q->scrolling_list( -name => "${router}_network",
					      -values => [sort &getNetworkList()],
					      -size => 5,
					      -multiple => 'true' ) );
	} else {
	    print $q->td( '&nbsp;' );
	}
	
	print $q->td( $q->checkbox( -name => "${router}_total",
				    -value => '1',
				    -label => 'Yes') );
	
	print $q->end_Tr;
    }
    print $q->end_table();
    
    print $q->br;

    print $q->hidden('showmenu','1');

    print $q->center( $q->submit( -name => '',
				  -value => 'Generate graph' ),
		      $q->checkbox( -name => 'legend',
				    -checked => 'ON',
				    -value => '1',
				    -label => 'Legend?' ) );

    print $q->end_form;

    print $q->end_html;    
    exit;
}

sub browserDie {
    print header;
    print start_html(-title => 'Error Occurred',
		     -bgcolor => 'ffffff');
    print '<pre>', "\n";
    print @_;
    print "\n", '</pre>', "\n";
    exit;
}

## Parse param()

sub getImageType {
    if( param('imageType') ) {
	if( param('imageType') eq 'png' || param('imageType') eq 'gif' ) {
	    $imageType = param('imageType');
	} else { &browserDie('Invalid imageType parameter') }
    }
}

sub getRouter {
    if( !param('router') ) {
	push @router, 'all';
    }
    # XXX how much is tainting a problem? .. attacks, etc
    else {
	foreach ( param('router') ) {
	    s/\.\./_/g;
	    if( $_ eq 'all' ) { push @router, 'all' }
	    elsif( -d $rrddir.'/'.$_ ) { push @router, $_ }
	    else { &browserDie('Invalid router parameter') }
	}
    }
}

sub getHours {
    if( param('hours') ) {
	if( param('hours') =~ /^\d+$/ ) { $hours = param('hours') }
	else { &browserDie( "Invalid hours parameter" ) }
    }
}

sub getDuration {
    if( param('duration') ) {
	if( param('duration') =~ /^\d+$/ ) { $duration = param('duration') }
	else { &browserDie( "Invalid duration parameter" ) }
    } else { $duration = $hours; }
}

sub getWidth {
    if( param('width') ) {
	if( param('width') =~ /^\d+$/ ) { $width = param('width') }
	else { &browserDie( "Invalid width parameter" ) }
    }
}

sub getHeight {
    if( param('height') ) {
	if( param('height') =~ /^\d+$/ ) { $height = param('height') }
	else { &browserDie( "Invalid height parameter" ) }
    }
}

sub getTotal {
    foreach my $r (@router) {
	if( param("${r}_all") ) {
	    $total{$r} = 1;
	}
	elsif( param("${r}_total") ) {
	    $total{$r} = param("${r}_total");
	}
    }
}

sub getDebug {
    if( param('debug') && param('debug') eq '1' ) {
	$debug = 1;
    } else { $debug = 0 }
}

sub doReport {
    defined param('report') or &browserDie( "You must specify report type" );

    return &generateImage( &io_report( param('report'), param('legend') ) );
}

# Generate list of protocols and resolve filenames
sub getProtocols {
    foreach my $r (@router) {
	if( param("${r}_all_protocols") ) {
	    push @{$protocol{$r}}, &getProtocolList();
	}
	elsif( param("${r}_protocol") ) {
	    push @{$protocol{$r}}, param("${r}_protocol");
	}
	foreach my $p ( @{$protocol{$r}} ) {
	    my $file;
	    if( $r eq 'all' ) { $file = "${rrddir}/protocol_${p}.rrd"}
	    else { $file =  "${rrddir}/${r}/protocol_${p}.rrd"}
	    -f $file or &browserDie("cannot find $file");
	    $filename{$r}{$p} = $file;
	}
	if( $r eq 'all' ) { $filename{$r}{'total'} = "${rrddir}/total.rrd" }
	else { $filename{$r}{'total'} = "${rrddir}/${r}/total.rrd" }
    }
}

# Generate list of services and resolve filenames
sub getServices {
    foreach my $r (@router) {
	if( param("${r}_all_services") ) {
	    push @{$service{$r}}, &getServiceList();
	}
	elsif( param("${r}_service") ) {
	    push @{$service{$r}}, param("${r}_service");
	}
	foreach my $s ( @{$service{$r}} ) {
	    my ($file_base, $file_src, $file_dst);
	    if( $r eq 'all' ) {
		$file_base = "${rrddir}/service_${s}";
		$file_src = "${rrddir}/service_${s}_src.rrd";
		$file_dst = "${rrddir}/service_${s}_dst.rrd";
	    } else {
		$file_base = "${rrddir}/${r}/service_${s}";
		$file_src = "${rrddir}/${r}/service_${s}_src.rrd";
		$file_dst = "${rrddir}/${r}/service_${s}_dst.rrd";
	    }
	    -f $file_src or &browserDie("cannot find $file_src");
	    -f $file_dst or &browserDie("cannot find $file_dst");
	    $filename{$r}{$s} = $file_base;
	}
    }
}

# Generate list of TOS and resolve filenames
sub getTOS {
    foreach my $r (@router) {
	if( param("${r}_all_tos") ) {
	    push @{$tos{$r}}, &getTOSList();
	}
	elsif( param("${r}_tos") ) {
	    push @{$tos{$r}}, param("${r}_tos");
	}
	foreach my $t ( @{$tos{$r}} ) {
	    my $file;
	    if( $r eq 'all' ) { $file = "${rrddir}/tos_${t}.rrd"}
	    else { $file =  "${rrddir}/${r}/tos_${t}.rrd"}
	    -f $file or &browserDie("cannot find $file");
	    $filename{$r}{$t} = $file;
	}
	if( $r eq 'all' ) { $filename{$r}{'total'} = "${rrddir}/total.rrd" }
	else { $filename{$r}{'total'} = "${rrddir}/${r}/total.rrd" }
    }
}

# Generate list of networks and resolve filenames
sub getNetworks {
    # Networks are only in the all category, for total traffic

    if( param("all_network") ) {
	push @{$network{'all'}}, param("all_network");
    }
    
    foreach my $n ( param("all_network") ) {
	my $file = "${rrddir}/network_${n}.rrd";

	-f $file or &browserDie("cannot find $file");

	$filename{'all'}{$n} = $file;
    }
}

# Generate a list of ASes and resolve filenames
sub getASs {
    foreach my $r (@router) {
	if( param("${r}_all_as") ) {
	    push @{$as{$r}}, &getASList();
	}
	elsif( param("${r}_as") ) {
	    push @{$as{$r}}, param("${r}_as");
	}
	foreach my $t ( @{$as{$r}} ) {
	    my $file;
	    if( $r eq 'all' ) { $file = "${rrddir}/as_${t}.rrd"}
	    else { $file =  "${rrddir}/${r}/as_${t}.rrd"}
	    -f $file or &browserDie("cannot find $file");
	    $filename{$r}{$t} = $file;
	}
	if( $r eq 'all' ) { $filename{$r}{'total'} = "${rrddir}/total.rrd" }
	else { $filename{$r}{'total'} = "${rrddir}/${r}/total.rrd" }
    }
}

## Assign each protocol/service a color

sub setColors {
    # "nice" colors. taken from Packeteer PacketShaper's web interface
    # (via Dave Plonka) and other places
    my @safe_colors = ( 0x746FAE, # lavender
			0x993366, # maroon
  			0xB8860B, # dark goldenrod
  			0xCCFFFF, # lt. cyan
  			0x660066, # purple
  			0xFF6666, # orange
  			0x0066CC, # med. blue
  			0xCCCCFF, # pale lavender
  			0x000066, # dk. blue
  			0x0000FF, # blue
  			0xFFFF00 # yellow
  			);

    foreach my $r (@router) {
	foreach my $n (@{$network{$r}}) {
	    $color{$r}{$n} = &iterateColor(\@safe_colors);
	}

	foreach my $a (@{$as{$r}}) {
	    $color{$r}{$a} = &iterateColor(\@safe_colors);
	}

	foreach my $p (@{$protocol{$r}}) {
	    $color{$r}{$p} = &iterateColor(\@safe_colors);
	}
	
	foreach my $s (@{$service{$r}}) {
	    $color{$r}{$s}{'src'} = &iterateColor(\@safe_colors);
	    $color{$r}{$s}{'dst'} = &iterateColor(\@safe_colors);
	}

	foreach my $t (@{$tos{$r}}) {
	    $color{$r}{$t} = &iterateColor(\@safe_colors);
	}

	$color{$r}{'total'} = &iterateColor(\@safe_colors);
    }
}

# use a color and move it to the back
sub iterateColor {
    my $color = shift @{$_[0]};
    push @{$_[0]}, $color;

    return sprintf('#%06x', $color);
}

# Generate list of available protocols
sub getProtocolList {
    opendir( DIR, $rrddir ) or &browserDie("open $rrddir failed ($!)");
    @_ = grep { /^protocol_.*\.rrd$/ } readdir( DIR );
    closedir DIR;
    
    foreach (@_) {
	s/^protocol_(.*)\.rrd$/$1/;
    }

    return @_;
}

# Generate list of available services
sub getServiceList {
    opendir( DIR, $rrddir ) or &browserDie("open $rrddir failed ($!)");
    @_ = grep { /^service_.*_src\.rrd$/ } readdir( DIR );
    closedir DIR;

    foreach (@_) {
	s/^service_(.*)_src\.rrd$/$1/;
    }

    return @_;
}

# Generate list of available TOS
sub getTOSList {
    opendir( DIR, $rrddir ) or &browserDie("open $rrddir failed ($!)");
    @_ = grep { /^tos_.*\.rrd$/ } readdir( DIR );
    closedir DIR;

    foreach (@_) {
	s/^tos_(.*)\.rrd$/$1/;
    }

    return @_;
}

# Generate list of available ASes
sub getASList {
    opendir( DIR, $rrddir ) or &browserDie("open $rrddir failed ($!)");
    @_ = grep { /^as_.*\.rrd$/ } readdir( DIR );
    closedir DIR;

    foreach (@_) {
	s/^as_(.*)\.rrd$/$1/;
    }

    return @_;
}

# Generate list of available networks
sub getNetworkList {
    opendir( DIR, $rrddir ) or &browserDie("open $rrddir failed ($!)");
    @_ = grep { /^network_.*\.rrd$/ } readdir( DIR );
    closedir DIR;

    foreach (@_) {
	s/^network_(.*)\.rrd$/$1/;
    }

    return @_;
}

# Generate list of available routers
sub getRouterList {
    opendir( DIR, $rrddir ) or &browserDie("open $rrddir failed ($!)");
    while( $_ = readdir( DIR ) ) {
	if( !/^\.\.?/ && -d $rrddir.'/'.$_ ) {
	    push @_, $_;
	}
    }
    closedir DIR;

    return @_;
}

# rrdtool has annoying format rules so just use MD5 like cricket does
sub cleanDEF {
    my $def = shift;

    return $def if $debug;

    unless( exists $cdef{$def} ) {
	$cdef{$def} = substr( md5_hex($def), 0, 29);
    }
    return $cdef{$def};
}

# make service labels a consistent length
sub cleanServiceLabel {
    my $labelLength = 15;
    my $s = shift;
    my $txt = shift;
    return uc($s) . ' ' x ($labelLength - length $s) . $txt;
}

# make protocol labels a consistent length
sub cleanProtocolLabel {
    my $labelLength = 47;
    my $p = shift;
    return uc($p) . ' ' x ($labelLength - length $p);
}

# make other percentage labels a consistent length
sub cleanOtherLabel {
    my $labelLength = 51;
    my $label = shift;
    my $format = shift;
    return $label . ' ' x ($labelLength - length $label) . $format;
}

sub io_report {
    my $reportType = shift;
    my $legend = shift;
    my @args;
    my $str;

    unless( exists $reportName{$reportType} ) {
	&browserDie('invalid report parameter');
    }

    push @args, ('--interlaced',
		 '--imgformat='.uc($imageType),
		 '--vertical-label='.$reportName{$reportType}.' per second',
		 "--title=${organization} Well Known Protocols/Services, ".
		 "\u${reportName{$reportType}}, +out/-in",
		 "--start=".(time - $hours*60*60),
		 "--end=".(time - $hours*60*60 + $duration*60*60),
		 "--width=${width}",
		 "--height=${height}",
		 '--alt-autoscale');

    push @args, '--no-legend' unless($legend);

    # CDEF for total
    foreach my $r (@router) {
	if( $reportType eq 'bits' ) {
	    push @args, ('DEF:'.&cleanDEF("${r}_total_out_bytes").'='.$filename{$r}{'total'}.':out_bytes:AVERAGE',
			 'DEF:'.&cleanDEF("${r}_total_in_bytes").'='.$filename{$r}{'total'}.':in_bytes:AVERAGE',
			 'CDEF:'.&cleanDEF("${r}_total_out_bits").'='.&cleanDEF("${r}_total_out_bytes").',8,*',
			 'CDEF:'.&cleanDEF("${r}_total_in_bits").'='.&cleanDEF("${r}_total_in_bytes").',8,*',
			 'CDEF:'.&cleanDEF("${r}_total_in_bits_neg").'='.&cleanDEF("${r}_total_in_bits").',-1,*');
	} else {
	    push @args, ('DEF:'.&cleanDEF("${r}_total_out_${reportType}").'='.$filename{$r}{'total'}.":out_${reportType}:AVERAGE",
			 'DEF:'.&cleanDEF("${r}_total_in_${reportType}").'='.$filename{$r}{'total'}.":in_${reportType}:AVERAGE",
			 'CDEF:'.&cleanDEF("${r}_total_in_${reportType}_neg").'='.&cleanDEF("${r}_total_in_${reportType}").',-1,*');
	}
    }
	
    # CDEFs for each service
    foreach my $r (@router) {
	foreach my $s (@{$service{$r}}) {
	    if( $reportType eq 'bits' ) {
		push @args, ('DEF:'.&cleanDEF("${r}_${s}_src_out_bytes").'='.$filename{$r}{$s}.'_src.rrd:out_bytes:AVERAGE',
			     'DEF:'.&cleanDEF("${r}_${s}_src_in_bytes").'='.$filename{$r}{$s}.'_src.rrd:in_bytes:AVERAGE',
			     'CDEF:'.&cleanDEF("${r}_${s}_src_out_bits").'='.&cleanDEF("${r}_${s}_src_out_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${s}_src_in_bits").'='.&cleanDEF("${r}_${s}_src_in_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${s}_src_in_bits_neg").'='.&cleanDEF("${r}_${s}_src_in_bytes").',8,*,-1,*',
			     'DEF:'.&cleanDEF("${r}_${s}_dst_out_bytes").'='.$filename{$r}{$s}.'_dst.rrd:out_bytes:AVERAGE',
			     'DEF:'.&cleanDEF("${r}_${s}_dst_in_bytes").'='.$filename{$r}{$s}.'_dst.rrd:in_bytes:AVERAGE',
			     'CDEF:'.&cleanDEF("${r}_${s}_dst_out_bits").'='.&cleanDEF("${r}_${s}_dst_out_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${s}_dst_in_bits").'='.&cleanDEF("${r}_${s}_dst_in_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${s}_dst_in_bits_neg").'='.&cleanDEF("${r}_${s}_dst_in_bytes").',8,*,-1,*');
	    } else {
		push @args, ('DEF:'.&cleanDEF("${r}_${s}_src_out_${reportType}").'='.$filename{$r}{$s}."_src.rrd:out_${reportType}:AVERAGE",
			     'DEF:'.&cleanDEF("${r}_${s}_src_in_${reportType}").'='.$filename{$r}{$s}."_src.rrd:in_${reportType}:AVERAGE",
			     'CDEF:'.&cleanDEF("${r}_${s}_src_in_${reportType}_neg").'='.&cleanDEF("${r}_${s}_src_in_${reportType}").',-1,*',
			     'DEF:'.&cleanDEF("${r}_${s}_dst_out_${reportType}").'='.$filename{$r}{$s}."_dst.rrd:out_${reportType}:AVERAGE",
			     'DEF:'.&cleanDEF("${r}_${s}_dst_in_${reportType}").'='.$filename{$r}{$s}."_dst.rrd:in_${reportType}:AVERAGE",
			     'CDEF:'.&cleanDEF("${r}_${s}_dst_in_${reportType}_neg").'='.&cleanDEF("${r}_${s}_dst_in_${reportType}").',-1,*');
	    }
	}
    }

    # CDEFs for service by percentage
    foreach my $r (@router) {
	if( scalar @{$service{$r}} ) {
	    foreach my $s ( @{$service{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${s}_in_pct").'='.&cleanDEF("${r}_${s}_src_in_${reportType}").','.&cleanDEF("${r}_${s}_dst_in_${reportType}").',+,'.&cleanDEF("${r}_total_in_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_service_in_pct").'=100';
	    foreach my $s ( @{$service{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${s}_in_pct").',-';
	    }
	    push @args, $str;
	    
	    foreach my $s ( @{$service{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${s}_out_pct").'='.&cleanDEF("${r}_${s}_src_out_${reportType}").','.&cleanDEF("${r}_${s}_dst_out_${reportType}").',+,'.&cleanDEF("${r}_total_out_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_service_out_pct").'=100';
	    foreach my $s ( @{$service{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${s}_out_pct").',-';
	    }
	    push @args, $str;
	}
    }
	
    # CDEFs for each protocol
    foreach my $r (@router) {
	foreach my $p ( @{$protocol{$r}} ) {
	    if( $reportType eq 'bits' ) {
		push @args, ('DEF:'.&cleanDEF("${r}_${p}_out_bytes").'='.$filename{$r}{$p}.':out_bytes:AVERAGE',
			     'DEF:'.&cleanDEF("${r}_${p}_in_bytes").'='.$filename{$r}{$p}.':in_bytes:AVERAGE',
			     'CDEF:'.&cleanDEF("${r}_${p}_out_bits").'='.&cleanDEF("${r}_${p}_out_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${p}_in_bits").'='.&cleanDEF("${r}_${p}_in_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${p}_in_bits_neg").'='.&cleanDEF("${r}_${p}_in_bytes").',8,*,-1,*');
	    } else {
		push @args, ('DEF:'.&cleanDEF("${r}_${p}_out_${reportType}").'='.$filename{$r}{$p}.":out_${reportType}:AVERAGE",
			     'DEF:'.&cleanDEF("${r}_${p}_in_${reportType}").'='.$filename{$r}{$p}.":in_${reportType}:AVERAGE",
			     'CDEF:'.&cleanDEF("${r}_${p}_in_${reportType}_neg").'='.&cleanDEF("${r}_${p}_in_${reportType}").',-1,*');
	    }
	}
    }

    # CDEFs for protocol by percentage
    foreach my $r (@router) {
	if( scalar @{$protocol{$r}} ) { 
	    foreach my $p ( @{$protocol{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${p}_in_pct").'='.&cleanDEF("${r}_${p}_in_${reportType}").','.&cleanDEF("${r}_total_in_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_protocol_in_pct").'=100';
	    foreach my $p ( @{$protocol{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${p}_in_pct").',-';
	    }
	    push @args, $str;
	    
	    foreach my $p ( @{$protocol{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${p}_out_pct").'='.&cleanDEF("${r}_${p}_out_${reportType}").','.&cleanDEF("${r}_total_out_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_protocol_out_pct").'=100';
	    foreach my $p ( @{$protocol{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${p}_out_pct").',-';
	    }
	    push @args, $str;
	}
    }

    # CDEFs for each AS
    foreach my $r (@router) {
	foreach my $p ( @{$as{$r}} ) {
	    if( $reportType eq 'bits' ) {
		push @args, ('DEF:'.&cleanDEF("${r}_${p}_out_bytes").'='.$filename{$r}{$p}.':out_bytes:AVERAGE',
			     'DEF:'.&cleanDEF("${r}_${p}_in_bytes").'='.$filename{$r}{$p}.':in_bytes:AVERAGE',
			     'CDEF:'.&cleanDEF("${r}_${p}_out_bits").'='.&cleanDEF("${r}_${p}_out_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${p}_in_bits").'='.&cleanDEF("${r}_${p}_in_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${p}_in_bits_neg").'='.&cleanDEF("${r}_${p}_in_bytes").',8,*,-1,*');
	    } else {
		push @args, ('DEF:'.&cleanDEF("${r}_${p}_out_${reportType}").'='.$filename{$r}{$p}.":out_${reportType}:AVERAGE",
			     'DEF:'.&cleanDEF("${r}_${p}_in_${reportType}").'='.$filename{$r}{$p}.":in_${reportType}:AVERAGE",
			     'CDEF:'.&cleanDEF("${r}_${p}_in_${reportType}_neg").'='.&cleanDEF("${r}_${p}_in_${reportType}").',-1,*');
	    }
	}
    }

    # CDEFs for AS by percentage
    foreach my $r (@router) {
	if( scalar @{$as{$r}} ) { 
	    foreach my $p ( @{$as{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${p}_in_pct").'='.&cleanDEF("${r}_${p}_in_${reportType}").','.&cleanDEF("${r}_total_in_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_as_in_pct").'=100';
	    foreach my $p ( @{$as{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${p}_in_pct").',-';
	    }
	    push @args, $str;
	    
	    foreach my $p ( @{$as{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${p}_out_pct").'='.&cleanDEF("${r}_${p}_out_${reportType}").','.&cleanDEF("${r}_total_out_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_as_out_pct").'=100';
	    foreach my $p ( @{$as{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${p}_out_pct").',-';
	    }
	    push @args, $str;
	}
    }

    # CDEFs for each TOS
    foreach my $r (@router) {
	foreach my $t ( @{$tos{$r}} ) {
	    if( $reportType eq 'bits' ) {
		push @args, ('DEF:'.&cleanDEF("${r}_${t}_out_bytes").'='.$filename{$r}{$t}.':out_bytes:AVERAGE',
			     'DEF:'.&cleanDEF("${r}_${t}_in_bytes").'='.$filename{$r}{$t}.':in_bytes:AVERAGE',
			     'CDEF:'.&cleanDEF("${r}_${t}_out_bits").'='.&cleanDEF("${r}_${t}_out_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${t}_in_bits").'='.&cleanDEF("${r}_${t}_in_bytes").',8,*',
			     'CDEF:'.&cleanDEF("${r}_${t}_in_bits_neg").'='.&cleanDEF("${r}_${t}_in_bytes").',8,*,-1,*');
	    } else {
		push @args, ('DEF:'.&cleanDEF("${r}_${t}_out_${reportType}").'='.$filename{$r}{$t}.":out_${reportType}:AVERAGE",
			     'DEF:'.&cleanDEF("${r}_${t}_in_${reportType}").'='.$filename{$r}{$t}.":in_${reportType}:AVERAGE",
			     'CDEF:'.&cleanDEF("${r}_${t}_in_${reportType}_neg").'='.&cleanDEF("${r}_${t}_in_${reportType}").',-1,*');
	    }
	}
    }

    # CDEFs for TOS by percentage
    foreach my $r (@router) {
	if( scalar @{$tos{$r}} ) { 
	    foreach my $t ( @{$tos{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${t}_in_pct").'='.&cleanDEF("${r}_${t}_in_${reportType}").','.&cleanDEF("${r}_total_in_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_tos_in_pct").'=100';
	    foreach my $t ( @{$tos{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${t}_in_pct").',-';
	    }
	    push @args, $str;
	    
	    foreach my $t ( @{$tos{$r}} ) {
		push @args, 'CDEF:'.&cleanDEF("${r}_${t}_out_pct").'='.&cleanDEF("${r}_${t}_out_${reportType}").','.&cleanDEF("${r}_total_out_${reportType}").',/,100,*';
	    }
	    
	    $str = 'CDEF:'.&cleanDEF("${r}_other_tos_out_pct").'=100';
	    foreach my $t ( @{$tos{$r}} ) {
		$str .= ','.&cleanDEF("${r}_${t}_out_pct").',-';
	    }
	    push @args, $str;
	}
    }

    # CDEFs for each network
    foreach my $n ( @{$network{'all'}} ) {
	if( $reportType eq 'bits' ) {
	    push @args, ('DEF:'.&cleanDEF("all_${n}_out_bytes").'='.$filename{'all'}{$n}.':out_bytes:AVERAGE',
			 'DEF:'.&cleanDEF("all_${n}_in_bytes").'='.$filename{'all'}{$n}.':in_bytes:AVERAGE',
			 'CDEF:'.&cleanDEF("all_${n}_out_bits").'='.&cleanDEF("all_${n}_out_bytes").',8,*',
			 'CDEF:'.&cleanDEF("all_${n}_in_bits").'='.&cleanDEF("all_${n}_in_bytes").',8,*',
			 'CDEF:'.&cleanDEF("all_${n}_in_bits_neg").'='.&cleanDEF("all_${n}_in_bytes").',8,*,-1,*');
	} else {
	    push @args, ('DEF:'.&cleanDEF("all_${n}_out_${reportType}").'='.$filename{'all'}{$n}.":out_${reportType}:AVERAGE",
			 'DEF:'.&cleanDEF("all_${n}_in_${reportType}").'='.$filename{'all'}{$n}.":in_${reportType}:AVERAGE",
			 'CDEF:'.&cleanDEF("all_${n}_in_${reportType}_neg").'='.&cleanDEF("all_${n}_in_${reportType}").',-1,*');
	}
    }

    # CDEFs for network by percentage
    if( scalar @{$network{'all'}} ) { 
	foreach my $n ( @{$network{'all'}} ) {
	    push @args, 'CDEF:'.&cleanDEF("all_${n}_in_pct").'='.&cleanDEF("all_${n}_in_${reportType}").','.&cleanDEF("all_total_in_${reportType}").',/,100,*';
	}
	    
	$str = 'CDEF:'.&cleanDEF("all_other_network_in_pct").'=100';
	foreach my $n ( @{$network{'all'}} ) {
	    $str .= ','.&cleanDEF("all_${n}_in_pct").',-';
	}
	push @args, $str;
	    
	foreach my $n ( @{$network{'all'}} ) {
	    push @args, 'CDEF:'.&cleanDEF("all_${n}_out_pct").'='.&cleanDEF("all_${n}_out_${reportType}").','.&cleanDEF("all_total_out_${reportType}").',/,100,*';
	}
	    
	$str = 'CDEF:'.&cleanDEF("all_other_network_out_pct").'=100';

	foreach my $n ( @{$network{'all'}} ) {
	    $str .= ','.&cleanDEF("all_${n}_out_pct").',-';
	}
	push @args, $str;
    }
	
    # Graph commands
    my $count;
	
    foreach my $r (@router) {
	$count = 0;

	# router name
	if( scalar @{$service{$r}} || scalar @{$protocol{$r}} || scalar @{$tos{$r}}
	    || exists $total{$r} ) {
	    push @args, 'COMMENT: Router: '.$r.'\n';
	}

	# service outbound, percentages
	foreach my $s ( @{$service{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${s}_src_out_".$reportType).$color{$r}{$s}{'src'}.':'.&cleanServiceLabel($s, ' src  +');
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${s}_src_out_".$reportType).$color{$r}{$s}{'src'}.':'.&cleanServiceLabel($s, ' src  +');
	    }
	    push @args, 'STACK:'.&cleanDEF("${r}_${s}_dst_out_".$reportType).$color{$r}{$s}{'dst'}.':'.&cleanServiceLabel($s, ' dst  ');
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${s}_out_pct").':AVERAGE:%.1lf%% Out';
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${s}_in_pct").':AVERAGE:%.1lf%% In\n',
	}
	
	# protocol outbound, percentages
	foreach my $p ( @{$protocol{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${p}_out_".$reportType).$color{$r}{$p}.':'.&cleanProtocolLabel($p);
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${p}_out_".$reportType).$color{$r}{$p}.':'.&cleanProtocolLabel($p);
	    }
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${p}_out_pct").':AVERAGE:%.1lf%% Out';
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${p}_in_pct").':AVERAGE:%.1lf%% In\n';
	}

	# tos outbound, percentages
	foreach my $t ( @{$tos{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${t}_out_".$reportType).$color{$r}{$t}.':'.&cleanProtocolLabel($t);
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${t}_out_".$reportType).$color{$r}{$t}.':'.&cleanProtocolLabel($t);
	    }
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${t}_out_pct").':AVERAGE:%.1lf%% Out';
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${t}_in_pct").':AVERAGE:%.1lf%% In\n';
	}
	
	# network outbound, percentages
	foreach my $n ( @{$network{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${n}_out_".$reportType).$color{$r}{$n}.':'.&cleanProtocolLabel($n);
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${n}_out_".$reportType).$color{$r}{$n}.':'.&cleanProtocolLabel($n);
	    }
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${n}_out_pct").':AVERAGE:%.1lf%% Out';
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${n}_in_pct").':AVERAGE:%.1lf%% In\n';
	}

	# AS outbound, percentages
	foreach my $n ( @{$as{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${n}_out_".$reportType).$color{$r}{$n}.':'.&cleanProtocolLabel($n);
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${n}_out_".$reportType).$color{$r}{$n}.':'.&cleanProtocolLabel($n);
	    }
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${n}_out_pct").':AVERAGE:%.1lf%% Out';
	    push @args, 'GPRINT:'.&cleanDEF("${r}_${n}_in_pct").':AVERAGE:%.1lf%% In\n';
	}

	# service other percentages
	if( scalar @{$service{$r}} ) {
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_service_out_pct").':AVERAGE:'.&cleanOtherLabel('Other services','%.1lf%% Out');
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_service_in_pct").':AVERAGE:%.1lf%% In\n';
	}
	# protocol other percentages
	if( scalar @{$protocol{$r}} ) {
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_protocol_out_pct").':AVERAGE:'.&cleanOtherLabel('Other protocols','%.1lf%% Out');
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_protocol_in_pct").':AVERAGE:%.1lf%% In\n';
	}
	# tos other percentages
	if( scalar @{$tos{$r}} ) {
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_tos_out_pct").':AVERAGE:'.&cleanOtherLabel('Other TOS','%.1lf%% Out');
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_tos_in_pct").':AVERAGE:%.1lf%% In\n';
	}
	# network other percentages
	if( scalar @{$network{$r}} ) {
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_network_out_pct").':AVERAGE:'.&cleanOtherLabel('Other networks','%.1lf%% Out');
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_network_in_pct").':AVERAGE:%.1lf%% In\n';
	}
	# AS other percentages
	if( scalar @{$as{$r}} ) {
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_as_out_pct").':AVERAGE:'.&cleanOtherLabel('Other ASes','%.1lf%% Out');
	    push @args, 'GPRINT:'.&cleanDEF("${r}_other_as_in_pct").':AVERAGE:%.1lf%% In\n';
	}
	# total outbound
	if( exists $total{$r} ) {
	    push @args, 'LINE1:'.&cleanDEF("${r}_total_out_".$reportType).$color{$r}{'total'}.':TOTAL';
	}
	
	$count = 0;

	# service inbound
	foreach my $s ( @{$service{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${s}_src_in_".$reportType.'_neg').$color{$r}{$s}{'src'};
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${s}_src_in_".$reportType.'_neg').$color{$r}{$s}{'src'};
	    }
	    push @args, 'STACK:'.&cleanDEF("${r}_${s}_dst_in_".$reportType.'_neg').$color{$r}{$s}{'dst'};
	}

	# protocol inbound
	foreach my $p ( @{$protocol{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${p}_in_".$reportType.'_neg').$color{$r}{$p};
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${p}_in_".$reportType.'_neg').$color{$r}{$p};
	    }
	}

	# TOS inbound
	foreach my $t ( @{$tos{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${t}_in_".$reportType.'_neg').$color{$r}{$t};
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${t}_in_".$reportType.'_neg').$color{$r}{$t};
	    }
	}

	# network inbound
	foreach my $n ( @{$network{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${n}_in_".$reportType.'_neg').$color{$r}{$n};
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${n}_in_".$reportType.'_neg').$color{$r}{$n};
	    }
	}

	# AS inbound
	foreach my $n ( @{$as{$r}} ) {
	    $count++;
	    if( $count == 1 ) {
		push @args, 'AREA:'.&cleanDEF("${r}_${n}_in_".$reportType.'_neg').$color{$r}{$n};
	    } else {
		push @args, 'STACK:'.&cleanDEF("${r}_${n}_in_".$reportType.'_neg').$color{$r}{$n};
	    }
	}

	# total inbound
	if( exists $total{$r} ) {
	    push @args, 'LINE1:'.&cleanDEF("${r}_total_in_".$reportType.'_neg').$color{$r}{'total'};
	}

	# blank line after router
	if( scalar @{$service{$r}} || scalar @{$protocol{$r}} || scalar @{$tos{$r}} ||
	    exists $total{$r} ) {
	    push @args, 'COMMENT:\n';
	}
    }

    push @args, 'HRULE:0#000000';
	
    return @args;
}
