#!/usr/bin/python

import os
import subprocess
import patcher
import openstack_conf
import openstack_pass
import osutils
import keystone_utils

osutils.beroot()

if not openstack_conf.useQuantum:
  exit("info: useQuantum False")

osutils.run_std('apt-get install -y openvswitch-switch openvswitch-datapath-dkms')

# br-int will be used for VM integration
osutils.run_std('ovs-vsctl add-br br-int')

# br-ex is used to make to access the internet (not covered in this guide)
osutils.run_std('ovs-vsctl add-br br-ex')

# Install the Quantum components:
osutils.run_std('apt-get install -y quantum-server quantum-plugin-openvswitch quantum-plugin-openvswitch-agent dnsmasq quantum-dhcp-agent quantum-l3-agent')

# Create database for Quantum
osutils.run_std("mysql -u root -p%s -e 'CREATE DATABASE quantum;'" % (openstack_pass.root_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON quantum.* TO 'quantum'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, '%', openstack_pass.quantum_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON quantum.* TO 'quantum'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, 'localhost', openstack_pass.quantum_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON quantum.* TO 'quantum'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, openstack_pass.pubhost, openstack_pass.quantum_db_pass) )

# Restart Quantum
osutils.run_std('cd /etc/init.d/; for i in $( ls quantum-* ); do sudo service $i status; done')


# Edit /etc/quantum/api-paste.ini
props = {}
props['[filter:authtoken]paste.filter_factory'] = (None, 'keystoneclient.middleware.auth_token:filter_factory')
props['[filter:authtoken]auth_host'] = (None, openstack_pass.pubhost)
props['[filter:authtoken]auth_port'] = (None, 35357)
props['[filter:authtoken]auth_protocol'] = (None, 'http')
props['[filter:authtoken]admin_tenant_name'] = (None, 'admin')
props['[filter:authtoken]admin_user'] = (None, 'admin')
props['[filter:authtoken]admin_password'] = (None, openstack_pass.openstack_pass)
p = patcher.patch_file('/etc/quantum/api-paste.ini', props, True)
print('info: /etc/quantum/api-paste.ini patched ' + str(p))

# SQL connection string
sql = "mysql://quantum:%s@%s:3306/quantum" % (openstack_pass.quantum_db_pass, openstack_pass.pubhost)

# Edit the OVS plugin configuration file
props = {}
props['[DATABASE]sql_connection'] = (None, sql)
props['[OVS]tenant_network_type'] = (None, 'gre')
props['[OVS]tunnel_id_ranges'] = (None, '1:1000')
props['[OVS]integration_bridge'] = (None, 'br-int')
props['[OVS]tunnel_bridge'] = (None, 'br-tun')
props['[OVS]local_ip'] = (None, openstack_conf.prvaddr)
props['[OVS]enable_tunneling'] = (None, True)
props['[SECURITYGROUP]firewall_driver'] = (None, 'quantum.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver')
p = patcher.patch_file('/etc/quantum/plugins/openvswitch/ovs_quantum_plugin.ini', props, True)
print('info: /etc/quantum/plugins/openvswitch/ovs_quantum_plugin.ini patched ' + str(p))

# Update /etc/quantum/metadata_agent.ini
props = {}
props['auth_url'] = (None, 'http://%s:35357/v2.0' % (openstack_pass.pubhost))
props['auth_region'] = (None, 'RegionOne')
props['admin_tenant_name'] = (None, 'service')
props['admin_user'] = (None, 'quantum')
props['admin_password'] = (None, openstack_pass.openstack_pass)
props['nova_metadata_ip'] = (None, openstack_conf.prvaddr)
props['nova_metadata_port'] = (None, 8775)
props['metadata_proxy_shared_secret'] = (None, 'helloOpenStack')
p = patcher.patch_file('/etc/quantum/metadata_agent.ini', props, True)
print('info: /etc/quantum/metadata_agent.ini patched ' + str(p))

# Edit your /etc/quantum/quantum.conf
props = {}
props['[DEFAULT]debug'] = (None, openstack_conf.debug)
props['[DEFAULT]verbose'] = (None, openstack_conf.verbose)
props['[keystone_authtoken]auth_host'] = (None, openstack_conf.prvaddr)
props['[keystone_authtoken]auth_port'] = (None, 35357)
props['[keystone_authtoken]auth_protocol'] = (None, 'http')
props['[keystone_authtoken]admin_tenant_name'] = (None, 'service')
props['[keystone_authtoken]admin_user'] = (None, 'quantum')
props['[keystone_authtoken]admin_password'] = (None, openstack_pass.openstack_pass)
props['[keystone_authtoken]auth_protocol'] = (None, 'http')
props['[keystone_authtoken]signing_dir'] = (None, '/var/lib/quantum/keystone-signing')

props['[DEFAULT]rabbit_host'] = (None, openstack_pass.pubhost)
props['[DEFAULT]rabbit_userid'] = (None, 'guest')
props['[DEFAULT]rabbit_password'] = ('guest', openstack_pass.rabbit_pass)

p = patcher.patch_file('/etc/quantum/quantum.conf', props, True)
print('info: /etc/quantum/quantum.conf patched ' + str(p))


# Restart Quantum
osutils.run_std('cd /etc/init.d/; for i in $( ls quantum-* ); do sudo service $i restart; done')
osutils.run_std('service dnsmasq restart')

# Add networks for Tenants
adminTenantId = keystone_utils.tenant_find('admin')
if adminTenantId != None:
  print('info: setup network for admin tenant')


projectTenantId = keystone_utils.tenant_find(openstack_conf.myproject)
if projectTenantId != None:
  print('info: setup network for %s tenant' % (openstack_conf.myproject))
