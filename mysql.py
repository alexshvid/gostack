#!/usr/bin/python

import re
import os
import os.path
import shutil
import subprocess
import time
import openstack_pass
import patcher

if os.geteuid() != 0:
  exit("Login as a root")

def install_mysql():
  apt_install = subprocess.Popen('export DEBIAN_FRONTEND=noninteractive && apt-get install -q -y mysql-server', shell=True, stdin=None, executable="/bin/bash")
  apt_install.wait()

def setup_root_pass():
  if os.system('mysqladmin -u root status') == 0:
    setup_pass = subprocess.Popen('mysqladmin -u root password ' + openstack_pass.root_db_pass, shell=True, stdin=None, executable="/bin/bash")
    setup_pass.wait()

def install_python_mysql():
  apt_install = subprocess.Popen('apt-get install -y python-mysqldb', shell=True, stdin=None, executable="/bin/bash")
  apt_install.wait()

install_mysql()

if not os.path.exists('/etc/mysql/my.cnf'):
  print('warn: file /etc/mysql/my.cnf not found, reinstalling mysql')
  install_mysql()

if not os.path.exists('/etc/mysql/my.cnf'):
  exit('error: file /etc/mysql/my.cnf not found, something wrong')

setup_root_pass()
install_python_mysql()

props = {}
props['bind-address'] = ('127.0.0.1', '0.0.0.0')
p = patcher.patch_file("/etc/mysql/my.cnf", props, True)
print("info: my.cnf patched " + str(p))

#Restart MySQL
restarter = subprocess.Popen('service mysql restart', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()



