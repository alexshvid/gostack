#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_pass

if os.geteuid() != 0:
  exit("Login as a root")

installer = subprocess.Popen('apt-get install -y rabbitmq-server', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

change_pass = subprocess.Popen('rabbitmqctl change_password guest \'' + openstack_pass.rabbit_pass + '\'', shell=True, stdin=None, executable="/bin/bash")
change_pass.wait()

restarter = subprocess.Popen('service rabbitmq-server restart', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()
