#!/usr/bin/python

import os
import os.path
import subprocess
import openstack_conf
import openstack_pass
import osutils

osutils.beroot()

osutils.run_std('./ntp.py')

osutils.run_std('./network.py')

osutils.run_std('./nova.py')

osutils.run_std('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done')

print(osutils.run('nova-manage service list'))

print("Open horizon on http://" + openstack_conf.pubaddr)
print("username = admin")
print("password = " + openstack_pass.openstack_pass)

