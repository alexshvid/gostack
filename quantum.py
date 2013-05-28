#!/usr/bin/python

import os
import subprocess
import patcher
import openstack_conf
import osutils

osutils.beroot()

#if openstack_conf.version == "essex":
osutils.run_std('apt-get install -y nova-network')

