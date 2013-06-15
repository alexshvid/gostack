gostack
=======

Installation Scripts for OpenStack (Ubuntu 12.4)

How to Install Essex/Folsom/Grizzly to Ubuntu 12.4 in 5 minutes

1. In VirtualBox create two Host-Only Ethernet adapters
192.168.100.0/24  vboxif1      # Public network
10.10.10.0/24     vboxif2      # Private network

for quantum add
192.168.101.0/24  vboxif3      # Management network

2. In new VM setup networks
eth0 = vboxif1
eth1 = vboxif2
eth2 = NAT

for quantum add
eth3 = vboxif3

Split HDD to
1Gb, /boot, ext2, primary, bootable
2Gb, swap, logical
2Gb, LVM, logical
7Gb, /, ext4, logical

Total 12Gb

3. Start VM and add interfaces to /etc/network/interfaces

sudo nano /etc/network/interfaces

for non quantum add

  # Public network
  auto eth0
  iface eth0 inet static
     address  192.168.100.77
     netmask  255.255.255.0

  # Private network
  auto eth1
  iface eth1 inet manual

for quantum add

  # Public network
  auto eth0
  iface eth0 inet manual
  
  # Private network
  auto eth1
  iface eth1 inet manual
  
  # Management network
  auto eth3
  iface eth3 inet static
     address  192.168.101.77
     netmask  255.255.255.0

sudo service networking restart

4. Change /etc/hosts file

sudo nano /etc/hosts

for non quantum

192.168.100.77  your_host_name

for quantum

192.168.101.77  your_host_name

5. Checkout this project
sudo apt-get install git
git clone git://github.com/shvid/gostack.git
cd gostack

6. Change configuration/settings if need

nano openstack_conf.py

a) change my_ip/controller_ip for controller or compute
b) change version of the openstack
c) change apt_update to True for non-updated system
d) for quantum change my_ip/controller_ip to subnet of eth3, for example 192.168.101.77

./aptupdate.py - if needed

7. Generate passwords
./genpass.py
sudo bash
source creds

8. Install OpenStack
./install.py

9. Copy openstack_pass.py and creds to the Compute node,
change my_ip in openstack_conf.py and run installer

Done.