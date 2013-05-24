#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_conf

if os.geteuid() != 0:
  exit("Login as a root")

installer = subprocess.Popen('apt-get install -y memcached python-memcache', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

installer = subprocess.Popen('apt-get install -y libapache2-mod-wsgi openstack-dashboard', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

restarter = subprocess.Popen('service apache2 restart', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()


