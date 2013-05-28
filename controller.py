#!/usr/bin/python

import os
import os.path
import subprocess
import openstack_conf
import osutils

osutils.beroot()

if not os.path.exists('openstack_pass.py'):
  exit('error: run ./genpass.py to generate passwords')

osutils.run_std('./ntp.py')

osutils.run_std('./network.py')

osutils.run_std('./mysql.py')

osutils.run_std('./rabbit.py')

osutils.run_std('./keystone.py')

osutils.run_std('./glance.py')

osutils.run_std('./nova.py')

osutils.run_std('./cinder.py')

osutils.run_std('./quantum.py')

osutils.run_std('./swift.py')

osutils.run_std('apt-get install -y dnsmasq')

if os.system('nova-manage network list') != 0:
  print('info: exception is ok')
  print('info: network create %s on %s' % (openstack_conf.fixedrange, openstack_conf.flatint) )
  osutils.run_std('nova-manage network create private --fixed_range_v4=%s --num_networks=1 --bridge=br100 --bridge_interface=%s --network_size=250 --multi_host=T' % (openstack_conf.fixedrange, openstack_conf.flatint) )

floatingOut = osutils.run('nova-manage floating list')

if floatingOut.find('No floating') >= 0:
  print("info: floating create " + openstack_conf.floating)
  osutils.run_std('nova-manage floating create --ip_range=%s' % (openstack_conf.floating) )

osutils.run_std('nova keypair-add ssh_key > ssh_key.pem')

osutils.run_std('chmod 0600 ssh_key.pem')

# Create Default Security Policy. Opening TCP 22 and ICMP from the script.
osutils.run_std('nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0')

osutils.run_std('nova secgroup-add-rule default tcp 22 22 0.0.0.0/0')

osutils.run_std('./horizon.py')

osutils.run_std('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done')

osutils.run_std('nova-manage service list')

print("Open horizon on http://" + openstack_conf.pubaddr)
print("username = admin")
print("password = " + openstack_conf.openstack_pass)
