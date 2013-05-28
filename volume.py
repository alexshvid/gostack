#!/usr/bin/python

import re
import os
import shutil
import subprocess
import osutils

osutils.beroot()

vgname = 'nova-volumes'

osutils.run_std('apt-get install -y lvm2')

out = osutils.run('vgscan')
print(out)

if not vgname in out:

  # Fdisk list
  out = osutils.run('fdisk -l')

  lvm_disk = None

  for line in out.split("\n"):
    part = re.split('\s+', line)
    if len(part) > 1 and 'Linux LVM' in line:
      lvm_disk = part[0]

  if lvm_disk != None:
    print('info: add vg ' + vgname + ' to lvm disk ' + lvm_disk)
    out = osutils.run('vgcreate ' + vgname + ' ' + lvm_disk)
    print(out)

osutils.run_std('apt-get install -y nova-volume')


