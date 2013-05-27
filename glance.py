#!/usr/bin/python

import os
import subprocess
import patcher
import openstack_conf
import openstack_pass
import time

if os.geteuid() != 0:
  exit("Login as a root")

#Create database for Glance
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE glance;'""")
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON glance.* TO 'glance'@'%' IDENTIFIED BY '"""+openstack_pass.glance_db_pass+"""';" """)
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '"""+openstack_pass.glance_db_pass+"""';" """)
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON glance.* TO 'glance'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.glance_db_pass+"""';" """)

installer = subprocess.Popen('apt-get install -y glance glance-api glance-client glance-common glance-registry python-glance', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

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
manageRun = subprocess.Popen("glance-manage version_control 0", shell=True, stdin=None, executable="/bin/bash")
manageRun.wait()
print(manageRun)
time.sleep(2)

# Sync Glance with MySQL
glanceSync = subprocess.Popen("glance-manage db_sync", shell=True, stdin=None, executable="/bin/bash")
glanceSync.wait()
print(glanceSync)
time.sleep(2)

# Restart Glance
restartGlance =  subprocess.Popen("service glance-api restart && service glance-registry restart", shell=True, stdin=None, executable="/bin/bash")
restartGlance.wait()
print(restartGlance)
time.sleep(2)

#Download Ubuntu Precise 12.04
if not os.path.isfile("precise-server-cloudimg-amd64-disk1.img"):
  downloading = subprocess.Popen("wget https://cloud-images.ubuntu.com/precise/current/precise-server-cloudimg-amd64-disk1.img", shell=True, stdin=None, executable="/bin/bash")
  downloading.wait()

#Import Ubuntu Cloud 12.04 to Glance
importUb = subprocess.Popen("glance add name=Ubuntu-12.04 is_public=true container_format=ovf disk_format=qcow2 < precise-server-cloudimg-amd64-disk1.img",shell=True)
importUb.wait()




