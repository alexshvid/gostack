#!/usr/bin/python

import re
import os
import shutil
import subprocess
import openstack_pass
import time
import osutils

def main():

  osutils.run_std('apt-get install -y rabbitmq-server python-amqplib')

  osutils.run_std('service rabbitmq-server restart')
  time.sleep(2)

  osutils.run_std('./rabbit-pwd.py')

if __name__ == '__main__':
  osutils.beroot()
  main()
