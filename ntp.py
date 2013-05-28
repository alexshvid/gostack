#!/usr/bin/python

import osutils

def main():

  osutils.run_std('apt-get install -y ntp')

  first_str = """server ntp.ubuntu.com iburst
server 127.127.1.0
fudge 127.127.1.0 stratum 10
"""

  with open('/etc/ntp.conf','r') as f:
    ntp_conf = f.read()

  if not ntp_conf.startswith(first_str):

    with open('/etc/ntp.conf', 'w') as f:
      f.write(first_str + ntp_conf)

    print("info: added servers to ntp.conf")

    # Restart network and ntp services
    osutils.run_std('service ntp restart')

if __name__ == '__main__':
  osutils.beroot()
  main()
