#!/usr/bin/python

import os
import os.path
import random
import string
import socket
import openstack_conf

if os.path.exists('openstack_pass.py'):
  exit('warn: openstack_pass.py already exists')

def generate_pass(pass_length=64):
    if hasattr(random, 'SystemRandom'):
        choice = random.SystemRandom().choice
    else:
        choice = random.choice
    return ''.join(map(lambda x: choice(string.digits + string.letters),
                   range(pass_length)))

pubhost=socket.gethostname()
admin_token=generate_pass(20)
keystone_db_pass=generate_pass(16)
glance_db_pass=generate_pass(16)
nova_db_pass=generate_pass(16)
rabbit_pass=generate_pass(16)

pf = open('openstack_pass.py', 'w')
pf.write("#!/usr/bin/python\n\n")
pf.write("pubhost='" + pubhost + "'\n")
pf.write("admin_token='" + admin_token + "'\n")
pf.write("keystone_db_pass='" + keystone_db_pass + "'\n")
pf.write("glance_db_pass='" + glance_db_pass + "'\n")
pf.write("nova_db_pass='" + nova_db_pass + "'\n")
pf.write("root_db_pass='" + openstack_conf.root_db_pass + "'\n")
pf.write("openstack_pass='" + openstack_conf.openstack_pass + "'\n")
pf.write("rabbit_pass='" + rabbit_pass + "'\n")
pf.close()

credsf = open('creds', 'w')
credsf.write("""
export OS_PASSWORD=""" + openstack_conf.openstack_pass + """
export SERVICE_TOKEN=""" + admin_token + """
export OS_TENANT_NAME=admin
export OS_USERNAME=admin
export SERVICE_ENDPOINT="http://""" + pubhost + """:35357/v2.0"
export OS_AUTH_URL="http://""" + pubhost + """:5000/v2.0/"
""")
credsf.close()

os.system('chmod +x creds')

print("info: passwords are generated, run 'source creds' in your shell")


