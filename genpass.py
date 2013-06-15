#!/usr/bin/python

import os.path
import random
import string
import socket

if os.path.exists('openstack_pass.py'):
  exit('warn: openstack_pass.py already exists')

def generate_pass(pass_length=64):
  if hasattr(random, 'SystemRandom'):
    choice = random.SystemRandom().choice
  else:
    choice = random.choice
  return ''.join(map(lambda x: choice(string.digits + string.letters), range(pass_length)))

controller_host=socket.gethostname()
admin_token=generate_pass(20)
rabbit_pass=generate_pass(16)
keystone_db_pass=generate_pass(16)
glance_db_pass=generate_pass(16)
nova_db_pass=generate_pass(16)
cinder_db_pass=generate_pass(16)
quantum_db_pass=generate_pass(16)
quantum_metadata_proxy_shared_secret=generate_pass(20)
root_db_pass=generate_pass(16)
openstack_pass=generate_pass(16)

with open('openstack_pass.py', 'w') as pf:
  pf.write("#!/usr/bin/python\n\n")
  pf.write("import os\n\n")
  pf.write("controller_host='" + controller_host + "'\n")
  pf.write("admin_token='" + admin_token + "'\n")
  pf.write("rabbit_pass='" + rabbit_pass + "'\n")
  pf.write("keystone_db_pass='" + keystone_db_pass + "'\n")
  pf.write("glance_db_pass='" + glance_db_pass + "'\n")
  pf.write("nova_db_pass='" + nova_db_pass + "'\n")
  pf.write("cinder_db_pass='" + cinder_db_pass + "'\n")
  pf.write("quantum_db_pass='" + quantum_db_pass + "'\n")
  pf.write("quantum_metadata_proxy_shared_secret='" + quantum_metadata_proxy_shared_secret + "'\n")
  pf.write("root_db_pass='" + root_db_pass + "'\n")
  pf.write("openstack_pass='" + openstack_pass + "'\n")
  pf.write("\n")
  pf.write("creds = ['OS_PASSWORD', 'SERVICE_TOKEN', 'OS_TENANT_NAME', 'OS_USERNAME', 'SERVICE_ENDPOINT', 'OS_AUTH_URL']\n")
  pf.write("\n")
  pf.write("def has_creds():\n")
  pf.write("  for cred in creds:\n")
  pf.write("    if not os.environ.has_key(cred):\n")
  pf.write("      return False\n")
  pf.write("  return True\n")
  pf.write("\n")

with open('creds', 'w') as f:
 f.write("""
export OS_PASSWORD=""" + openstack_pass + """
export SERVICE_TOKEN=""" + admin_token + """
export OS_TENANT_NAME=admin
export OS_USERNAME=admin
export SERVICE_ENDPOINT="http://""" + controller_host + """:35357/v2.0"
export OS_AUTH_URL="http://""" + controller_host + """:5000/v2.0/"
""")

os.system('chmod +x creds')

print("info: passwords are generated, run 'source creds' in your shell")


