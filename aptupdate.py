#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_conf
import osutils

osutils.beroot()

if openstack_conf.version in ["folsom", "grizzly"]:

  if not os.path.exists('/etc/apt/sources.list.d/openstack.list'):

    packages_str = 'apt-get -y install ubuntu-cloud-keyring python-software-properties software-properties-common python-keyring'
    sources_list = 'echo deb http://ubuntu-cloud.archive.canonical.com/ubuntu precise-updates/' + openstack_conf.version + ' main >> /etc/apt/sources.list.d/openstack.list'

    osutils.run_std(packages_str)
    osutils.run_std(sources_list)

osutils.run_std('apt-get update')
osutils.run_std('apt-get -y upgrade')
osutils.run_std('apt-get -y dist-upgrade')

