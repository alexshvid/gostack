#!/usr/bin/python

aptupdate=False
sudoers=True
vgcreate=True

#version="essex"      # now supports only essex on Ubuntu 12.4
#version="folsom"
version="grizzly"

#hyperv='kvm'
hyperv='qemu'

myproject="myproject"
myemail="my@email.com"
mydomain='mydomain.com'

pub_int='eth0'
pubaddr='192.168.100.77'
my_ip='192.168.100.77'
floating_range='192.168.100.128/25'

flat_int='eth1'
flat_dhcpstart='10.10.10.2'
fixed_range='10.10.10.0/23'
iscsiprefix='10.10.10'

verbose=True
debug=True

useQuantum=False
quantumProjectSubNet='100.100.100.0/24'
quantumIntInt='eth1'
quantumExtInt='eth3'
quantumFloating='192.168.56.0/24'
quantumFloatingStart='192.168.56.2'
quantumFloatingEnd='192.168.56.254'
quantumFloatingGateway='192.168.56.1'
use_namespaces=True

#if version == 'grizzly':
#  useQuantum=True
