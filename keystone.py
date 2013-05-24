#!/usr/bin/python

import os
import subprocess
import openstack_conf
import openstack_pass
import patcher

if os.geteuid() != 0:
  exit("Login as a root")

os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e 'CREATE DATABASE keystone;'""")
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)
os.system("""mysql -u root -p"""+openstack_pass.root_db_pass+""" -e "GRANT ALL ON keystone.* TO 'keystone'@'""" + openstack_pass.pubhost + """' IDENTIFIED BY '"""+openstack_pass.keystone_db_pass+"""';" """)

installer = subprocess.Popen('apt-get install -y keystone python-keystone python-keystoneclient', shell=True, stdin=None, stderr=None, executable="/bin/bash")
installer.wait()

props = {}
props['[DEFAULT]bind_host'] = (None, '0.0.0.0')
props['[DEFAULT]admin_token'] = ('ADMIN', openstack_pass.admin_token)
props['[sql]connection'] = ('sqlite:////var/lib/keystone/keystone.db', "mysql://keystone:"+openstack_pass.keystone_db_pass+"@"+openstack_pass.pubhost+":3306/keystone")
props['[catalog]driver'] = ('keystone.catalog.backends.sql.Catalog', 'keystone.catalog.backends.templated.TemplatedCatalog')
props['[catalog]template_file'] = (None, '/etc/keystone/default_catalog.templates')

p = patcher.patch_file('/etc/keystone/keystone.conf', props, True)
print("info: /etc/keystone/keystone.conf patched " + str(p))

# Restart keystone
os.system("service keystone restart")

# Sync keystone with MySQL
keystoneSync = subprocess.Popen('keystone-manage db_sync', shell=True, stdin=None, executable="/bin/bash")
keystoneSync.wait()

# Keystone user-list
keystoneList = subprocess.Popen('keystone user-list', shell=True, stdin=None, stdout=subprocess.PIPE, executable="/bin/bash")
keystoneList.wait()
userList, err = keystoneList.communicate()
print(userList)

if userList.find(openstack_conf.myemail) >= 0:
  exit("info: keystone has user " + openstack_conf.myemail)

#Add Keystone user roles devstack functions

keystoneInitScript="""ADMIN_PASSWORD=${ADMIN_PASSWORD:-"""+openstack_pass.openstack_pass+"""}
SERVICE_PASSWORD=${SERVICE_PASSWORD:-$ADMIN_PASSWORD}
export SERVICE_ENDPOINT="http://""" + openstack_pass.pubhost + """:35357/v2.0"
SERVICE_TENANT_NAME=${SERVICE_TENANT_NAME:-service}
#This function pulls IDs from command outputs
function get_id () {
    echo `$@ | awk '/ id / { print $4 }'`
}

# Tenants
ADMIN_TENANT=$(get_id keystone tenant-create --name=admin)
SERVICE_TENANT=$(get_id keystone tenant-create --name=$SERVICE_TENANT_NAME)
MY_TENANT=$(get_id keystone tenant-create --name=""" + openstack_conf.myproject + """)

# Users
ADMIN_USER=$(get_id keystone user-create --name=admin --pass="$ADMIN_PASSWORD" --email=""" + openstack_conf.myemail + """)
MY_USER=$(get_id keystone user-create --name=""" + openstack_conf.myproject + """ --pass="$ADMIN_PASSWORD" --email=""" + openstack_conf.myemail + """)

# Roles
ADMIN_ROLE=$(get_id keystone role-create --name=admin)
KEYSTONEADMIN_ROLE=$(get_id keystone role-create --name=KeystoneAdmin)
KEYSTONESERVICE_ROLE=$(get_id keystone role-create --name=KeystoneServiceAdmin)

# Add Roles to Users in Tenants
keystone user-role-add --user $ADMIN_USER --role $ADMIN_ROLE --tenant_id $ADMIN_TENANT
keystone user-role-add --user $ADMIN_USER --role $ADMIN_ROLE --tenant_id $MY_TENANT

keystone user-role-add --user $ADMIN_USER --role $KEYSTONEADMIN_ROLE --tenant_id $ADMIN_TENANT
keystone user-role-add --user $ADMIN_USER --role $KEYSTONESERVICE_ROLE --tenant_id $ADMIN_TENANT

# The Member role is used by Horizon and Swift so we need to keep it:
MEMBER_ROLE=$(get_id keystone role-create --name=Member)
keystone user-role-add --user $MY_USER --role $MEMBER_ROLE --tenant_id $MY_TENANT

# Configure service users/roles
NOVA_USER=$(get_id keystone user-create --name=nova --pass="$SERVICE_PASSWORD" --tenant_id $SERVICE_TENANT --email=""" + openstack_conf.myemail + """)
keystone user-role-add --tenant_id $SERVICE_TENANT --user $NOVA_USER --role $ADMIN_ROLE

GLANCE_USER=$(get_id keystone user-create --name=glance --pass="$SERVICE_PASSWORD" --tenant_id $SERVICE_TENANT --email=""" + openstack_conf.myemail + """)
keystone user-role-add --tenant_id $SERVICE_TENANT --user $GLANCE_USER --role $ADMIN_ROLE

QUANTUM_USER=$(get_id keystone user-create --name=quantum --pass="$SERVICE_PASSWORD" --tenant_id $SERVICE_TENANT --email=""" + openstack_conf.myemail + """)
keystone user-role-add --tenant_id $SERVICE_TENANT --user $QUANTUM_USER --role $ADMIN_ROLE"""

keystoneScript = subprocess.Popen(keystoneInitScript, shell=True, stdin=None, executable="/bin/bash")
keystoneScript.wait()



