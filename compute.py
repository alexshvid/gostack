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

osutils.run_std('./nova.py')

osutils.run_std('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done')

print(osutils.run('nova-manage service list'))

print("Open horizon on http://" + openstack_conf.pubaddr)
print("username = admin")
print("password = " + openstack_conf.openstack_pass)

