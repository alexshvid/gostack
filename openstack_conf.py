#!/usr/bin/python

#version="essex"      # now supports only essex on Ubuntu 12.4
version="folsom"
#version="grizzly"

myproject="myproject"
myemail="my@email.com"
mydomain='mydomain.com'

pubaddr='192.168.100.77'
dhcpstart='192.168.100.128'
floating='192.168.100.128/25'

#hyperv='kvm'
hyperv='qemu'

pubint='eth0'
flatint='eth1'

fixedrange='10.10.10.0/23'
prvaddr='10.10.10.77'
prvnetmask='255.255.255.0'
iscsiprefix='10.10.10'

verbose=True
debug=True

useQuantum=False

