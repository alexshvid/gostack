#!/usr/bin/python

# GoStack installation properties
apt_update=False
add_sudoers=True
cinder_vgcreate=True
glance_download_image=True

#version="essex"
#version="folsom"
version="grizzly"

#hyperv='kvm'
hyperv='qemu'

myproject="myproject"
myemail="my@email.com"
mydomain='mydomain.com'

# Management network, different from floating for quantum
controller_ip='192.168.100.77'
my_ip='192.168.100.77'

# External Network
floating_int='eth0'
floating_range='192.168.100.128/25'

# Internal Network
fixed_int='eth1'
fixed_dhcpstart='10.10.10.2'
fixed_range='10.10.10.0/23'
iscsi_prefix='10.10.10'

verbose=True
debug=False

use_quantum=False
floating_range_start='192.168.100.129'
floating_range_end='192.168.100.254'
floating_range_gw='192.168.100.1'
use_namespaces=True

if use_quantum and version != 'grizzly':
  exit("wrong configuration")
  
