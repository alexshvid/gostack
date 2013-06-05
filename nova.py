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

if openstack_conf.version == 'grizzly':
  packages = packages + ' nova-conductor'

if openstack_conf.hyperv == 'qemu':
  print "info: setup qemu"
  packages = packages + ' nova-compute-qemu qemu'
elif openstack_conf.hyperv == 'kvm':
  print "info: setup kvm"
  packages = packages + ' nova-compute-kvm kvm'
else:
  print('error: unknown hypervisor ' + openstack_conf.hyperv)

# Install Nova
osutils.run_std('apt-get install -y ' + packages)

if openstack_conf.hyperv == 'qemu':
  osutils.run_std('apt-get -y purge dmidecode')

# Install VNC
osutils.run_std('apt-get install -y nova-vncproxy')

# Install NOVNC
osutils.run_std('apt-get install -y novnc nova-novncproxy')

# Install LibVirt
osutils.run_std('apt-get install -y libvirt-bin pm-utils')

# Install iSCSI
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

patcher.template_file('nova.conf.' + openstack_conf.version, '/etc/nova/nova.conf')
print('info: /etc/nova/nova.conf saved')

if not os.path.exists('/etc/nova/nova-compute.conf.bak'):
  shutil.copy2('/etc/nova/nova-compute.conf', '/etc/nova/nova-compute.conf.bak')

patcher.template_file('nova-compute.conf.' + openstack_conf.version, '/etc/nova/nova-compute.conf')
print('info: /etc/nova/nova-compute.conf saved')

# Setup Networks
if openstack_conf.version == 'grizzly':
  if openstack_conf.useQuantum:

    props = {}
    props['network_api_class'] = (None, 'nova.network.quantumv2.api.API')
    props['quantum_url'] = (None, 'http://'+openstack_pass.pubhost+':9696')
    props['quantum_auth_strategy'] = (None, 'keystone')
    props['quantum_admin_tenant_name'] = (None, 'service')
    props['quantum_admin_username'] = (None, 'quantum')
    props['quantum_admin_password'] = (None, openstack_pass.openstack_pass)
    props['quantum_admin_auth_url'] = (None, 'http://'+openstack_pass.pubhost+':35357/v2.0')
    props['libvirt_vif_driver'] = (None, 'nova.virt.libvirt.vif.LibvirtHybridOVSBridgeDriver')
    props['linuxnet_interface_driver'] = (None, 'nova.network.linux_net.LinuxOVSInterfaceDriver')
    props['firewall_driver'] = (None, 'nova.virt.libvirt.firewall.IptablesFirewallDriver')
    props['service_quantum_metadata_proxy'] = (None, True)
    props['quantum_metadata_proxy_shared_secret'] = (None, openstack_pass.quantum_metadata_proxy_shared_secret)

    p = patcher.patch_file('/etc/nova/nova.conf', props, True)
    print('info: /etc/nova/nova.conf patched for quantum ' + str(p))

  else:

    props = {}
    props['network_manager'] = (None, 'nova.network.manager.FlatDHCPManager')
    props['force_dhcp_release'] = (None, True)
    props['dhcpbridge'] = (None, '/usr/bin/nova-dhcpbridge')
    props['dhcpbridge_flagfile'] = (None, '/etc/nova/nova.conf')
    props['firewall_driver'] = (None, 'nova.virt.libvirt.firewall.IptablesFirewallDriver')
    props['my_ip'] = (None, openstack_conf.my_ip)
    props['public_interface'] = (None, openstack_conf.pubint)
    #props['vlan_interface'] = (None, openstack_conf.pubint)
    props['flat_interface'] = (None, openstack_conf.flatint)
    props['flat_network_bridge'] = (None, 'br100')
    props['floating_range'] = (None, openstack_conf.floating_range)
    props['flat_network_dhcp_start'] = (None, openstack_conf.flat_dhcpstart)
    props['flat_injected'] = (None, False)
    props['connection_type'] = (None, 'libvirt')

    p = patcher.patch_file('/etc/nova/nova.conf', props, True)
    print('info: /etc/nova/nova.conf patched for nova-network ' + str(p))


# Patch sudoers file
sudoers = patcher.read_text_file('/etc/sudoers')
novaAll = 'nova ALL=(ALL) NOPASSWD:ALL'
if not novaAll in sudoers:
  with open('/etc/sudoers', 'w') as f:
    f.write(sudoers + '\n' + novaAll + '\n')
  print('info: file /etc/sudoers patched True')

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


