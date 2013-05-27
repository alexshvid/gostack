#!/usr/bin/python

import os
import subprocess
import openstack_pass
import time
from amqplib import client_0_8 as amqp

if os.geteuid() != 0:
  exit("Login as a root")

while 1:

  change_pass = subprocess.Popen(['rabbitmqctl', 'change_password', 'guest', openstack_pass.rabbit_pass], stdin=None)
  change_pass.wait()

  try:
    conn = amqp.Connection(host='localhost:5672', userid='guest', password=openstack_pass.rabbit_pass, virtual_host="/", insist=False)
    print(conn)

    chan = conn.channel()
    print(chan)

    break

  except:
    print("Wrong password... reconnect.")
    time.sleep(2)

