#!/bin/bash
  apt-get purge -y nova-network libvirt-bin  nova-objectstore nova-api nova-cert nova-common nova-compute nova-compute-kvm nova-scheduler nova-vncproxy nova-volume
   apt-get autoremove -y
   rm -rf /var/lib/nova/
 rm -rf /etc/nova/
   rm -rf /var/lib/libvirt/
   rm -rf /var/log/nova/
   apt-get purge -y glance glance-api glance-client glance-common glance-registry python-glance
apt-get purge -y rabbitmq-server bridge-utils
  apt-get autoremove -y
sudo apt-get -y install dnsmasq
apt-get autoremove -y
   rm -rf /var/lib/glance/images
apt-get purge -y python-novaclient
 apt-get auto remove -y
 rm -rf /etc/glance/
   rm -rf /var/lib/glance/images
   apt-get purge -y keystone python-keystone python-keystoneclient
 apt-get auto remove -y
rm -rf /var/lib/keystone
rm -rf /etc/keystone
  apt-get auto remove -y
apt-get purge -y mysql-common mysql-server mysql-server-core-5.5
 apt-get auto remove -y
apt-get purge -y mysql-client-core-5.5
 apt-get auto remove -y
rmmod bridge
rm  -rf /var/lib/glance/
  apt-get purge -y mysql-server python-mysqldb mysql-client 
   apt-get auto remove -y
   rm -rf /etc/mysql/
   rm -rf /var/lib/mysql
killall dnsmasq
apt-get purge -y libvirt-bin
apt-get autoremove -y
rm -rf /etc/libvirt/
rm -rf /var/lib/libvirt/
rm -rf /var/log/libvirt/
apt-get purge -y tgt open-iscsi open-iscsi-utils rabbitmq-server memcached python-memcache kvm libvirt-bin 
apt-get autoremove -y
/etc/init.d/networking restart
apt-get purge -y openvswitch-datapath-dkms