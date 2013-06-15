#!/usr/bin/python

import os
import openstack_conf
import osutils

osutils.beroot()

if not openstack_conf.use_quantum:
  hasNetwork = False
  if openstack_conf.version == 'essex':
    hasNetwork = os.system('nova-manage network list') == 0
    print('info: exception is ok')
  else:
    out = osutils.run('nova-manage network list')
    cidr = openstack_conf.fixed_range.split('/')[0]
    print("cidr = " + cidr)
    hasNetwork = cidr in out

  if not hasNetwork:
    print('info: network create %s on %s' % (openstack_conf.fixed_range, openstack_conf.fixed_int) )
    osutils.run_std('nova-manage network create private --fixed_range_v4=%s --num_networks=1 --bridge=br100 --bridge_interface=%s --network_size=250 --multi_host=T' % (openstack_conf.fixed_range, openstack_conf.fixed_int) )

  floatingOut = osutils.run('nova-manage floating list')

  if floatingOut.find('No floating') >= 0:
    print("info: floating create " + openstack_conf.floating_range)
    osutils.run_std('nova-manage floating create --ip_range=%s' % (openstack_conf.floating_range) )
