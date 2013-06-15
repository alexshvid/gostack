#!/usr/bin/python

import patcher
import openstack_conf
import openstack_pass
import time
import osutils
import os

osutils.beroot()

#Create database for Glance
osutils.run_std("mysql -u root -p%s -e 'CREATE DATABASE glance;'" % (openstack_pass.root_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON glance.* TO 'glance'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, '%', openstack_pass.glance_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON glance.* TO 'glance'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, 'localhost', openstack_pass.glance_db_pass) )
osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON glance.* TO 'glance'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, openstack_pass.controller_host, openstack_pass.glance_db_pass) )

sql = "mysql://glance:%s@%s:3306/glance" % (openstack_pass.glance_db_pass, openstack_pass.controller_host)

if openstack_conf.version == 'essex':
  osutils.run_std('apt-get install -y glance glance-api glance-client glance-common glance-registry python-glance')

  props = {}
  props['rabbit_password'] = ('guest', openstack_pass.rabbit_pass)
  props['[paste_deploy]flavor'] = (None, 'keystone')
  p = patcher.patch_file('/etc/glance/glance-api.conf', props, True)
  print('info: /etc/glance/glance-api.conf patched ' + str(p))

  props = {}
  props['sql_connection'] = ('sqlite:////var/lib/glance/glance.sqlite', sql)
  props['[paste_deploy]flavor'] = (None, 'keystone')
  p = patcher.patch_file('/etc/glance/glance-registry.conf', props, True)
  print('info: /etc/glance/glance-registry.conf patched ' + str(p))

  props = {}
  props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
  props['admin_user'] = ('%SERVICE_USER%', 'admin')
  props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)
  p = patcher.patch_file('/etc/glance/glance-registry-paste.ini', props, True)
  print('info: /etc/glance/glance-registry-paste.ini patched ' + str(p))

  props = {}
  props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
  props['admin_user'] = ('%SERVICE_USER%', 'admin')
  props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)
  p = patcher.patch_file('/etc/glance/glance-api-paste.ini', props, True)
  print('info: /etc/glance/glance-api-paste.ini patched ' + str(p))

  # Manage Glance
  osutils.run_std("glance-manage version_control 0")
  time.sleep(2)

else:
  osutils.run_std('apt-get install -y glance glance-api glance-registry python-glanceclient glance-common')

  props = {}
  props['[DEFAULT]verbose'] = (None, str(openstack_conf.verbose))
  props['[DEFAULT]debug'] = (None, str(openstack_conf.debug))

  props['sql_connection'] = ('sqlite:////var/lib/glance/glance.sqlite', sql)
  props['[paste_deploy]flavor'] = (None, 'keystone')

  props['auth_host'] = ('127.0.0.1', openstack_pass.controller_host)
  props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
  props['admin_user'] = ('%SERVICE_USER%', 'admin')
  props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)

  p = patcher.patch_file('/etc/glance/glance-registry.conf', props, True)
  print('info: /etc/glance/glance-registry.conf patched ' + str(p))

  props['notifier_strategy'] = ('noop', 'rabbit')
  props['rabbit_password'] = ('guest', openstack_pass.rabbit_pass)

  p = patcher.patch_file('/etc/glance/glance-api.conf', props, True)
  print('info: /etc/glance/glance-api.conf patched ' + str(p))


# Sync Glance with MySQL
osutils.run_std("glance-manage db_sync")
time.sleep(2)

# Restart Glance
osutils.run_std("service glance-api restart && service glance-registry restart")
time.sleep(2)

if openstack_conf.downloadImage:

  #Import Ubuntu Cloud 12.04 to Glance
  glanceIndex = osutils.run('glance index')
  if not 'Ubuntu-12.04' in glanceIndex:
      
    #Download Ubuntu Precise 12.04
    if not os.path.isfile("precise-server-cloudimg-amd64-disk1.img"):
      print('download ubuntu image')
      osutils.run_std("wget https://cloud-images.ubuntu.com/precise/current/precise-server-cloudimg-amd64-disk1.img")
      
    print('add ubuntu image')
    osutils.run_std("glance add name=Ubuntu-12.04 is_public=true container_format=ovf disk_format=qcow2 < precise-server-cloudimg-amd64-disk1.img")




