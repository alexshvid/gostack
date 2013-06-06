#!/usr/bin/python

import re
import os
import shutil
import subprocess
import osutils
import openstack_conf
import openstack_pass
import patcher

osutils.beroot()

#
#  Searches first LVM disk
#

def get_lvm_disk():
  # Fdisk list
  out = osutils.run('fdisk -l')

  lvm_disk = None

  for line in out.split("\n"):
    part = re.split('\s+', line)
    if len(part) > 1 and 'Linux LVM' in line:
      lvm_disk = part[0]

  return lvm_disk

#
#  Creates LVM group on first LVM disk
#

def vg_create(vgname):

  osutils.run_std('apt-get install -y lvm2')

  out = osutils.run('vgscan')
  print(out)

  if not vgname in out:

    lvm_disk = get_lvm_disk()
    if lvm_disk != None:
      print('info: add vg ' + vgname + ' to lvm disk ' + lvm_disk)
      out = osutils.run('vgcreate ' + vgname + ' ' + lvm_disk)
      print(out)


if openstack_conf.version == 'essex':
  if openstack_conf.vgcreate:
    vg_create('nova-volumes')
  osutils.run_std('apt-get install -y nova-volume')
else:
  if openstack_conf.vgcreate:
    vg_create('cinder-volumes')
  osutils.run_std('apt-get install -y cinder-api cinder-scheduler cinder-volume iscsitarget iscsitarget-dkms')

  # Create database for Cinder
  osutils.run_std("mysql -u root -p%s -e 'CREATE DATABASE cinder;'" % (openstack_pass.root_db_pass) )
  osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON cinder.* TO 'cinder'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, '%', openstack_pass.cinder_db_pass) )
  osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON cinder.* TO 'cinder'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, 'localhost', openstack_pass.cinder_db_pass) )
  osutils.run_std("mysql -u root -p%s -e \"GRANT ALL ON cinder.* TO 'cinder'@'%s' IDENTIFIED BY '%s';\"" % (openstack_pass.root_db_pass, openstack_pass.pubhost, openstack_pass.cinder_db_pass) )

  # Patch confs
  props = {}
  props['service_host'] = ('127.0.0.1', openstack_pass.pubhost)
  props['auth_host'] = ('127.0.0.1', openstack_pass.pubhost)
  props['admin_tenant_name'] = ('%SERVICE_TENANT_NAME%', 'admin')
  props['admin_user'] = ('%SERVICE_USER%', 'admin')
  props['admin_password'] = ('%SERVICE_PASSWORD%', openstack_pass.openstack_pass)
  p = patcher.patch_file('/etc/cinder/api-paste.ini', props, True)
  print('info: /etc/cinder/api-paste.ini patched ' + str(p))

  sql = "mysql://cinder:%s@%s:3306/cinder" % (openstack_pass.cinder_db_pass, openstack_pass.pubhost)

  props = {}
  props['sql_connection'] = (None, sql)
  props['auth_strategy'] = (None, 'keystone')
  props['verbose'] = (None, openstack_conf.verbose)
  props['debug'] = (None, openstack_conf.debug)
  props['iscsi_helper'] = (None, 'tgtadm')
  props['state_path'] = (None, '/var/lib/cinder')
  props['volumes_dir'] = (None, '/var/lib/cinder/volumes')

  props['rabbit_host'] = (None, openstack_pass.pubhost)
  props['rabbit_port'] = (None, 5672)
  props['rabbit_userid'] = (None, 'guest')
  props['rabbit_password'] = (None, openstack_pass.rabbit_pass)

  p = patcher.patch_file('/etc/cinder/cinder.conf', props, True)
  print('info: /etc/cinder/cinder.conf patched ' + str(p))

  # DB Sync
  osutils.run_std('cinder-manage db sync')

  # Restart services
  osutils.run_std('cd /etc/init.d/; for i in $( ls cinder-* ); do sudo service $i restart; done')


