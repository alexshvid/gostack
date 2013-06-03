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
props['admin_tenant_name'] = (None, 'admin')
props['admin_user'] = (None, 'admin')
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
props['[keystone_authtoken]admin_tenant_name'] = (None, 'admin')
props['[keystone_authtoken]admin_user'] = (None, 'admin')
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

def quantum_id(out):
  tbl = keystone_utils.table(out)
  return keystone_utils.get(tbl, 'Value', keystone_utils.row(tbl, 'Field', 'id'))

def quantum_net_create(tenantId, netName):
  tbl = keystone_utils.table( osutils.run('quantum net-list') )
  r = keystone_utils.row(tbl, 'name', netName)
  if r != None:
    return keystone_utils.get(tbl, 'id', r)
  return quantum_id( osutils.run('quantum net-create --tenant-id %s %s' % (tenantId, netName)) )

def quantum_subnet_create(tenantId, netName, cidr):
  tbl = keystone_utils.table (osutils.run('quantum subnet-list') )
  r = keystone_utils.row(tbl, 'cidr', cidr)
  if r != None:
    return keystone_utils.get(tbl, 'id', r)
  return quantum_id( osutils.run('quantum subnet-create --tenant-id %s %s %s' % (tenantId, netName, cidr)) )

def quantum_router_create(tenantId, routerName):
  tbl = keystone_utils.table (osutils.run('quantum router-list') )
  r = keystone_utils.row(tbl, 'name', routerName)
  if r != None:
    return keystone_utils.get(tbl, 'id', r)
  return quantum_id( osutils.run('quantum router-create --tenant-id %s %s' % (tenantId, routerName) ))

def quantum_agent_find(agentName):
  tbl = keystone_utils.table (osutils.run('quantum agent-list') )
  print(tbl)
  r = keystone_utils.row(tbl, 'agent_type', agentName)
  if r != None:
    return keystone_utils.get(tbl, 'id', r)
  return None

# Add networks for Tenants
adminTenantId = keystone_utils.tenant_find('admin')
if adminTenantId != None:

  print('info: setup network for admin tenant')

  netId = quantum_net_create(adminTenantId, 'net_admin')
  print("admin netId = %s" % (netId))
  subNetId = quantum_subnet_create(adminTenantId, 'net_admin', openstack_conf.quantumAdminSubNet)
  print("admin subNetId = %s" % (subNetId))
  routerId = quantum_router_create(adminTenantId, 'router_admin')
  print("admin routerId = %s" % (routerId))

  # Add the router to the subnet
  osutils.run_std('quantum router-interface-add %s %s' % (routerId, subNetId))

projectTenantId = keystone_utils.tenant_find(openstack_conf.myproject)
if projectTenantId != None:
  print('info: setup network for %s tenant' % (openstack_conf.myproject))

  netName = 'net_' + openstack_conf.myproject
  routerName = 'router_' + openstack_conf.myproject

  netId = quantum_net_create(projectTenantId, netName)
  print("project netId = %s" % (netId))
  subNetId = quantum_subnet_create(projectTenantId, netName, openstack_conf.quantumProjectSubNet)
  print("project subNetId = %s" % (subNetId))
  routerId = quantum_router_create(projectTenantId, routerName)
  print("project routerId = %s" % (routerId))

  # Add the router to the subnet
  osutils.run_std('quantum router-interface-add %s %s' % (routerId, subNetId))


# Add Routers to L3 Agent
l3AgentId = quantum_agent_find('L3 agent')
print("l3AgentId = %s" % (l3AgentId))
if l3AgentId != None:
  osutils.run_std('quantum l3-agent-router-add %s router_admin' % (l3AgentId))
  osutils.run_std('quantum l3-agent-router-add %s router_%s' % (l3AgentId, openstack_conf.myproject))
else:
  print('error: L3 Agent not found')


# Restart Quantum
osutils.run_std('cd /etc/init.d/; for i in $( ls quantum-* ); do sudo service $i restart; done')



