#!/usr/bin/python

import osutils
import openstack_conf

#
#  Keystone Ouput Parsers
#

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
  if len(tbl) > 0 and col in tbl[0]:
    c = tbl[0].index(col)
    return row[c]
  return None


#
#  Keystone get_id Parser
#

def keystone_id(out):
  tbl = table(out)
  return get(tbl, 'Value', row(tbl, 'Property', 'id'))


#
#  Keystone Factories
#

def tenant_create(name):
  tbl = table( osutils.run('keystone tenant-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    return keystone_id( osutils.run('keystone tenant-create --name=' + name) )

def tenant_find(name):
  tbl = table( osutils.run('keystone tenant-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  return None

def user_create(name, pwd, email, tenantId=None):
  tbl = table( osutils.run('keystone user-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    cmd = 'keystone user-create --name=' + name + ' --pass=' + pwd + ' --email=' + email
    if tenantId != None:
      cmd = cmd + ' --tenant_id=' + tenantId
    return keystone_id( osutils.run(cmd) )

def role_create(name):
  tbl = table( osutils.run('keystone role-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    return keystone_id( osutils.run('keystone role-create --name=' + name ) )

def user_role_add(userId, roleId, tenantId):
  if openstack_conf.version == "essex":
    return osutils.run('keystone user-role-add --user=' + userId + ' --role=' + roleId + ' --tenant_id=' + tenantId )
  else:
    return osutils.run('keystone user-role-add --user-id=' + userId + ' --role-id=' + roleId + ' --tenant_id=' + tenantId )

def service_create(name, type, desc):
  tbl = table( osutils.run('keystone service-list') )
  r = row(tbl, 'name', name)
  if r != None:
    return get(tbl, 'id', r)
  else:
    return keystone_id( osutils.run("keystone service-create --name {0} --type {1} --description '{2}'".format(name, type, desc) ) )

def endpoint_create(region, id, publicurl, adminurl, internalurl):
  tbl = table( osutils.run('keystone endpoint-list') )
  r = row(tbl, 'internalurl', internalurl)
  if r == None:
    if openstack_conf.version == "essex":
      osutils.run_std( "keystone endpoint-create --region {0} --service_id {1} --publicurl '{2}' --adminurl '{3}' --internalurl '{4}'".format(region, id, publicurl, adminurl, internalurl) )
    else:
      osutils.run_std( "keystone endpoint-create --region {0} --service-id {1} --publicurl '{2}' --adminurl '{3}' --internalurl '{4}'".format(region, id, publicurl, adminurl, internalurl) )

