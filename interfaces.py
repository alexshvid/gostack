#!/usr/bin/python

import patcher
import osutils

osutils.beroot()

osutils.run_std('apt-get install -y bridge-utils vlan')

props={}
props["net.ipv4.ip_forward"] = ("0", "1")
props["net.ipv4.conf.all.rp_filter"] = (None, "0")
props["net.ipv4.conf.default.rp_filter"] = (None, "0")

p = patcher.patch_file("/etc/sysctl.conf", props)
print("info: /etc/sysctl.conf patched " + str(p))

osutils.run_std('sysctl net.ipv4.ip_forward=1')

# Append eth1 to /etc/network/interface
#
# auto eth1
# iface eth1 inet manual
#        up ifconfig $IFACE 0.0.0.0 up
#        up ifconfig $IFACE promisc
#
# Restart network
# osutils.run_std('service networking restart')


