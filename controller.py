#!/usr/bin/python

import os
import os.path
import subprocess
import openstack_conf

if os.geteuid() != 0:
  exit("Login as a root")

if not os.path.exists('openstack_pass.py'):
  exit('error: run ./genpass.py to generate passwords')

installer = subprocess.Popen('./ntp.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./mysql.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./rabbit.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./network.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./keystone.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./glance.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./nova.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('./volume.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('apt-get install -y nova-objectstore nova-scheduler', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('apt-get install -y dnsmasq', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

if os.system('nova-manage network list') != 0:
  print("info: exception is ok")
  print("info: network create " + openstack_conf.fixedrange + " on " + openstack_conf.flatint)
  runner = subprocess.Popen('nova-manage network create private --fixed_range_v4='+openstack_conf.fixedrange+' --num_networks=1 --bridge=br100 --bridge_interface='+openstack_conf.flatint+' --network_size=250 --multi_host=T', shell=True, stdin=None, executable="/bin/bash")
  runner.wait()

floatingList = subprocess.Popen('nova-manage floating list', shell=True, stdin=None, stdout=subprocess.PIPE, executable="/bin/bash")
floatingList.wait()
list, err = floatingList.communicate()

if list.find('No floating') >= 0:
  print("info: floating create " + openstack_conf.floating)
  runner = subprocess.Popen('nova-manage floating create --ip_range='+openstack_conf.floating, shell=True, stdin=None, executable="/bin/bash")
  runner.wait()

runner = subprocess.Popen('nova keypair-add ssh_key > ssh_key.pem', shell=True, stdin=None, executable="/bin/bash")
runner.wait()

runner = subprocess.Popen('chmod 0600 ssh_key.pem', shell=True, stdin=None, executable="/bin/bash")
runner.wait()

#Create Default Security Policy. Opening TCP 22 and ICMP from the script.
runner = subprocess.Popen('nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0', shell=True, stdin=None, executable="/bin/bash")
runner.wait()

runner = subprocess.Popen('nova secgroup-add-rule default tcp 22 22 0.0.0.0/0', shell=True, stdin=None, executable="/bin/bash")
runner.wait()

installer = subprocess.Popen('./horizon.py', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

os.system('./rabbit-change-pass.sh')

restarter = subprocess.Popen('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()

os.system('nova-manage service list')

print("Open horizon on http://" + openstack_conf.pubaddr)
print("username = admin")
print("password = " + openstack_conf.openstack_pass)
