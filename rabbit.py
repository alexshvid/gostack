#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_pass
import time
import osutils

if os.geteuid() != 0:
  exit("Login as a root")

osutils.run_std('apt-get install -y rabbitmq-server python-amqplib')

osutils.run_std('service rabbitmq-server restart')

osutils.run_std('./rabbit-pwd.py')

