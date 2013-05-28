#!/usr/bin/python

import os
import os.path
import subprocess
import patcher
import openstack_conf
import openstack_pass
import shutil
import osutils

osutils.beroot()

# Create database for Nova
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE nova;'""")
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e "GRANT ALL ON nova.* TO 'nova'@'%' IDENTIFIED BY '"""+openstack_pass.nova_db_pass+"""';" """)
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e "GRANT ALL ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '"""+openstack_pass.nova_db_pass+"""';" """)
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e "GRANT ALL ON nova.* TO 'nova'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.nova_db_pass+"""';" """)

# Install Nova
osutils.run_std('apt-get install -y nova-api nova-cert nova-common nova-compute nova-doc python-nova python-novaclient nova-consoleauth nova-scheduler')

# Install VNC
osutils.run_std('apt-get install -y nova-vncproxy')

# Install NOVNC
osutils.run_std('apt-get install -y novnc')

props = {}
props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
props['admin_user'] = ('%SERVICE_USER%', 'admin')
props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)
p = patcher.patch_file('/etc/nova/api-paste.ini', props, True)
print('info: /etc/nova/api-paste.ini patched ' + str(p))

# Patch confs

if not os.path.exists('/etc/nova/nova.conf.bak'):
  shutil.copy2('/etc/nova/nova.conf', '/etc/nova/nova.conf.bak')

if openstack_conf.version == 'essex':
  template = 'essex'
else:
  template = 'folsom'

patcher.template_file('nova.conf.' + template, '/etc/nova/nova.conf')
print('info: /etc/nova/nova.conf saved')

if not os.path.exists('/etc/nova/nova-compute.conf.bak'):
  shutil.copy2('/etc/nova/nova-compute.conf', '/etc/nova/nova-compute.conf.bak')

patcher.template_file('nova-compute.conf.' + template, '/etc/nova/nova-compute.conf')
print('info: /etc/nova/nova-compute.conf saved')


# Install LibVirt

osutils.run_std('apt-get install -y libvirt-bin vlan bridge-utils')

osutils.run_std('apt-get install -y tgt open-iscsi open-iscsi-utils')

if openstack_conf.hyperv == 'qemu':
  print "info: setup qemu"
  osutils.run_std('apt-get -y install nova-compute-qemu qemu')
  osutils.run_std('apt-get -y purge dmidecode')

elif openstack_conf.hyperv == 'kvm':
  print "info: setup kvm"
  osutils.run_std('apt-get -y install nova-compute-kvm kvm pm-utils')
else:
  print('error: unknown hypervisor ' + openstack_conf.hyperv)


# DB Sync
osutils.run_std('nova-manage db sync')

# Restart services
osutils.run_std('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done')


