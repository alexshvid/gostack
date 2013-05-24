#!/usr/bin/python

import re
import os
import shutil
import subprocess

if os.geteuid() != 0:
  exit("Login as a root")

installer = subprocess.Popen('apt-get install -y nova-volume', shell=True, stdin=None, executable="/bin/bash")
installer.wait()


