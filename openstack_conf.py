#!/usr/bin/python

#version="essex"      # now supports only essex on Ubuntu 12.4
#version="folsom"
version="grizzly"

myproject="myproject"
myemail="my@email.com"
mydomain='mydomain.com'

pubaddr='192.168.100.77'
dhcpstart='192.168.100.129'
dhcpend='192.168.100.254'
floating='192.168.100.128/25'

#hyperv='kvm'
hyperv='qemu'

pubint='eth0'
flatint='eth1'

fixedrange='10.10.10.0/23'
prvnetmask='255.255.255.0'
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

if version == 'grizzly':
  useQuantum=True
