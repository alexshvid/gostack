#!/usr/bin/python

import re
import subprocess
import openstack_conf
import openstack_pass
import patcher
import osutils
import keystone_utils

osutils.beroot()

osutils.run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE keystone;'""")
osutils.run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)
osutils.run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)
osutils.run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)

osutils.run_std('apt-get install -y keystone python-keystone python-keystoneclient')

props = {}
props['[DEFAULT]bind_host'] = (None, '0.0.0.0')
props['[DEFAULT]admin_token'] = ('ADMIN', openstack_pass.admin_token)

props['[DEFAULT]verbose'] = (None, str(openstack_conf.verbose))
props['[DEFAULT]debug'] = (None, str(openstack_conf.debug))

props['[DEFAULT]public_port'] = (None, '5000')
props['[DEFAULT]admin_port'] = (None, '35357')
props['[DEFAULT]compute_port'] = (None, '8774')

props['[sql]connection'] = ('sqlite:////var/lib/keystone/keystone.db', "mysql://keystone:"+openstack_pass.keystone_db_pass+"@"+openstack_pass.pubhost+":3306/keystone")
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
novaUserId    = keystone_utils.user_create('nova',    openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)
glanceUserId  = keystone_utils.user_create('glance',   openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)
swiftUserId   = keystone_utils.user_create('swift',    openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)
quantumUserId = keystone_utils.user_create('quantum', openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)

keystone_utils.user_role_add(novaUserId,    adminRoleId, serviceTenantId)
keystone_utils.user_role_add(glanceUserId,  adminRoleId, serviceTenantId)
keystone_utils.user_role_add(swiftUserId,   adminRoleId, serviceTenantId)
keystone_utils.user_role_add(quantumUserId, adminRoleId, serviceTenantId)

if openstack_conf.version in ["folsom", "grizzly"]:
  resellerRoleId = keystone_utils.role_create('ResellerAdmin')
  keystone_utils.user_role_add(novaUserId, resellerRoleId, serviceTenantId)

  cinderUserId = keystone_utils.user_create('cinder', openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)
  keystone_utils.user_role_add(cinderUserId, adminRoleId, serviceTenantId)


# Create EndPoints
novaEndpointId = keystone_utils.service_create('nova', 'compute', 'OpenStack Compute Service')
url = "http://{0}:8774/v2/{1}".format(openstack_pass.pubhost, serviceTenantId)
keystone_utils.endpoint_create('RegionOne', novaEndpointId, url, url, url)

cinderEndpointId = keystone_utils.service_create('cinder', 'volume', 'OpenStack Volume Service')
url = "http://{0}:8776/v1/{1}".format(openstack_pass.pubhost, serviceTenantId)
keystone_utils.endpoint_create('RegionOne', cinderEndpointId, url, url, url)

glanceEndpointId = keystone_utils.service_create('glance', 'image', 'OpenStack Image Service')
url = "http://{0}:9292/v2".format(openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', glanceEndpointId, url, url, url)

swiftEndpointId = keystone_utils.service_create('swift', 'object-store', 'OpenStack Storage Service')
url = "http://{0}:8080/v1/AUTH_{1}".format(openstack_pass.pubhost, serviceTenantId)
adminurl = "http://{0}:8080/v1".format(openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', swiftEndpointId, url, adminurl, url)

keystoneEndpointId = keystone_utils.service_create('keystone', 'identity', 'OpenStack Identity Service')
url = "http://{0}:5000/v2.0".format(openstack_pass.pubhost)
adminurl = "http://{0}:35357/v2.0".format(openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', keystoneEndpointId, url, adminurl, url)

ec2EndpointId = keystone_utils.service_create('ec2', 'ec2', 'OpenStack EC2 Service')
url = "http://{0}:8773/services/Cloud".format(openstack_pass.pubhost)
adminurl = "http://{0}:8773/services/Admin".format(openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', ec2EndpointId, url, adminurl, url)

quantumEndpointId = keystone_utils.service_create('quantum', 'network', 'OpenStack Networking Service')
url = "http://{0}:9696/".format(openstack_pass.pubhost)
keystone_utils.endpoint_create('RegionOne', quantumEndpointId, url, url, url)



