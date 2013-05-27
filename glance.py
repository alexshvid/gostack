#!/usr/bin/python

import patcher
import openstack_conf
import openstack_pass
import time
import osutils

osutils.beroot()

#Create database for Glance
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE glance;'""")
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e "GRANT ALL ON glance.* TO 'glance'@'%' IDENTIFIED BY '"""+openstack_pass.glance_db_pass+"""';" """)
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e "GRANT ALL ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '"""+openstack_pass.glance_db_pass+"""';" """)
osutils.run_std('mysql -u root -p'+openstack_pass.root_db_pass+""" -e "GRANT ALL ON glance.* TO 'glance'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.glance_db_pass+"""';" """)

osutils.run_std('apt-get install -y glance glance-api glance-client glance-common glance-registry python-glance')

props = {}
props['rabbit_password'] = ('guest', openstack_pass.rabbit_pass)
props['[paste_deploy]flavor'] = (None, 'keystone')
p = patcher.patch_file('/etc/glance/glance-api.conf', props, True)
print('info: /etc/glance/glance-api.conf patched ' + str(p))

props = {}
props['sql_connection'] = ('sqlite:////var/lib/glance/glance.sqlite', "mysql://glance:"+openstack_pass.glance_db_pass+"@"+openstack_pass.pubhost+"/glance")
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

# Sync Glance with MySQL
osutils.run_std("glance-manage db_sync")
time.sleep(2)

# Restart Glance
osutils.run_std("service glance-api restart && service glance-registry restart")
time.sleep(2)

#Download Ubuntu Precise 12.04
if not os.path.isfile("precise-server-cloudimg-amd64-disk1.img"):
  osutils.run_std("wget https://cloud-images.ubuntu.com/precise/current/precise-server-cloudimg-amd64-disk1.img")

#Import Ubuntu Cloud 12.04 to Glance
osutils.run_std("glance add name=Ubuntu-12.04 is_public=true container_format=ovf disk_format=qcow2 < precise-server-cloudimg-amd64-disk1.img")




