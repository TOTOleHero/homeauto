#!/usr/bin/perl
################################################################################
#
# xPL Hub for Perl
#
# Version 1.1
#
# Copyright (C) 2003 John Bent
# http://www.xpl.myby.co.uk/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# Linking this library statically or dynamically with other modules is
# making a combined work based on this library. Thus, the terms and
# conditions of the GNU General Public License cover the whole
# combination.
# As a special exception, the copyright holders of this library give you
# permission to link this library with independent modules to produce an
# executable, regardless of the license terms of these independent
# modules, and to copy and distribute the resulting executable under
# terms of your choice, provided that you also meet, for each linked
# independent module, the terms and conditions of the license of that
# module. An independent module is a module which is not derived from
# or based on this library. If you modify this library, you may extend
# this exception to your version of the library, but you are not
# obligated to do so. If you do not wish to do so, delete this
# exception statement from your version.
#
################################################################################
use strict;
use warnings;

use IO::Socket;
use IO::Select;
use Sys::Hostname;

my (
  $foundport,
  $xpl_socket,
  $msg,
  $fromaddr,
  @localaddr
);

my %hubs = ();


sub broadcastMessage {
  my $ipaddr   = inet_aton('127.0.0.1');
  my $portaddr = sockaddr_in($_[1], $ipaddr);
  my $sockUDP = IO::Socket::INET->new(PeerPort => $_[1],
    Proto => 'udp'
  );
  if (!defined($sockUDP)) {
    print "Error sending xPL message to port $_[1].\n";
    return;
  }  
  $sockUDP->autoflush(1);
  $sockUDP->sockopt(SO_BROADCAST,1);
  $sockUDP->send($_[0],0,$portaddr);  
  close $sockUDP;
}

sub getparam {
# Retrieves a parameter from the body of an xPL message
	my $buff = $_[0];  
	$buff = substr($buff,index($buff,"}"),length($buff)-index($buff,"}"));
	$buff = substr($buff,index($buff,"{")+2,length($buff)-index($buff,"{")-2);
	$buff = substr($buff,0,index($buff,"}")-1);
	my %params = map { split /=/, $_, 2 } split /\n/, $buff ;
	return $params{$_[1]};
}

sub gethdrparam {
# Retrieves a parameter from the header of an xPL message
	my $buff = $_[0];  
	$buff = substr($buff,index($buff,"{")+2,length($buff)-index($buff,"{")-2);
	$buff = substr($buff,0,index($buff,"}")-1);
	my %params = map { split /=/, $_, 2 } split /\n/, $buff ;
	return $params{$_[1]};
}

sub getmsgtype {
# Returns the type of an xPL message, e.g. xpl-stat, xpl-trig or xpl-cmnd
	return lc substr($_[0],0,8);
}

sub getmsgschema {
# This routine accepts an xPL message and returns the message schema, in lowercase characters
	my $buff = $_[0];
	$buff = substr($buff,index($buff,"}")+2,length($buff)-index($buff,"}")-2);
	$buff = substr($buff,0,index($buff,"\n"));
	return lc $buff;
}

sub getlocalips {
  my $hostname = Sys::Hostname::hostname();
  my($name, $aliases, $addrtype, $length, @addrs) = gethostbyname($hostname);
  return @addrs;
}

sub isMessageLocal {
  foreach my $ip (@localaddr) {
    if ($ip eq $_[0]) {
      return 1;
    }
  }
  return 0;
}



$xpl_socket = IO::Socket::INET->new(
  Proto     => 'udp',
  LocalPort => 3865,
);	

die "The hub could not bind to port 3865. Make sure you are not already running an xPL hub.\n" unless $xpl_socket;

# Get all local IP addresses
@localaddr = getlocalips();

print "xPL Hub for Perl (version 1.0) ready.\n\n";

while (defined($xpl_socket)) {
  $fromaddr = recv($xpl_socket,$msg,1500,0);
  my($port, $ipaddr) = sockaddr_in($fromaddr);
  # Check for heartbeat/config message
  if (getmsgtype($msg) eq 'xpl-stat' && getmsgschema($msg) =~ "^(config\.(app|end))|(hbeat\.(app|end))") {
    # Is the message local?
    if (isMessageLocal($ipaddr)) {
      $port = getparam($msg,"port");
      # If we've not got it, then add it
      if (!defined($hubs{$port})) {
        $hubs{$port} = gethdrparam($msg,"source");
        print "xPL process $hubs{$port} detected on port $port.\n";
      }
      elsif (getmsgschema($msg) =~ "^(config\.end)|(hbeat\.end)") {
        # Device is shutting down, so remove it
        delete $hubs{$port};                
      }

    }
  }
  # Broadcast the message to all listening ports
  foreach my $hub (keys %hubs) {
    broadcastMessage($msg,$hub);
  }
}

close($xpl_socket);

1;
