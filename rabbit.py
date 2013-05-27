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


rcpf = open("rabbit-change-pass.sh","w")
rcpf.write( '#!/bin/sh\n\n' )
rcpf.write( 'rabbitmqctl change_password guest ' + openstack_pass.rabbit_pass + '\n' )
rcpf.close()

os.system('chmod +x rabbit-change-pass.sh')
os.system('./rabbit-change-pass.sh')

#change_pass = subprocess.Popen(['rabbitmqctl', 'change_password', 'guest', openstack_pass.rabbit_pass], stdin=None)
#change_pass.wait()

restarter = subprocess.Popen('service rabbitmq-server restart', shell=True, stdin=None, executable="/bin/bash")
restarter.wait()
