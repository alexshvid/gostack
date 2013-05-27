#!/usr/bin/python

import os
import re
import subprocess
import openstack_conf
import openstack_pass
import patcher

if os.geteuid() != 0:
  exit("Login as a root")

if not os.path.exists('openstack_pass.py'):
  exit('error: run ./genpass.py to generate passwords')

def run(cmd):
  p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, executable="/bin/bash")
  p.wait()
  out, err = p.communicate()
  if err != None:
    print('error: fail run command ' + cmd + ', error code = ' + str(err))
  return out

def run_std(cmd):
  p = subprocess.Popen(cmd, shell=True, stdin=None, executable="/bin/bash")
  p.wait()


def table(str):
  tbl = []
  for line in str.split('\n'):
    part = [p.strip() for p in line.split('|')]
    if len(part) > 2:
      tbl.append(part[1:-1])
  return tbl

def row(tbl, col, key):
  if len(tbl) > 0 and col in tbl[0]:
    c = tbl[0].index(col)
    for r in range(1, len(tbl)):
      if tbl[r][c] == key:
        return tbl[r]
  return None

def get(tbl, col, row):
  if col in tbl[0]:
    c = tbl[0].index(col)
    return row[c]
  return None

def keystone_id(out):
  tbl = table(out)
  return get(tbl, 'Value', row(tbl, 'Property', 'id'))


run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE keystone;'""")
run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)
run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)
run_std("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)

run_std('apt-get install -y keystone python-keystone python-keystoneclient')

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
run_std('service keystone restart')

# Sync keystone with MySQL
run_std('keystone-manage db_sync')

def tenant_create(name):
  tbl = table( run('keystone tenant-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    return keystone_id( run('keystone tenant-create --name=' + name) )

def user_create(name, pwd, email, tenantId=None):
  tbl = table( run('keystone user-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    cmd = 'keystone user-create --name=' + name + ' --pass=' + pwd + ' --email=' + email
    if tenantId != None:
      cmd = cmd + ' --tenant_id=' + tenantId
    return keystone_id( run(cmd) )

def role_create(name):
  tbl = table( run('keystone role-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    return keystone_id( run('keystone role-create --name=' + name ) )

def user_role_add(userId, roleId, tenantId):
  if openstack_conf.version == "essex":
    return run('keystone user-role-add --user=' + userId + ' --role=' + roleId + ' --tenant_id=' + tenantId )
  else:
    return run('keystone user-role-add --user-id=' + userId + ' --role-id=' + roleId + ' --tenant_id=' + tenantId )

# Tenants
adminTenantId   = tenant_create('admin')
serviceTenantId = tenant_create('service')
projectTenantId = tenant_create(openstack_conf.myproject)

print("adminTenantId = " + adminTenantId)
print("serviceTenantId = " + serviceTenantId)
print("projectTenantId = " + projectTenantId)

# Users
adminUserId   = user_create('admin', openstack_pass.openstack_pass, openstack_conf.myemail)
projectUserId = user_create(openstack_conf.myproject, openstack_pass.openstack_pass, openstack_conf.myemail)

print("adminUserId = " + adminUserId)
print("projectUserId = " + projectUserId)

# Roles
adminRoleId           = role_create('admin')
keystoneAdminRoleId   = role_create('KeystoneAdmin')
keystoneServiceRoleId = role_create('KeystoneServiceAdmin')
memberRoleId          = role_create('Member')

print("adminRoleId = " + adminRoleId)
print("keystoneAdminRoleId = " + keystoneAdminRoleId)
print("keystoneServiceRoleId = " + keystoneServiceRoleId)
print("memberRoleId = " + memberRoleId)

user_role_add(adminUserId, adminRoleId, adminTenantId)
user_role_add(adminUserId, keystoneAdminRoleId, adminTenantId)
user_role_add(adminUserId, keystoneServiceRoleId, adminTenantId)
user_role_add(adminUserId, adminRoleId, projectTenantId)
user_role_add(projectUserId, memberRoleId, projectTenantId)

# Configure service users/roles
novaUserId   = user_create('nova',    openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)
glanceUserId = user_create('glance',   openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)
quantumUserId = user_create('quantum', openstack_pass.openstack_pass, openstack_conf.myemail, serviceTenantId)

user_role_add(novaUserId, adminRoleId, serviceTenantId)
user_role_add(glanceUserId, adminRoleId, serviceTenantId)
user_role_add(quantumUserId, adminRoleId, serviceTenantId)



