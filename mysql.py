#!/usr/bin/python

import os.path
import openstack_pass
import patcher
import osutils

osutils.beroot()

def install_mysql():
  osutils.run_std('export DEBIAN_FRONTEND=noninteractive && apt-get install -q -y mysql-server')

def setup_root_pass():
  if os.system('mysqladmin -u root status') == 0:
    osutils.run_std('mysqladmin -u root password ' + openstack_pass.root_db_pass)

def install_python_mysql():
  osutils.run_std('apt-get install -y python-mysqldb')

install_mysql()

while not os.path.exists('/etc/mysql/my.cnf'):
  print('warn: file /etc/mysql/my.cnf not found, reinstalling mysql')
  install_mysql()

setup_root_pass()
install_python_mysql()

props = {}
props['bind-address'] = ('127.0.0.1', '0.0.0.0')
p = patcher.patch_file("/etc/mysql/my.cnf", props, True)
print("info: my.cnf patched " + str(p))

#Restart MySQL
osutils.run_std('service mysql restart')



