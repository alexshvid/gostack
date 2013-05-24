#!/usr/bin/python

import re
import os
import shutil
import subprocess

if os.geteuid() != 0:
  exit("Login as a root")

install_ntp = subprocess.Popen('apt-get install -y ntp', shell=True, stdin=None, executable="/bin/bash")
install_ntp.wait()

first_str = 'server ntp.ubuntu.com iburst\nserver 127.127.1.0\nfudge 127.127.1.0 stratum 10\n'

ntpf = open('/etc/ntp.conf','r')
ntp_conf = ntpf.read()
ntpf.close()

if not ntp_conf.startswith(first_str):

  ntpf = open('/etc/ntp.conf', 'w')
  ntpf.write(first_str + ntp_conf)
  ntpf.close()

  print("info: added servers to ntp.conf")

  #Restart network and ntp services
  restart_ntp = subprocess.Popen('service ntp restart', shell=True, stdin=None, executable="/bin/bash")
  restart_ntp.wait()

