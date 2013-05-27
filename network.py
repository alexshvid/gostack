#!/usr/bin/python

import os
import subprocess
import patcher
import openstack_conf

if os.geteuid() != 0:
  exit("Login as a root")

props={}
props["net.ipv4.ip_forward"] = ("0", "1")
props["net.ipv4.conf.all.rp_filter"] = (None, "0")
props["net.ipv4.conf.default.rp_filter"] = (None, "0")

p = patcher.patch_file("/etc/sysctl.conf", props)
print("info: /etc/sysctl.conf patched " + str(p))

apply = subprocess.Popen('sysctl net.ipv4.ip_forward=1', shell=True, stdin=None, executable="/bin/bash")
apply.wait()


if openstack_conf.version == "essex":
  installer = subprocess.Popen('apt-get install -y nova-network', shell=True, stdin=None, executable="/bin/bash")
  installer.wait()


# Append eth1 to /etc/network/interface
#
# auto eth1
# iface eth1 inet manual
#        up ifconfig $IFACE 0.0.0.0 up
#        up ifconfig $IFACE promisc
#
# Restart network
# restarter = subprocess.Popen('service networking restart', shell=True, stdin=None, executable="/bin/bash")
# restarter.wait()


