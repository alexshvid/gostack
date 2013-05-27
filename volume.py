#!/usr/bin/python

import re
import os
import shutil
import subprocess

if os.geteuid() != 0:
  exit("Login as a root")

vgname = 'nova-volumes'

def run_cmd(cmd):
  p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=subprocess.PIPE, executable="/bin/bash")
  p.wait()
  out, err = p.communicate()
  if err != None:
    print('error: fail run command ' + cmd + ', error code = ' + str(err))
  return out

installer = subprocess.Popen('apt-get install -y lvm2', shell=True, stdin=None, executable="/bin/bash")
installer.wait()

out = run_cmd('vgscan')
print(out)

if not vgname in out:

  # Fdisk list
  out = run_cmd('fdisk -l')

  lvm_disk = None

  for line in out.split("\n"):
    part = re.split('\s+', line)
    if len(part) > 1 and 'Linux LVM' in line:
      lvm_disk = part[0]

  if lvm_disk != None:
    print('info: add vg ' + vgname + ' to lvm disk ' + lvm_disk)
    out = run_cmd('vgcreate ' + vgname + ' ' + lvm_disk)
    print(out)


installer = subprocess.Popen('apt-get install -y nova-volume', shell=True, stdin=None, executable="/bin/bash")
installer.wait()


