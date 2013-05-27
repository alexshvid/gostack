#!/usr/bin/python

import os
import os.path
import subprocess
import patcher
import openstack_conf
import openstack_pass
import shutil

if os.geteuid() != 0:
  exit("Login as a root")

# Create database for Nova
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE nova;'""")
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON nova.* TO 'nova'@'%' IDENTIFIED BY '"""+openstack_pass.nova_db_pass+"""';" """)
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '"""+openstack_pass.nova_db_pass+"""';" """)
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON nova.* TO 'nova'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.nova_db_pass+"""';" """)

installer = subprocess.Popen('apt-get install -y libvirt-bin vlan bridge-utils', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('apt-get install -y tgt open-iscsi open-iscsi-utils', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

# Install Nova
installer = subprocess.Popen('apt-get install -y nova-api nova-cert nova-consoleauth nova-common nova-compute nova-doc python-nova python-novaclient', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

# Install VNC
installer = subprocess.Popen('apt-get install -y nova-vncproxy', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

# Install NOVNC
installer = subprocess.Popen('apt-get install -y novnc', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

props = {}
props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
props['admin_user'] = ('%SERVICE_USER%', 'admin')
props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)
p = patcher.patch_file('/etc/nova/api-paste.ini', props, True)
print('info: /etc/nova/api-paste.ini patched ' + str(p))

if openstack_conf.hyperv == 'qemu':
  print "info: setup qemu"
  installer = subprocess.Popen('apt-get -y install nova-compute-qemu qemu', shell=True, stdin=None, executable="/bin/bash")
  installer.wait()
  installer = subprocess.Popen('apt-get -y purge dmidecode', shell=True, stdin=None, executable="/bin/bash")
  installer.wait()

elif openstack_conf.hyperv == 'kvm':
  print "info: setup kvm"
  installer = subprocess.Popen('apt-get -y install nova-compute-kvm kvm pm-utils', shell=True, stdin=None, executable="/bin/bash")
  installer.wait()
else:
  print('error: unknown hypervisor ' + openstack_conf.hyperv)


# Patch confs

if not os.path.exists('/etc/nova/nova.conf.bak'):
  shutil.copy2('/etc/nova/nova.conf', '/etc/nova/nova.conf.bak')

patcher.template_file('nova.conf.template', '/etc/nova/nova.conf')
print('info: /etc/nova/nova.conf saved')

if not os.path.exists('/etc/nova/nova-compute.conf.bak'):
  shutil.copy2('/etc/nova/nova-compute.conf', '/etc/nova/nova-compute.conf.bak')

patcher.template_file('nova-compute.conf.template', '/etc/nova/nova-compute.conf')
print('info: /etc/nova/nova-compute.conf saved')


dbSync = subprocess.Popen('nova-manage db sync', shell=True, stdin=None, executable="/bin/bash")
dbSync.wait()

# Restart services

restarter = subprocess.Popen('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()


