#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_conf

if os.geteuid() != 0:
  exit("Login as a root")

if openstack_conf.version in ["folsom", "grizzly"]:

  packages_str = 'apt-get -y install ubuntu-cloud-keyring python-software-properties software-properties-common python-keyring'
  sources_list = 'echo deb http://ubuntu-cloud.archive.canonical.com/ubuntu precise-updates/' + openstack_conf.version + ' main >> /etc/apt/sources.list.d/openstack.list'

  apt_install = subprocess.Popen(packages_str, shell=True, stdin=None, executable="/bin/bash")
  apt_install.wait()

  apt_sources = subprocess.Popen(sources_list, shell=True, stdin=None, executable="/bin/bash")
  apt_sources.wait()

apt_update = subprocess.Popen('apt-get update', shell=True, stdin=None, executable="/bin/bash")
apt_update.wait()

apt_upgrade = subprocess.Popen('apt-get -y upgrade', shell=True, stdin=None, executable="/bin/bash")
apt_upgrade.wait()

apt_dist_upgrade = subprocess.Popen('apt-get -y dist-upgrade', shell=True, stdin=None, executable="/bin/bash")
apt_dist_upgrade.wait()

