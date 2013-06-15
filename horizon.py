#!/usr/bin/python

import openstack_conf
import openstack_pass
import osutils

osutils.beroot()

osutils.run_std('apt-get install -y memcached python-memcache')

osutils.run_std('apt-get install -y libapache2-mod-wsgi openstack-dashboard')

# osutils.run_std('dpkg --purge openstack-dashboard-ubuntu-theme')

osutils.run_std('service apache2 restart')


if openstack_conf.version == 'essex':
  print("Open horizon on http://%s" % (openstack_conf.controller_ip) )
else:
  print("Open horizon on http://%s/horizon" % (openstack_conf.controller_ip) )

print("username = admin")
print("password = " + openstack_pass.openstack_pass)
