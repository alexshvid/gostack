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
osutils.run_std("mysql -u root -p%s -e 'CREATE DATABASE nova;'" % (openstack_pass.root_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON nova.* TO 'nova'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, '%', openstack_pass.nova_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON nova.* TO 'nova'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, 'localhost', openstack_pass.nova_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON nova.* TO 'nova'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, openstack_pass.pubhost, openstack_pass.nova_db_pass) )

packages = 'nova-api nova-cert nova-common nova-compute nova-doc python-nova python-novaclient nova-consoleauth nova-scheduler nova-network'

if openstack_conf.hyperv == 'qemu':
  print "info: setup qemu"
  packages = packages + ' nova-compute-qemu qemu'
elif openstack_conf.hyperv == 'kvm':
  print "info: setup kvm"
  packages = packages + ' nova-compute-kvm kvm pm-utils'
else:
  print('error: unknown hypervisor ' + openstack_conf.hyperv)

# Install Nova
osutils.run_std('apt-get install -y ' + packages)

if openstack_conf.hyperv == 'qemu':
  osutils.run_std('apt-get -y purge dmidecode')

# Install VNC
osutils.run_std('apt-get install -y nova-vncproxy')

# Install NOVNC
osutils.run_std('apt-get install -y novnc')


# Install LibVirt
osutils.run_std('apt-get install -y libvirt-bin')
osutils.run_std('apt-get install -y tgt open-iscsi open-iscsi-utils')


# Patch confs

props = {}
props['auth_host'] = ('127.0.0.1', openstack_pass.pubhost)
props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
props['admin_user'] = ('%SERVICE_USER%', 'admin')
props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)
p = patcher.patch_file('/etc/nova/api-paste.ini', props, True)
print('info: /etc/nova/api-paste.ini patched ' + str(p))

# Templates confs

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


if openstack_conf.version in ['folsom', 'grizzly']:

  acl = '[ "/dev/null", "/dev/full", "/dev/zero", "/dev/random", "/dev/urandom", "/dev/ptmx", "/dev/kvm", "/dev/kqemu", "/dev/rtc", "/dev/hpet", "/dev/net/tun" ]'
  props = {}
  props['cgroup_device_acl'] = (None, acl)
  p = patcher.patch_file('/etc/libvirt/qemu.conf', props, True)
  print('info: /etc/libvirt/qemu.conf patched ' + str(p))

  # Delete the default virtual bridge
  osutils.run_std('virsh net-destroy default')
  osutils.run_std('virsh net-undefine default')

  # Setup live migration
  props = {}
  props['listen_tls'] = (None, 0)
  props['listen_tcp'] = (None, 1)
  props['auth_tcp'] = (None, '"none"')
  p = patcher.patch_file('/etc/libvirt/libvirtd.conf', props, True)
  print('info: /etc/libvirt/libvirtd.conf patched ' + str(p))

  libvirt_bin_conf = patcher.read_text_file('/etc/init/libvirt-bin.conf')
  libvirt_bin_conf_new = libvirt_bin_conf.replace('env libvirtd_opts="-d"', 'env libvirtd_opts="-d -l"')
  if libvirt_bin_conf_new != libvirt_bin_conf:
    with open('/etc/init/libvirt-bin.conf', 'w') as f:
      f.write(libvirt_bin_conf_new)
    print('info: /etc/init/libvirt-bin.conf patched True');

  libvirt_bin = patcher.read_text_file('/etc/default/libvirt-bin')
  libvirt_bin_new = libvirt_bin.replace('libvirtd_opts="-d"', 'libvirtd_opts="-d -l"')
  if libvirt_bin_new != libvirt_bin:
    with open('/etc/default/libvirt-bin', 'w') as f:
      f.write(libvirt_bin_new)
    print('info: /etc/default/libvirt-bin patched True');

  osutils.run_std('service libvirt-bin restart')


# DB Sync
osutils.run_std('nova-manage db sync')

# Restart services
osutils.run_std('cd /etc/init.d/; for i in $( ls nova-* ); do sudo service $i restart; done')


