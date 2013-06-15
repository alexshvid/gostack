#!/usr/bin/python

import os
import os.path
import subprocess
import openstack_conf
import openstack_pass
import osutils

osutils.beroot()

if openstack_conf.aptupdate:
  osutils.run_std('./aptupdate.py')

osutils.run_std('./interfaces.py')

osutils.run_std('./ntp.py')

if openstack_conf.my_ip == openstack_conf.controller_ip:
  osutils.run_std('./mysql.py')
  osutils.run_std('./rabbit.py')
  osutils.run_std('./keystone.py')
  osutils.run_std('./glance.py')

osutils.run_std('./nova.py')

if openstack_conf.my_ip == openstack_conf.controller_ip:
  osutils.run_std('apt-get install -y dnsmasq')
  osutils.run_std('./cinder.py')
  osutils.run_std('./network.py')
  osutils.run_std('./quantum.py')

osutils.run_std('./swift.py')

if openstack_conf.my_ip == openstack_conf.controller_ip:
  osutils.run_std('nova keypair-add ssh_key > ssh_key.pem')
  osutils.run_std('chmod 0600 ssh_key.pem')

  # Create Default Security Policy. Opening TCP 22 and ICMP from the script.
  osutils.run_std('nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0')
  osutils.run_std('nova secgroup-add-rule default tcp 22 22 0.0.0.0/0')


if openstack_conf.my_ip == openstack_conf.controller_ip:
  osutils.run_std('./horizon.py')

osutils.run_std('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done')

osutils.run_std('nova-manage network list')

osutils.run_std('nova-manage service list')

if openstack_conf.version == 'essex':
  print("Open horizon on http://%s" % (openstack_conf.controller_ip) )
else:
  print("Open horizon on http://%s/horizon" % (openstack_conf.controller_ip) )

print("username = admin")
print("password = " + openstack_pass.openstack_pass)

