#!/usr/bin/python

import os
import os.path
import subprocess
import openstack_conf

if os.geteuid() != 0:
  exit("Login as a root")

if not os.path.exists('openstack_pass.py'):
  exit('error: run ./genpass.py firstly')

installer = subprocess.Popen('./ntp.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./network.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./nova.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()


restarter = subprocess.Popen('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()

os.system('nova-manage service list')

print("Open horizon on http://" + openstack_conf.pubaddr)
print("username = admin")
print("password = " + openstack_conf.openstack_pass)

