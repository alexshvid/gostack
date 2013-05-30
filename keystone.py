#!/usr/bin/python

import re
import subprocess
import openstack_conf
import openstack_pass
import patcher
import osutils
import keystone_utils

osutils.beroot()

osutils.run_std("mysql -u root -p%s -e 'CREATE DATABASE keystone;'" % (openstack_pass.root_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON keystone.* TO 'keystone'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, '%', openstack_pass.keystone_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON keystone.* TO 'keystone'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, 'localhost', openstack_pass.keystone_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON keystone.* TO 'keystone'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, openstack_pass.pubhost, openstack_pass.keystone_db_pass) )

osutils.run_std('apt-get install -y keystone python-keystone python-keystoneclient')

props = {}
props['[DEFAULT]bind_host'] = (None, '0.0.0.0')
props['[DEFAULT]admin_token'] = ('ADMIN', openstack_pass.admin_token)

props['[DEFAULT]verbose'] = (None, str(openstack_conf.verbose))
props['[DEFAULT]debug'] = (None, str(openstack_conf.debug))

props['[DEFAULT]public_port'] = (None, '5000')
props['[DEFAULT]admin_port'] = (None, '35357')
props['[DEFAULT]compute_port'] = (None, '8774')

sql = "mysql://keystone:%s@%s:3306/keystone" % (openstack_pass.keystone_db_pass, openstack_pass.pubhost)
print("sql = " + sql)

props['[sql]connection'] = ('sqlite:////var/lib/keystone/keystone.db', sql)
props['[sql]idle_timeout'] = (None, '200')

if openstack_conf.version in ["folsom", "grizzly"]:
  #props['[identity]driver'] = (None, 'keystone.identity.backends.sql.Identity')
  pass
else:
  props['[catalog]driver'] = ('keystone.catalog.backends.sql.Catalog', 'keystone.catalog.backends.templated.TemplatedCatalog')
  props['[catalog]template_file'] = (None, '/etc/keystone/default_catalog.templates')

p = patcher.patch_file('/etc/keystone/keystone.conf', props, True)
print("info: /etc/keystone/keystone.conf patched " + str(p))


# Restart keystone
osutils.run_std('service keystone restart')

# Sync keystone with MySQL
osutils.run_std('keystone-manage db_sync')

# Tenants
adminTenantId   = keystone_utils.tenant_create('admin')
serviceTenantId = keystone_utils.tenant_create('service')
projectTenantId = keystone_utils.tenant_create(openstack_conf.myproject)

print("adminTenantId = " + adminTenantId)
print("serviceTenantId = " + serviceTenantId)
print("projectTenantId = " + projectTenantId)

# Users
adminUserId   = keystone_utils.user_create('admin', openstack_pass.openstack_pass, openstack_conf.myemail)
projectUserId = keystone_utils.user_create(openstack_conf.myproject, openstack_pass.openstack_pass, openstack_conf.myemail)

print("adminUserId = " + adminUserId)
print("projectUserId = " + projectUserId)

# Roles
adminRoleId           = keystone_utils.role_create('admin')
keystoneAdminRoleId   = keystone_utils.role_create('KeystoneAdmin')
keystoneServiceRoleId = keystone_utils.role_create('KeystoneServiceAdmin')
memberRoleId          = keystone_utils.role_create('Member')

print("adminRoleId = " + adminRoleId)
print("keystoneAdminRoleId = " + keystoneAdminRoleId)
print("keystoneServiceRoleId = " + keystoneServiceRoleId)
print("memberRoleId = " + memberRoleId)

keystone_utils.user_role_add(adminUserId, adminRoleId, adminTenantId)
keystone_utils.user_role_add(adminUserId, keystoneAdminRoleId, adminTenantId)
keystone_utils.user_role_add(adminUserId, keystoneServiceRoleId, adminTenantId)
keystone_utils.user_role_add(adminUserId, adminRoleId, projectTenantId)
keystone_utils.user_role_add(projectUserId, memberRoleId, projectTenantId)

# Configure service users/roles
novaUserId    = keystone_utils.user_create('nova',    openstack_pass.openstack_pass, 'nova@'   + openstack_conf.mydomain, serviceTenantId)
glanceUserId  = keystone_utils.user_create('glance',   openstack_pass.openstack_pass, 'glance@' + openstack_conf.mydomain, serviceTenantId)
cinderUserId  = keystone_utils.user_create('cinder',   openstack_pass.openstack_pass, 'cinder@'  + openstack_conf.mydomain, serviceTenantId)
swiftUserId   = keystone_utils.user_create('swift',    openstack_pass.openstack_pass, 'swift@'    + openstack_conf.mydomain, serviceTenantId)
if openstack_conf.useQuantum:
  quantumUserId = keystone_utils.user_create('quantum', openstack_pass.openstack_pass, 'quantum@' + openstack_conf.mydomain, serviceTenantId)

keystone_utils.user_role_add(novaUserId,    adminRoleId, serviceTenantId)
keystone_utils.user_role_add(glanceUserId,  adminRoleId, serviceTenantId)
keystone_utils.user_role_add(cinderUserId,  adminRoleId, serviceTenantId)
keystone_utils.user_role_add(swiftUserId,   adminRoleId, serviceTenantId)
if openstack_conf.useQuantum:
  keystone_utils.user_role_add(quantumUserId, adminRoleId, serviceTenantId)

if openstack_conf.version in ["folsom", "grizzly"]:
  resellerRoleId = keystone_utils.role_create('ResellerAdmin')
  keystone_utils.user_role_add(novaUserId, resellerRoleId, serviceTenantId)

# Create EndPoints
novaEndpointId = keystone_utils.service_create('nova', 'compute', 'OpenStack Compute Service')
url = "http://%s:8774/v2/$(tenant_id)s" % (openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', novaEndpointId, url, url, url)

cinderEndpointId = keystone_utils.service_create('cinder', 'volume', 'OpenStack Volume Service')
url = "http://%s:8776/v1/$(tenant_id)s" % (openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', cinderEndpointId, url, url, url)

glanceEndpointId = keystone_utils.service_create('glance', 'image', 'OpenStack Image Service')
url = "http://%s:9292/v2" % (openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', glanceEndpointId, url, url, url)

swiftEndpointId = keystone_utils.service_create('swift', 'object-store', 'OpenStack Storage Service')
url = "http://%s:8080/v1/AUTH_%s" % (openstack_pass.pubhost, '%(tenant_id)s')
adminurl = "http://%s:8080/v1" % (openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', swiftEndpointId, url, adminurl, url)

keystoneEndpointId = keystone_utils.service_create('keystone', 'identity', 'OpenStack Identity Service')
url = "http://%s:5000/v2.0" % (openstack_pass.pubhost)
adminurl = "http://%s:35357/v2.0" % (openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', keystoneEndpointId, url, adminurl, url)

ec2EndpointId = keystone_utils.service_create('ec2', 'ec2', 'OpenStack EC2 Service')
url = "http://%s:8773/services/Cloud" % (openstack_pass.pubhost)
adminurl = "http://%s:8773/services/Admin" % (openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', ec2EndpointId, url, adminurl, url)

if openstack_conf.useQuantum:
  quantumEndpointId = keystone_utils.service_create('quantum', 'network', 'OpenStack Networking Service')
  url = "http://%s:9696/" % (openstack_pass.pubhost)
  keystone_utils.endpoint_create('RegionOne', quantumEndpointId, url, url, url)



