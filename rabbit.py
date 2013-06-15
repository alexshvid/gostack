#!/usr/bin/python

import time
import osutils

def main():

  osutils.run_std('apt-get install -y rabbitmq-server python-amqplib')

  osutils.run_std('service rabbitmq-server restart')
  time.sleep(2)

  osutils.run_std('./rabbitpwd.py')

if __name__ == '__main__':
  osutils.beroot()
  main()
